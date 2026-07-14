#!/usr/bin/env python3
"""Build deterministic, bounded, security-scanned skill context bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.context import (  # noqa: E402
    CONTEXT_GENERATOR,
    CONTEXT_SCHEMA_VERSION,
    canonical_sha256,
    digest_record,
    payload_without_digest,
    verify_context_bundle,
)
from hpc_skill_hub.security import SKIP_DIRS, scan_target  # noqa: E402


INDEX_JSON = ROOT / "registry" / "index.json"
OUTPUT_JSON = ROOT / "registry" / "skill-context.json"
MAX_FILE_BYTES = 65_536
MAX_FILES_PER_SKILL = 64
MAX_SKILL_BYTES = 262_144
MAX_TOTAL_BYTES = 2_097_152


class ContextBuildError(ValueError):
    """Raised when repository content crosses the generated trust boundary."""


def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContextBuildError(f"cannot read valid JSON from {path}: {exc}") from exc


def file_record(path: Path, repo_path: str, role: str, title: str = "") -> Dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ContextBuildError(f"declared artifact is not a regular file: {repo_path}")
    data = path.read_bytes()
    if len(data) > MAX_FILE_BYTES:
        raise ContextBuildError(
            f"declared artifact exceeds {MAX_FILE_BYTES} bytes: {repo_path}"
        )
    try:
        content = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContextBuildError(f"declared artifact is not UTF-8: {repo_path}") from exc
    if "\x00" in content:
        raise ContextBuildError(f"declared artifact contains NUL bytes: {repo_path}")
    record: Dict[str, Any] = {
        "path": repo_path,
        "role": role,
        "bytes": len(data),
        "digest": digest_record(hashlib.sha256(data).hexdigest()),
        "content": content,
    }
    if title:
        record["title"] = title
    return record


def normalized_artifact_path(value: Any, skill_id: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContextBuildError(f"{skill_id}: artifact path must be a non-empty string")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or ".." in posix.parts
        or ".." in windows.parts
        or posix.as_posix() != value
    ):
        raise ContextBuildError(f"{skill_id}: unsafe artifact path: {value}")
    return value


def iter_skill_files(skill_dir: Path) -> Iterable[Path]:
    for path in sorted(skill_dir.rglob("*")):
        relative = path.relative_to(skill_dir)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.is_symlink():
            raise ContextBuildError(
                f"symbolic links are not allowed in skill packages: {skill_dir.name}/{relative}"
            )
        if path.is_file():
            yield path


def security_provenance(skill_dir: Path) -> Dict[str, Any]:
    report = scan_target(skill_dir, fail_on="high")
    summary = report["summary"]
    if summary["verdict"] == "block":
        raise ContextBuildError(
            f"{skill_dir.name}: security scan blocked context generation "
            f"with {summary['blocking_count']} finding(s)"
        )
    return {
        "scanner": report["scanner"],
        "policy": report["policy"],
        "provenance": report["provenance"],
        "verdict": summary["verdict"],
        "files_scanned": summary["files_scanned"],
        "finding_count": summary["finding_count"],
        "blocking_count": summary["blocking_count"],
        "accepted_exception_count": summary["accepted_exception_count"],
        "severity_counts": summary["severity_counts"],
        "report_digest": digest_record(canonical_sha256(report)),
        "findings": [
            {
                "rule_id": item["rule_id"],
                "base_severity": item["base_severity"],
                "severity": item["severity"],
                "category": item["category"],
                "path": item["path"],
                "line": item["line"],
                "fingerprint": item["fingerprint"],
                "finding_digest": item["finding_digest"],
                "disposition": item["disposition"],
                "exception": item["exception"],
            }
            for item in report["findings"]
        ],
    }


def build_skill(root: Path, indexed: Dict[str, Any]) -> Dict[str, Any]:
    skill_id = indexed["id"]
    expected_source_path = f"skills/{skill_id}"
    if indexed.get("path") != expected_source_path:
        raise ContextBuildError(
            f"{skill_id}: registry path must be {expected_source_path}"
        )
    skill_dir = root / expected_source_path
    manifest_path = skill_dir / "skill.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ContextBuildError(f"{skill_id}: skill.json is missing or not a regular file")
    manifest = load_json(manifest_path)
    for field in ("id", "version", "status", "maturity", "risk_level"):
        if manifest.get(field) != indexed.get(field):
            raise ContextBuildError(f"{skill_id}: registry {field} does not match skill.json")

    declared_list = manifest.get("artifacts")
    if not isinstance(declared_list, list):
        raise ContextBuildError(f"{skill_id}: artifacts must be an array")
    declared = [normalized_artifact_path(value, skill_id) for value in declared_list]
    if len(declared) != len(set(declared)):
        raise ContextBuildError(f"{skill_id}: duplicate artifact paths")
    if "README.md" not in declared:
        raise ContextBuildError(f"{skill_id}: artifacts must include README.md")
    if len(declared) > MAX_FILES_PER_SKILL:
        raise ContextBuildError(
            f"{skill_id}: artifact count exceeds {MAX_FILES_PER_SKILL}"
        )

    actual = {
        path.relative_to(skill_dir).as_posix() for path in iter_skill_files(skill_dir)
    }
    expected = set(declared) | {"skill.json"}
    missing = sorted(expected - actual)
    untracked = sorted(actual - expected)
    if missing:
        raise ContextBuildError(f"{skill_id}: missing declared files: {', '.join(missing)}")
    if untracked:
        raise ContextBuildError(
            f"{skill_id}: files are not declared in artifacts: {', '.join(untracked)}"
        )

    example_titles = {
        item["path"]: item["title"] for item in indexed.get("examples", [])
    }
    indexed_readme = indexed.get("readme")
    expected_readme = f"{expected_source_path}/README.md"
    if indexed_readme != expected_readme:
        raise ContextBuildError(f"{skill_id}: registry README path mismatch")
    manifest_examples = {
        f"{expected_source_path}/{item['path']}": item["title"]
        for item in manifest.get("examples", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    if manifest_examples != example_titles:
        raise ContextBuildError(f"{skill_id}: registry examples do not match skill.json")

    files: List[Dict[str, Any]] = []
    for artifact in sorted(declared):
        repo_path = f"{expected_source_path}/{artifact}"
        role = "readme" if artifact == "README.md" else (
            "example" if repo_path in example_titles else "artifact"
        )
        files.append(
            file_record(
                skill_dir / artifact,
                repo_path,
                role,
                example_titles.get(repo_path, ""),
            )
        )
    total_bytes = sum(item["bytes"] for item in files)
    if total_bytes > MAX_SKILL_BYTES:
        raise ContextBuildError(
            f"{skill_id}: content exceeds {MAX_SKILL_BYTES} bytes"
        )

    manifest_data = manifest_path.read_bytes()
    if len(manifest_data) > MAX_FILE_BYTES:
        raise ContextBuildError(f"{skill_id}: skill.json exceeds {MAX_FILE_BYTES} bytes")
    skill: Dict[str, Any] = {
        "id": skill_id,
        "name": indexed["name"],
        "version": indexed["version"],
        "status": indexed["status"],
        "maturity": indexed["maturity"],
        "risk_level": indexed["risk_level"],
        "source_path": expected_source_path,
        "manifest": {
            "path": f"{expected_source_path}/skill.json",
            "bytes": len(manifest_data),
            "digest": digest_record(hashlib.sha256(manifest_data).hexdigest()),
        },
        "security": security_provenance(skill_dir),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "files": files,
    }
    skill["digest"] = digest_record(canonical_sha256(payload_without_digest(skill)))
    return skill


def build_context(root: Path = ROOT) -> Dict[str, Any]:
    index_path = root / "registry" / "index.json"
    index_data = index_path.read_bytes()
    index = load_json(index_path)
    skills = [build_skill(root, item) for item in index.get("skills", [])]
    skills.sort(key=lambda item: item["id"])
    if len(skills) != index.get("skill_count"):
        raise ContextBuildError("registry skill_count does not match indexed skills")
    total_bytes = sum(item["total_bytes"] for item in skills)
    if total_bytes > MAX_TOTAL_BYTES:
        raise ContextBuildError(
            f"registry context exceeds {MAX_TOTAL_BYTES} bytes"
        )
    payload: Dict[str, Any] = {
        "$schema": "../schemas/skill-context-bundle.schema.json",
        "schema_version": CONTEXT_SCHEMA_VERSION,
        "generated_by": CONTEXT_GENERATOR,
        "source_index": {
            "path": "registry/index.json",
            "digest": digest_record(hashlib.sha256(index_data).hexdigest()),
        },
        "limits": {
            "max_file_bytes": MAX_FILE_BYTES,
            "max_files_per_skill": MAX_FILES_PER_SKILL,
            "max_skill_bytes": MAX_SKILL_BYTES,
            "max_total_bytes": MAX_TOTAL_BYTES,
        },
        "skill_count": len(skills),
        "file_count": sum(item["file_count"] for item in skills),
        "total_bytes": total_bytes,
        "skills": skills,
    }
    payload["digest"] = digest_record(canonical_sha256(payload_without_digest(payload)))
    verify_context_bundle(payload)
    return payload


def rendered(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build bounded, digest-verified skill context bundles"
    )
    parser.add_argument("--check", action="store_true", help="Fail if output is stale")
    args = parser.parse_args()
    try:
        payload = build_context(ROOT)
    except (ContextBuildError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    expected = rendered(payload)
    if args.check:
        if not OUTPUT_JSON.exists():
            print(f"ERROR: {OUTPUT_JSON.relative_to(ROOT)} is missing", file=sys.stderr)
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != expected:
            print(
                f"ERROR: {OUTPUT_JSON.relative_to(ROOT)} is stale; "
                "run tools/build_skill_context.py",
                file=sys.stderr,
            )
            return 1
        print(
            f"Skill context is current for {payload['skill_count']} skill(s) and "
            f"{payload['file_count']} file(s)."
        )
        return 0
    OUTPUT_JSON.write_text(expected, encoding="utf-8")
    print(
        f"Wrote {OUTPUT_JSON.relative_to(ROOT)} for {payload['skill_count']} "
        f"skill(s) and {payload['file_count']} file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
