"""No-execution quarantine intake for untrusted community skill bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tarfile
import tempfile
import unicodedata
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, BinaryIO, Dict, List, Optional, Sequence, Tuple

from .security import EXECUTABLE_SUFFIXES, TEXT_SUFFIXES, scan_target
from .security_policy import SecurityPolicyError, canonical_digest


INTAKE_NAME = "hpc-skill-community-intake"
INTAKE_VERSION = "0.1.0"
SCHEMA_URL = (
    "https://hpc-skill-hub.org/schemas/community-skill-intake-report.schema.json"
)
ARCHIVE_SUFFIXES = (
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".tar.bz2",
    ".tbz2",
    ".tar.xz",
    ".txz",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".rar",
)
RESERVED_PARTS = {".git", ".hg", ".svn", "__pycache__", "build", "dist"}
WINDOWS_RESERVED_NAMES = {
    "aux",
    "con",
    "nul",
    "prn",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}
CHUNK_BYTES = 64 * 1024


@dataclass(frozen=True)
class IntakeLimits:
    max_archive_bytes: int = 5_000_000
    max_entries: int = 512
    max_files: int = 256
    max_file_bytes: int = 1_000_000
    max_total_bytes: int = 5_000_000
    max_compression_ratio: int = 100
    max_path_depth: int = 12
    max_path_bytes: int = 240


DEFAULT_LIMITS = IntakeLimits()


class IntakeError(ValueError):
    """Raised when intake cannot produce a bounded report."""


def _validate_limits(limits: IntakeLimits) -> None:
    invalid = [name for name, value in asdict(limits).items() if value < 1]
    if invalid:
        raise IntakeError(f"intake limits must be positive: {', '.join(invalid)}")


def _safe_path_display(path: str) -> str:
    rendered = []
    for character in path or ".":
        category = unicodedata.category(character)
        if category in {"Cc", "Cf", "Cs"}:
            rendered.append(f"\\u{ord(character):04x}")
        else:
            rendered.append(character)
    return "".join(rendered)


def _finding(
    finding_id: str,
    path: str,
    message: str,
    remediation: str,
) -> Dict[str, str]:
    return {
        "id": finding_id,
        "severity": "high",
        "path": _safe_path_display(path),
        "message": message,
        "remediation": remediation,
    }


def _append_finding(
    findings: List[Dict[str, str]],
    finding_id: str,
    path: str,
    message: str,
    remediation: str,
) -> None:
    key = (finding_id, _safe_path_display(path))
    if any((item["id"], item["path"]) == key for item in findings):
        return
    findings.append(_finding(finding_id, path, message, remediation))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _archive_name(path: str) -> bool:
    lowered = path.lower()
    return any(lowered.endswith(suffix) for suffix in ARCHIVE_SUFFIXES)


def _archive_magic(data: bytes) -> bool:
    return (
        data.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"))
        or data.startswith(b"\x1f\x8b")
        or data.startswith(b"BZh")
        or data.startswith(b"\xfd7zXZ\x00")
        or (len(data) > 262 and data[257:262] == b"ustar")
    )


def _executable_magic(data: bytes) -> bool:
    return data.startswith((b"\x7fELF", b"MZ")) or data[:4] in {
        b"\xca\xfe\xba\xbe",
        b"\xcf\xfa\xed\xfe",
        b"\xfe\xed\xfa\xcf",
    }


def _validate_member_path(
    raw_path: str,
    limits: IntakeLimits,
    findings: List[Dict[str, str]],
) -> Optional[str]:
    display = _safe_path_display(raw_path)
    posix = PurePosixPath(raw_path)
    windows = PureWindowsPath(raw_path)
    if (
        not raw_path
        or any(unicodedata.category(character) in {"Cc", "Cf", "Cs"} for character in raw_path)
        or "\\" in raw_path
        or posix.is_absolute()
        or windows.is_absolute()
        or bool(windows.drive)
        or ".." in posix.parts
        or ".." in windows.parts
    ):
        _append_finding(
            findings,
            "intake.path-escape",
            display,
            "A package path is absolute, ambiguous, or escapes the quarantine root.",
            "Use normalized relative POSIX paths contained by the package.",
        )
        return None

    parts = tuple(part for part in posix.parts if part not in {"", "."})
    if not parts:
        return ""
    normalized = PurePosixPath(*parts).as_posix()
    if len(parts) > limits.max_path_depth:
        _append_finding(
            findings,
            "intake.path-depth-limit",
            normalized,
            "A package path exceeds the quarantine depth limit.",
            "Flatten the package layout before review.",
        )
        return None
    try:
        normalized_bytes = normalized.encode("utf-8")
    except UnicodeEncodeError:
        _append_finding(
            findings,
            "intake.path-encoding",
            display,
            "A package path is not valid Unicode text.",
            "Rename the entry using a valid UTF-8 path.",
        )
        return None
    if len(normalized_bytes) > limits.max_path_bytes:
        _append_finding(
            findings,
            "intake.path-length-limit",
            normalized,
            "A package path exceeds the quarantine byte-length limit.",
            "Shorten package directory and file names.",
        )
        return None
    if any(part.casefold() in RESERVED_PARTS for part in parts):
        _append_finding(
            findings,
            "intake.reserved-path",
            normalized,
            "The package contains a directory excluded from normal source scanning.",
            "Remove VCS metadata, caches, build outputs, and distribution directories.",
        )
        return None
    if any(
        ":" in part
        or part.endswith((".", " "))
        or part.split(".", 1)[0].casefold() in WINDOWS_RESERVED_NAMES
        for part in parts
    ):
        _append_finding(
            findings,
            "intake.ambiguous-path",
            normalized,
            "A package path is ambiguous or reserved on a supported platform.",
            "Use portable path components without reserved names, colons, or trailing dots and spaces.",
        )
        return None
    return normalized


def _content_finding(path: str, data: bytes) -> Optional[Dict[str, str]]:
    suffix = Path(path).suffix.lower()
    if _archive_name(path) or _archive_magic(data):
        return _finding(
            "intake.nested-archive",
            path,
            "Nested archive content would create a second unreviewed extraction boundary.",
            "Expand the nested archive separately and submit readable bounded source files.",
        )
    if suffix in EXECUTABLE_SUFFIXES or _executable_magic(data):
        return _finding(
            "intake.binary-content",
            path,
            "Executable or loadable binary content is not accepted by quarantined intake.",
            "Remove the binary and reference a separately verified release artifact.",
        )
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        finding_id = (
            "intake.non-utf8-text" if suffix in TEXT_SUFFIXES else "intake.binary-content"
        )
        return _finding(
            finding_id,
            path,
            "The file is opaque binary data or is not valid UTF-8 reviewable text.",
            "Submit UTF-8 source text and keep opaque binary artifacts outside the package.",
        )
    if "\x00" in text:
        return _finding(
            "intake.binary-content",
            path,
            "The file contains NUL bytes and is not treated as reviewable text.",
            "Remove opaque binary content and submit readable UTF-8 source text.",
        )
    return None


def _record(
    path: str,
    kind: str,
    size: int,
    digest: Optional[str],
    content_type: str,
) -> Dict[str, Any]:
    return {
        "path": _safe_path_display(path),
        "type": kind,
        "bytes": size,
        "sha256": digest,
        "content_type": content_type,
    }


def _stage_data(
    data: bytes,
    relative: str,
    destination: Path,
    records: List[Dict[str, Any]],
    findings: List[Dict[str, str]],
) -> None:
    digest = hashlib.sha256(data).hexdigest()
    content_finding = _content_finding(relative, data)
    content_type = "text" if content_finding is None else "rejected"
    records.append(_record(relative, "file", len(data), digest, content_type))
    if content_finding is not None:
        findings.append(content_finding)
        return
    output = destination / PurePosixPath(relative)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)


def _limit_file(
    relative: str,
    size: int,
    file_count: int,
    total_bytes: int,
    limits: IntakeLimits,
    findings: List[Dict[str, str]],
) -> bool:
    blocked = False
    if file_count > limits.max_files:
        _append_finding(
            findings,
            "intake.file-count-limit",
            relative,
            "The package exceeds the quarantine file-count limit.",
            "Split the contribution into smaller independently reviewed packages.",
        )
        blocked = True
    if size > limits.max_file_bytes:
        _append_finding(
            findings,
            "intake.file-size-limit",
            relative,
            "A package file exceeds the quarantine per-file byte limit.",
            "Move large data or generated artifacts to a separately verified release.",
        )
        blocked = True
    if total_bytes > limits.max_total_bytes:
        _append_finding(
            findings,
            "intake.total-size-limit",
            relative,
            "The package exceeds the quarantine total uncompressed byte limit.",
            "Reduce the contribution to the source needed for one reviewable skill.",
        )
        blocked = True
    return blocked


def _register_package_path(
    relative: str,
    kind: str,
    findings: List[Dict[str, str]],
    seen: Dict[str, str],
) -> bool:
    """Register a portable path while rejecting aliases and prefix collisions."""

    key = relative.casefold()
    collision = key in seen
    parts = PurePosixPath(relative).parts
    for index in range(1, len(parts)):
        parent = PurePosixPath(*parts[:index]).as_posix().casefold()
        if seen.get(parent) == "file":
            collision = True
            break
    if kind == "file" and any(item.startswith(f"{key}/") for item in seen):
        collision = True
    if collision:
        _append_finding(
            findings,
            "intake.duplicate-path",
            relative,
            "Package entries collide after portable path normalization.",
            "Use unique case-insensitive paths without file/directory prefix aliases.",
        )
        return False
    seen[key] = kind
    return True


def _empty_stage(source_type: str) -> Dict[str, Any]:
    return {
        "source_type": source_type,
        "source_bytes": 0,
        "source_sha256": None,
        "digest_scope": "unavailable",
        "entry_count": 0,
        "file_count": 0,
        "total_bytes": 0,
        "complete": False,
        "content_digest": None,
        "files": [],
        "findings": [],
    }


def _finalize_stage(stage: Dict[str, Any]) -> Dict[str, Any]:
    records = sorted(stage["files"], key=lambda item: item["path"])
    stage["files"] = records
    digest_ready = stage["complete"] and all(item["sha256"] for item in records)
    stage["content_digest"] = canonical_digest(records) if digest_ready else None
    if stage["source_type"] == "directory":
        stage["source_sha256"] = stage["content_digest"]
        stage["digest_scope"] = "bounded-tree" if digest_ready else "unavailable"
    stage["findings"].sort(key=lambda item: (item["path"], item["id"]))
    return stage


def _stage_directory(
    source: Path,
    destination: Path,
    limits: IntakeLimits,
) -> Dict[str, Any]:
    required_dir_fd = {os.open, os.stat, os.readlink}
    if (
        os.scandir not in os.supports_fd
        or not required_dir_fd.issubset(os.supports_dir_fd)
        or not hasattr(os, "O_DIRECTORY")
        or not hasattr(os, "O_NOFOLLOW")
    ):
        raise IntakeError(
            "secure directory intake is unavailable on this platform; use a ZIP or TAR archive"
        )

    stage = _empty_stage("directory")
    stage["complete"] = True
    destination.mkdir(parents=True, exist_ok=True)
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory_flags |= getattr(os, "O_BINARY", 0)
    try:
        root_descriptor = os.open(str(source), directory_flags)
    except OSError as exc:
        raise IntakeError(f"cannot open source directory without following links: {exc}") from exc
    queue: List[Tuple[int, PurePosixPath]] = [
        (root_descriptor, PurePosixPath())
    ]
    seen: Dict[str, str] = {}

    try:
        while queue:
            current_descriptor, prefix = queue.pop(0)
            try:
                entries = sorted(
                    os.scandir(current_descriptor),
                    key=lambda item: item.name,
                )
            except OSError as exc:
                os.close(current_descriptor)
                raise IntakeError(f"cannot inventory directory {prefix or '.'}: {exc}") from exc
            try:
                for entry in entries:
                    stage["entry_count"] += 1
                    raw_relative = (prefix / entry.name).as_posix()
                    if stage["entry_count"] > limits.max_entries:
                        _append_finding(
                            stage["findings"],
                            "intake.entry-count-limit",
                            raw_relative,
                            "The package exceeds the quarantine directory-entry limit.",
                            "Remove generated trees and split the contribution into smaller packages.",
                        )
                        stage["complete"] = False
                        return _finalize_stage(stage)

                    relative = _validate_member_path(
                        raw_relative,
                        limits,
                        stage["findings"],
                    )
                    try:
                        metadata = entry.stat(follow_symlinks=False)
                    except OSError as exc:
                        raise IntakeError(
                            f"cannot inspect package entry {entry.name}: {exc}"
                        ) from exc
                    is_directory = stat.S_ISDIR(metadata.st_mode)
                    path_registered = relative is not None and _register_package_path(
                        relative,
                        "directory" if is_directory else "file",
                        stage["findings"],
                        seen,
                    )

                    if stat.S_ISLNK(metadata.st_mode):
                        target = os.readlink(
                            entry.name,
                            dir_fd=current_descriptor,
                        )
                        digest = hashlib.sha256(
                            target.encode("utf-8", errors="surrogateescape")
                        ).hexdigest()
                        stage["files"].append(
                            _record(raw_relative, "symlink", 0, digest, "rejected")
                        )
                        _append_finding(
                            stage["findings"],
                            "intake.symlink",
                            raw_relative,
                            "A symbolic link can escape or alias the reviewed package boundary.",
                            "Replace the link with a regular reviewed file inside the package.",
                        )
                        continue
                    if is_directory:
                        if not path_registered:
                            stage["complete"] = False
                            continue
                        try:
                            child_descriptor = os.open(
                                entry.name,
                                directory_flags,
                                dir_fd=current_descriptor,
                            )
                        except OSError as exc:
                            raise IntakeError(
                                f"cannot open package directory {raw_relative}: {exc}"
                            ) from exc
                        opened = os.fstat(child_descriptor)
                        if (
                            not stat.S_ISDIR(opened.st_mode)
                            or opened.st_dev != metadata.st_dev
                            or opened.st_ino != metadata.st_ino
                        ):
                            os.close(child_descriptor)
                            stage["complete"] = False
                            _append_finding(
                                stage["findings"],
                                "intake.source-changed",
                                raw_relative,
                                "A source directory changed during quarantine traversal.",
                                "Retry intake from an immutable contribution snapshot.",
                            )
                            continue
                        queue.append((child_descriptor, PurePosixPath(relative)))
                        continue
                    if not stat.S_ISREG(metadata.st_mode):
                        stage["files"].append(
                            _record(raw_relative, "special", 0, None, "rejected")
                        )
                        _append_finding(
                            stage["findings"],
                            "intake.special-file",
                            raw_relative,
                            "A device, socket, FIFO, or other special file is not reviewable source.",
                            "Remove special filesystem entries from the contribution.",
                        )
                        continue

                    stage["file_count"] += 1
                    stage["total_bytes"] += metadata.st_size
                    stage["source_bytes"] = stage["total_bytes"]
                    if _limit_file(
                        raw_relative,
                        metadata.st_size,
                        stage["file_count"],
                        stage["total_bytes"],
                        limits,
                        stage["findings"],
                    ):
                        stage["files"].append(
                            _record(
                                raw_relative,
                                "file",
                                metadata.st_size,
                                None,
                                "unread",
                            )
                        )
                        continue
                    if relative is None:
                        stage["files"].append(
                            _record(
                                raw_relative,
                                "file",
                                metadata.st_size,
                                None,
                                "rejected",
                            )
                        )
                        continue
                    if not path_registered:
                        stage["files"].append(
                            _record(
                                relative,
                                "file",
                                metadata.st_size,
                                None,
                                "rejected",
                            )
                        )
                        continue
                    if _archive_name(relative):
                        stage["files"].append(
                            _record(
                                relative,
                                "file",
                                metadata.st_size,
                                None,
                                "rejected",
                            )
                        )
                        _append_finding(
                            stage["findings"],
                            "intake.nested-archive",
                            relative,
                            "Nested archive content is outside the single extraction boundary.",
                            "Submit expanded readable source files instead of nested archives.",
                        )
                        continue
                    try:
                        data = _read_directory_file(
                            entry.name,
                            metadata,
                            limits.max_file_bytes,
                            dir_fd=current_descriptor,
                        )
                    except OSError as exc:
                        raise IntakeError(
                            f"cannot read package entry {entry.name}: {exc}"
                        ) from exc
                    if data is None:
                        stage["files"].append(
                            _record(
                                relative,
                                "file",
                                metadata.st_size,
                                None,
                                "rejected",
                            )
                        )
                        _append_finding(
                            stage["findings"],
                            "intake.source-changed",
                            relative,
                            "A source file changed while the quarantine copy was being created.",
                            "Retry intake from an immutable contribution snapshot.",
                        )
                        continue
                    _stage_data(
                        data,
                        relative,
                        destination,
                        stage["files"],
                        stage["findings"],
                    )
            finally:
                os.close(current_descriptor)
    finally:
        for descriptor, _prefix in queue:
            os.close(descriptor)

    return _finalize_stage(stage)


def _archive_limit_stage(
    source: Path,
    source_type: str,
    limits: IntakeLimits,
    source_label: str,
) -> Optional[Dict[str, Any]]:
    size = source.stat().st_size
    if size <= limits.max_archive_bytes:
        return None
    stage = _empty_stage(source_type)
    stage["source_bytes"] = size
    _append_finding(
        stage["findings"],
        "intake.archive-size-limit",
        source_label,
        "The compressed archive exceeds the quarantine input byte limit.",
        "Publish a smaller source-only contribution for review.",
    )
    return stage


def _observe_archive_file(
    relative: str,
    size: int,
    limits: IntakeLimits,
    stage: Dict[str, Any],
) -> bool:
    stage["file_count"] += 1
    stage["total_bytes"] += size
    return not _limit_file(
        relative,
        size,
        stage["file_count"],
        stage["total_bytes"],
        limits,
        stage["findings"],
    )


def _archive_content_allowed(relative: str, stage: Dict[str, Any]) -> bool:
    if not _archive_name(relative):
        return True
    _append_finding(
        stage["findings"],
        "intake.nested-archive",
        relative,
        "Nested archive content is outside the single extraction boundary.",
        "Submit expanded readable source files instead of nested archives.",
    )
    return False


def _read_bounded(stream: BinaryIO, expected_size: int, limit: int) -> bytes:
    chunks: List[bytes] = []
    observed = 0
    ceiling = min(expected_size, limit) + 1
    while observed < ceiling:
        chunk = stream.read(min(CHUNK_BYTES, ceiling - observed))
        if not chunk:
            break
        chunks.append(chunk)
        observed += len(chunk)
    data = b"".join(chunks)
    if len(data) > limit:
        raise IntakeError("archive member expanded beyond the declared intake limit")
    if len(data) != expected_size:
        raise IntakeError("archive member size differs from its declared metadata")
    return data


def _read_directory_file(
    path: str,
    metadata: os.stat_result,
    limit: int,
    dir_fd: Optional[int] = None,
) -> Optional[bytes]:
    flags = os.O_RDONLY
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, dir_fd=dir_fd)
    with os.fdopen(descriptor, "rb") as handle:
        opened = os.fstat(handle.fileno())
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_dev != metadata.st_dev
            or opened.st_ino != metadata.st_ino
        ):
            return None
        try:
            data = _read_bounded(handle, opened.st_size, limit)
        except IntakeError:
            return None
        after_read = os.fstat(handle.fileno())
    try:
        after_path = os.stat(path, dir_fd=dir_fd, follow_symlinks=False)
    except OSError:
        return None
    expected = (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )
    observed = (opened, after_read, after_path)
    unchanged = all(
        (
            item.st_dev,
            item.st_ino,
            item.st_mode,
            item.st_size,
            item.st_mtime_ns,
            item.st_ctime_ns,
        )
        == expected
        for item in observed
    )
    return data if unchanged else None


def _snapshot_archive(source: Path, destination: Path, limit: int) -> None:
    metadata = os.stat(str(source), follow_symlinks=False)
    if not stat.S_ISREG(metadata.st_mode):
        raise IntakeError("archive source changed before quarantine snapshot")
    try:
        data = _read_directory_file(str(source), metadata, limit)
    except OSError as exc:
        raise IntakeError(f"cannot snapshot archive source: {exc}") from exc
    if data is None:
        raise IntakeError("archive source changed while creating quarantine snapshot")
    destination.write_bytes(data)


def _stage_zip(
    source: Path,
    destination: Path,
    limits: IntakeLimits,
    source_label: Optional[str] = None,
) -> Dict[str, Any]:
    display_label = source_label or source.name
    limited = _archive_limit_stage(source, "zip", limits, display_label)
    if limited is not None:
        return _finalize_stage(limited)
    stage = _empty_stage("zip")
    stage.update(
        {
            "source_bytes": source.stat().st_size,
            "source_sha256": _sha256_file(source),
            "digest_scope": "archive-bytes",
            "complete": True,
        }
    )
    destination.mkdir(parents=True, exist_ok=True)
    seen: Dict[str, str] = {}
    members: List[Tuple[zipfile.ZipInfo, str]] = []
    try:
        with zipfile.ZipFile(source) as archive:
            for info in archive.infolist():
                stage["entry_count"] += 1
                if stage["entry_count"] > limits.max_entries:
                    _append_finding(
                        stage["findings"],
                        "intake.entry-count-limit",
                        info.filename,
                        "The archive exceeds the quarantine entry-count limit.",
                        "Remove generated trees and split the contribution.",
                    )
                    stage["complete"] = False
                    break
                relative = _validate_member_path(
                    info.filename.rstrip("/") if info.is_dir() else info.filename,
                    limits,
                    stage["findings"],
                )
                if info.is_dir():
                    if relative:
                        _register_package_path(
                            relative,
                            "directory",
                            stage["findings"],
                            seen,
                        )
                    continue
                mode = (info.external_attr >> 16) & 0xFFFF
                file_type = stat.S_IFMT(mode)
                if file_type == stat.S_IFLNK:
                    stage["files"].append(
                        _record(info.filename, "symlink", 0, None, "rejected")
                    )
                    _append_finding(
                        stage["findings"],
                        "intake.symlink",
                        info.filename,
                        "A ZIP symbolic link can escape or alias the quarantine boundary.",
                        "Replace the link with a regular reviewed file.",
                    )
                    continue
                if file_type not in {0, stat.S_IFREG}:
                    stage["files"].append(
                        _record(info.filename, "special", 0, None, "rejected")
                    )
                    _append_finding(
                        stage["findings"],
                        "intake.special-file",
                        info.filename,
                        "A non-regular ZIP member is not reviewable source.",
                        "Remove special entries from the archive.",
                    )
                    continue
                observed_path = relative or info.filename
                if not _observe_archive_file(
                    observed_path,
                    info.file_size,
                    limits,
                    stage,
                ):
                    stage["files"].append(
                        _record(observed_path, "file", info.file_size, None, "unread")
                    )
                    continue
                if relative is None:
                    stage["files"].append(
                        _record(info.filename, "file", info.file_size, None, "rejected")
                    )
                    continue
                if not _register_package_path(
                    relative,
                    "file",
                    stage["findings"],
                    seen,
                ):
                    stage["files"].append(
                        _record(relative, "file", info.file_size, None, "rejected")
                    )
                    continue
                if not _archive_content_allowed(relative, stage):
                    stage["files"].append(
                        _record(relative, "file", info.file_size, None, "rejected")
                    )
                    continue
                if info.flag_bits & 0x1:
                    stage["files"].append(
                        _record(relative, "file", info.file_size, None, "rejected")
                    )
                    _append_finding(
                        stage["findings"],
                        "intake.encrypted-entry",
                        info.filename,
                        "Encrypted archive content cannot be statically reviewed.",
                        "Submit unencrypted source files for review.",
                    )
                    continue
                if info.file_size and (
                    info.file_size / max(info.compress_size, 1)
                    > limits.max_compression_ratio
                ):
                    _append_finding(
                        stage["findings"],
                        "intake.compression-ratio-limit",
                        relative,
                        "An archive member exceeds the quarantine compression-ratio limit.",
                        "Submit ordinary source files without extreme compression.",
                    )
                    stage["files"].append(
                        _record(relative, "file", info.file_size, None, "rejected")
                    )
                    continue
                members.append((info, relative))

            if stage["total_bytes"] and (
                stage["total_bytes"] / max(stage["source_bytes"], 1)
                > limits.max_compression_ratio
            ):
                _append_finding(
                    stage["findings"],
                    "intake.compression-ratio-limit",
                    display_label,
                    "The archive exceeds the quarantine aggregate compression-ratio limit.",
                    "Submit ordinary source files without extreme compression.",
                )
            if not stage["findings"]:
                for info, relative in members:
                    with archive.open(info, "r") as stream:
                        data = _read_bounded(
                            stream,
                            info.file_size,
                            limits.max_file_bytes,
                        )
                    _stage_data(
                        data,
                        relative,
                        destination,
                        stage["files"],
                        stage["findings"],
                    )
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise IntakeError(f"cannot inspect ZIP archive: {exc}") from exc
    return _finalize_stage(stage)


def _stage_tar(
    source: Path,
    destination: Path,
    limits: IntakeLimits,
    source_label: Optional[str] = None,
) -> Dict[str, Any]:
    display_label = source_label or source.name
    limited = _archive_limit_stage(source, "tar", limits, display_label)
    if limited is not None:
        return _finalize_stage(limited)
    stage = _empty_stage("tar")
    stage.update(
        {
            "source_bytes": source.stat().st_size,
            "source_sha256": _sha256_file(source),
            "digest_scope": "archive-bytes",
            "complete": True,
        }
    )
    destination.mkdir(parents=True, exist_ok=True)
    seen: Dict[str, str] = {}
    members: List[Tuple[tarfile.TarInfo, str]] = []
    try:
        with tarfile.open(source, mode="r:*") as archive:
            for member in archive:
                stage["entry_count"] += 1
                if stage["entry_count"] > limits.max_entries:
                    _append_finding(
                        stage["findings"],
                        "intake.entry-count-limit",
                        member.name,
                        "The archive exceeds the quarantine entry-count limit.",
                        "Remove generated trees and split the contribution.",
                    )
                    stage["complete"] = False
                    break
                relative = _validate_member_path(
                    member.name.rstrip("/") if member.isdir() else member.name,
                    limits,
                    stage["findings"],
                )
                if member.isdir():
                    if relative:
                        _register_package_path(
                            relative,
                            "directory",
                            stage["findings"],
                            seen,
                        )
                    continue
                if member.issym() or member.islnk():
                    stage["files"].append(
                        _record(member.name, "symlink", 0, None, "rejected")
                    )
                    _append_finding(
                        stage["findings"],
                        "intake.symlink",
                        member.name,
                        "A TAR link can escape or alias the quarantine boundary.",
                        "Replace the link with a regular reviewed file.",
                    )
                    continue
                if not member.isreg():
                    stage["files"].append(
                        _record(member.name, "special", 0, None, "rejected")
                    )
                    _append_finding(
                        stage["findings"],
                        "intake.special-file",
                        member.name,
                        "A non-regular TAR member is not reviewable source.",
                        "Remove devices, sockets, FIFOs, and special entries.",
                    )
                    continue
                observed_path = relative or member.name
                if not _observe_archive_file(
                    observed_path,
                    member.size,
                    limits,
                    stage,
                ):
                    stage["files"].append(
                        _record(observed_path, "file", member.size, None, "unread")
                    )
                    continue
                if relative is None:
                    stage["files"].append(
                        _record(member.name, "file", member.size, None, "rejected")
                    )
                    continue
                if not _register_package_path(
                    relative,
                    "file",
                    stage["findings"],
                    seen,
                ):
                    stage["files"].append(
                        _record(relative, "file", member.size, None, "rejected")
                    )
                    continue
                if not _archive_content_allowed(relative, stage):
                    stage["files"].append(
                        _record(relative, "file", member.size, None, "rejected")
                    )
                    continue
                members.append((member, relative))

            if stage["total_bytes"] and (
                stage["total_bytes"] / max(stage["source_bytes"], 1)
                > limits.max_compression_ratio
            ):
                _append_finding(
                    stage["findings"],
                    "intake.compression-ratio-limit",
                    display_label,
                    "The archive exceeds the quarantine aggregate compression-ratio limit.",
                    "Submit ordinary source files without extreme compression.",
                )
            if not stage["findings"]:
                for member, relative in members:
                    stream = archive.extractfile(member)
                    if stream is None:
                        raise IntakeError(f"cannot read TAR member {relative}")
                    with stream:
                        data = _read_bounded(
                            stream,
                            member.size,
                            limits.max_file_bytes,
                        )
                    _stage_data(
                        data,
                        relative,
                        destination,
                        stage["files"],
                        stage["findings"],
                    )
    except (OSError, tarfile.TarError) as exc:
        raise IntakeError(f"cannot inspect TAR archive: {exc}") from exc
    return _finalize_stage(stage)


def _source_type(source: Path) -> str:
    metadata = os.stat(str(source), follow_symlinks=False)
    if stat.S_ISDIR(metadata.st_mode):
        return "directory"
    if not stat.S_ISREG(metadata.st_mode):
        raise IntakeError("intake source must be a regular directory or archive")
    if zipfile.is_zipfile(source):
        return "zip"
    if tarfile.is_tarfile(source):
        return "tar"
    raise IntakeError("intake accepts a directory, ZIP archive, or TAR archive")


def _ensure_external_policy(source: Path, policy_path: Optional[Path]) -> None:
    if policy_path is None:
        return
    policy = policy_path.expanduser().resolve()
    if source.is_dir() and _is_within(policy, source.resolve()):
        raise IntakeError("an intake policy cannot be loaded from inside the contribution")
    if source.is_file() and policy == source.resolve():
        raise IntakeError("the contribution cannot be its own intake policy")


def intake_package(
    source: Path,
    policy_path: Optional[Path] = None,
    limits: IntakeLimits = DEFAULT_LIMITS,
    temp_parent: Optional[Path] = None,
) -> Dict[str, Any]:
    """Quarantine, inventory, and statically scan one untrusted contribution."""

    _validate_limits(limits)
    source = source.expanduser().absolute()
    if not source.exists() and not source.is_symlink():
        raise FileNotFoundError(f"intake source does not exist: {source}")
    _ensure_external_policy(source, policy_path)
    source_label = _safe_path_display(source.name or ".")
    source_type = "symlink" if source.is_symlink() else _source_type(source)
    security_report: Optional[Dict[str, Any]] = None
    quarantine_parent = (
        temp_parent.expanduser().resolve()
        if temp_parent is not None
        else Path(tempfile.gettempdir()).resolve()
    )
    if source_type == "directory" and _is_within(
        quarantine_parent,
        source.resolve(),
    ):
        raise IntakeError("quarantine workspace must be outside the contribution")

    with tempfile.TemporaryDirectory(
        prefix="hpc-skill-intake-",
        dir=str(quarantine_parent),
    ) as temp_dir:
        quarantine_root = Path(temp_dir).resolve()
        if source.is_dir() and _is_within(quarantine_root, source.resolve()):
            raise IntakeError("quarantine workspace must be outside the contribution")
        payload = quarantine_root / "payload"
        if source_type == "symlink":
            stage = _empty_stage("symlink")
            target = os.readlink(source)
            stage["source_sha256"] = hashlib.sha256(
                target.encode("utf-8", errors="surrogateescape")
            ).hexdigest()
            stage["digest_scope"] = "symlink-target"
            stage["files"].append(
                _record(source_label, "symlink", 0, stage["source_sha256"], "rejected")
            )
            _append_finding(
                stage["findings"],
                "intake.symlink",
                source_label,
                "The intake source itself is a symbolic link.",
                "Provide the explicit regular directory or archive to review.",
            )
            stage = _finalize_stage(stage)
        elif source_type == "directory":
            stage = _stage_directory(source, payload, limits)
        else:
            archive_source = source
            if source.stat().st_size <= limits.max_archive_bytes:
                archive_source = quarantine_root / "archive-input"
                _snapshot_archive(source, archive_source, limits.max_archive_bytes)
            if source_type == "zip":
                stage = _stage_zip(
                    archive_source,
                    payload,
                    limits,
                    source_label=source_label,
                )
            else:
                stage = _stage_tar(
                    archive_source,
                    payload,
                    limits,
                    source_label=source_label,
                )

        if not stage["findings"]:
            security_report = scan_target(
                payload,
                fail_on="policy",
                policy_path=policy_path.expanduser() if policy_path else None,
            )

    security_verdict = (
        security_report["summary"]["verdict"] if security_report else None
    )
    if stage["findings"] or security_verdict == "block":
        status = "blocked"
    elif security_verdict in {"review", "pass-with-exceptions"}:
        status = "review-required"
    else:
        status = "ready-for-review"

    return {
        "$schema": SCHEMA_URL,
        "schema_version": "0.1.0",
        "engine": {"name": INTAKE_NAME, "version": INTAKE_VERSION},
        "source": {
            "label": source_label,
            "type": stage["source_type"],
            "bytes": stage["source_bytes"],
            "sha256": stage["source_sha256"],
            "digest_scope": stage["digest_scope"],
        },
        "limits": asdict(limits),
        "quarantine": {
            "strategy": "temporary-copy",
            "outside_source": True,
            "cleaned": True,
            "execution_performed": False,
            "instruction_content_returned": False,
        },
        "inventory": {
            "complete": stage["complete"],
            "entry_count": stage["entry_count"],
            "file_count": stage["file_count"],
            "total_bytes": stage["total_bytes"],
            "content_digest": stage["content_digest"],
            "files": stage["files"],
        },
        "boundary_findings": stage["findings"],
        "security_report": security_report,
        "summary": {
            "status": status,
            "boundary_finding_count": len(stage["findings"]),
            "security_verdict": security_verdict,
            "eligible_for_human_review": status != "blocked",
            "context_loading_allowed": False,
        },
    }


def text_report(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    inventory = report["inventory"]
    lines = [
        f"Community skill intake: {summary['status'].upper()}",
        f"Source: {report['source']['label']} ({report['source']['type']})",
        (
            f"Observed {inventory['file_count']} file(s), "
            f"{inventory['total_bytes']} byte(s), "
            f"{summary['boundary_finding_count']} boundary finding(s)."
        ),
        (
            "Quarantine: temporary copy cleaned; no execution; "
            "no instruction content returned."
        ),
    ]
    if summary["security_verdict"]:
        lines.append(f"Security policy verdict: {summary['security_verdict']}")
    for item in report["boundary_findings"]:
        lines.append(
            f"{item['severity'].upper()}: {item['path']}: "
            f"{item['id']}: {item['message']}"
        )
    if report["security_report"]:
        for item in report["security_report"]["findings"]:
            lines.append(
                f"{item['severity'].upper()}: {item['path']}:{item['line']}: "
                f"{item['rule_id']}: {item['message']}"
            )
    lines.append("Context loading remains disabled until a later reviewed acceptance step.")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Quarantine and scan an untrusted community skill bundle"
    )
    parser.add_argument("source", help="Directory, ZIP archive, or TAR archive")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format",
    )
    parser.add_argument("--json", action="store_true", help="Alias for --format json")
    parser.add_argument(
        "--policy",
        type=Path,
        help="External policy pack stored outside the contribution",
    )
    return parser


def run_cli(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = intake_package(Path(args.source), policy_path=args.policy)
    except (FileNotFoundError, IntakeError, OSError, SecurityPolicyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json or args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(text_report(report))
    return 1 if report["summary"]["status"] == "blocked" else 0


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
