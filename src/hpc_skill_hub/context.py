"""Load and verify packaged skill context bundles."""

from __future__ import annotations

import hashlib
import importlib.resources as resources
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Optional, Tuple

from .security import RULE_CATALOG
from .security_policy import (
    SecurityPolicyError,
    load_effective_policy,
    policy_receipt,
)


PACKAGE_NAME = "hpc_skill_hub"
CONTEXT_FILENAME = "skill-context.json"
CONTEXT_SCHEMA_VERSION = "0.2.0"
CONTEXT_GENERATOR = "tools/build_skill_context.py"
RESOURCE_URI_TEMPLATE = "hpc-skill://skills/{skill_id}"


class ContextBundleError(ValueError):
    """Raised when a context bundle fails its integrity contract."""


def canonical_sha256(payload: Any) -> str:
    """Return a stable SHA-256 over canonical UTF-8 JSON."""
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def digest_record(value: str) -> Dict[str, str]:
    return {"algorithm": "sha256", "value": value}


def payload_without_digest(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "digest"}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContextBundleError(message)


def _verify_digest(record: Any, expected: str, context: str) -> None:
    _require(
        isinstance(expected, str) and re.fullmatch(r"[a-f0-9]{64}", expected) is not None,
        f"{context}: expected SHA-256 is invalid",
    )
    _require(isinstance(record, dict), f"{context}: digest must be an object")
    _require(record.get("algorithm") == "sha256", f"{context}: unsupported digest")
    _require(record.get("value") == expected, f"{context}: SHA-256 mismatch")


def _safe_repo_path(value: Any, context: str) -> str:
    _require(isinstance(value, str) and bool(value), f"{context}: invalid path")
    path = PurePosixPath(value)
    _require(not path.is_absolute(), f"{context}: absolute path is not allowed")
    _require(".." not in path.parts, f"{context}: path escape is not allowed")
    _require(path.as_posix() == value, f"{context}: path must be normalized POSIX")
    return value


def verify_context_bundle(payload: Dict[str, Any]) -> None:
    """Fail closed unless all bundle counts, bounds, paths, and digests match."""
    try:
        expected_policy = load_effective_policy(RULE_CATALOG)
    except (SecurityPolicyError, OSError) as exc:
        raise ContextBundleError(f"packaged security policy is invalid: {exc}") from exc
    expected_policy_receipt = policy_receipt(expected_policy)
    expected_policy_receipt["fail_on"] = expected_policy.fail_on

    _require(isinstance(payload, dict), "context bundle must be an object")
    _require(
        payload.get("schema_version") == CONTEXT_SCHEMA_VERSION,
        "context bundle schema_version mismatch",
    )
    _require(
        payload.get("$schema") == "../schemas/skill-context-bundle.schema.json",
        "context bundle $schema mismatch",
    )
    _require(
        payload.get("generated_by") == CONTEXT_GENERATOR,
        "context bundle generated_by mismatch",
    )
    source_index = payload.get("source_index")
    _require(isinstance(source_index, dict), "source_index must be an object")
    _require(
        _safe_repo_path(source_index.get("path"), "source_index")
        == "registry/index.json",
        "source_index path mismatch",
    )
    source_digest = source_index.get("digest")
    _verify_digest(
        source_digest,
        source_digest.get("value", "") if isinstance(source_digest, dict) else "",
        "source_index",
    )

    limits = payload.get("limits")
    _require(isinstance(limits, dict), "limits must be an object")
    for name in (
        "max_file_bytes",
        "max_files_per_skill",
        "max_skill_bytes",
        "max_total_bytes",
    ):
        _require(
            isinstance(limits.get(name), int) and limits[name] > 0,
            f"limits.{name} must be a positive integer",
        )

    skills = payload.get("skills")
    _require(isinstance(skills, list), "skills must be an array")
    _require(payload.get("skill_count") == len(skills), "skill_count mismatch")

    skill_ids = []
    total_files = 0
    total_bytes = 0
    for skill in skills:
        _require(isinstance(skill, dict), "skill context must be an object")
        skill_id = skill.get("id")
        _require(
            isinstance(skill_id, str)
            and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_id) is not None,
            "skill id is invalid",
        )
        skill_ids.append(skill_id)
        context = f"skills/{skill_id}"
        source_path = _safe_repo_path(skill.get("source_path"), context)
        _require(source_path == context, f"{context}: source_path mismatch")

        manifest = skill.get("manifest")
        _require(isinstance(manifest, dict), f"{context}: manifest must be an object")
        _require(
            _safe_repo_path(manifest.get("path"), f"{context}: manifest")
            == f"{context}/skill.json",
            f"{context}: manifest path mismatch",
        )
        _require(
            isinstance(manifest.get("bytes"), int) and manifest["bytes"] >= 0,
            f"{context}: invalid manifest byte count",
        )
        digest = manifest.get("digest")
        _require(
            isinstance(digest, dict)
            and digest.get("algorithm") == "sha256"
            and isinstance(digest.get("value"), str)
            and len(digest["value"]) == 64,
            f"{context}: invalid manifest digest",
        )

        security = skill.get("security")
        _require(isinstance(security, dict), f"{context}: security must be an object")
        scanner = security.get("scanner")
        _require(
            isinstance(scanner, dict)
            and scanner.get("name") == "hpc-skill-security"
            and scanner.get("version") == "0.2.0",
            f"{context}: invalid security scanner provenance",
        )
        policy = security.get("policy")
        _require(
            policy == expected_policy_receipt,
            f"{context}: invalid security policy provenance",
        )
        provenance = security.get("provenance")
        _require(
            isinstance(provenance, dict)
            and provenance.get("policy_digest") == policy["effective_digest"]
            and all(
                isinstance(provenance.get(field), str)
                and re.fullmatch(r"[a-f0-9]{64}", provenance[field]) is not None
                for field in ("target_digest", "rule_catalog_digest", "policy_digest")
            )
            and isinstance(provenance.get("applied_exception_ids"), list),
            f"{context}: invalid security scan provenance receipt",
        )
        _require(
            security.get("verdict") in {"pass", "pass-with-exceptions", "review"},
            f"{context}: blocked security verdict",
        )
        _require(
            security.get("blocking_count") == 0,
            f"{context}: security report has blocking findings",
        )
        findings = security.get("findings")
        _require(isinstance(findings, list), f"{context}: security findings must be an array")
        _require(
            security.get("finding_count") == len(findings),
            f"{context}: security finding_count mismatch",
        )
        accepted = [item for item in findings if item.get("disposition") == "accepted"]
        _require(
            security.get("accepted_exception_count")
            == len(provenance["applied_exception_ids"])
            == len(accepted),
            f"{context}: accepted security exception count mismatch",
        )
        for item in findings:
            _require(
                item.get("base_severity") in {"low", "medium", "high", "critical"}
                and item.get("severity") in {"low", "medium", "high", "critical"}
                and item.get("disposition") in {"active", "accepted"}
                and isinstance(item.get("finding_digest"), str)
                and re.fullmatch(r"[a-f0-9]{64}", item["finding_digest"]) is not None,
                f"{context}: invalid security finding receipt",
            )
            _require(
                (item.get("disposition") == "accepted")
                == isinstance(item.get("exception"), dict),
                f"{context}: invalid security finding exception",
            )
        severity_counts = security.get("severity_counts")
        _require(
            isinstance(severity_counts, dict)
            and all(
                isinstance(severity_counts.get(level), int)
                and severity_counts[level] >= 0
                for level in ("low", "medium", "high", "critical")
            ),
            f"{context}: invalid security severity counts",
        )
        _require(
            sum(severity_counts.values()) == len(findings),
            f"{context}: security severity count mismatch",
        )
        report_digest = security.get("report_digest")
        _verify_digest(
            report_digest,
            report_digest.get("value", "") if isinstance(report_digest, dict) else "",
            f"{context}: security report",
        )

        files = skill.get("files")
        _require(isinstance(files, list), f"{context}: files must be an array")
        _require(skill.get("file_count") == len(files), f"{context}: file_count mismatch")
        _require(
            len(files) <= limits["max_files_per_skill"],
            f"{context}: file count exceeds bundle limit",
        )
        paths = []
        skill_bytes = 0
        readme_count = 0
        for source in files:
            _require(isinstance(source, dict), f"{context}: file must be an object")
            path = _safe_repo_path(source.get("path"), f"{context}: file")
            _require(path.startswith(f"{context}/"), f"{path}: file is outside skill path")
            role = source.get("role")
            _require(
                role in {"readme", "example", "artifact"},
                f"{path}: invalid content role",
            )
            if role == "readme":
                readme_count += 1
                _require(path == f"{context}/README.md", f"{path}: README path mismatch")
            paths.append(path)
            content = source.get("content")
            _require(isinstance(content, str), f"{path}: content must be UTF-8 text")
            encoded = content.encode("utf-8")
            _require(source.get("bytes") == len(encoded), f"{path}: byte count mismatch")
            _require(
                len(encoded) <= limits["max_file_bytes"],
                f"{path}: file exceeds bundle limit",
            )
            _verify_digest(
                source.get("digest"), hashlib.sha256(encoded).hexdigest(), path
            )
            skill_bytes += len(encoded)

        _require(readme_count == 1, f"{context}: expected exactly one README")
        _require(
            security.get("files_scanned") == len(files) + 1,
            f"{context}: security scan file count mismatch",
        )
        _require(paths == sorted(paths), f"{context}: file paths must be sorted")
        _require(len(paths) == len(set(paths)), f"{context}: duplicate file paths")
        _require(skill.get("total_bytes") == skill_bytes, f"{context}: total_bytes mismatch")
        _require(
            skill_bytes <= limits["max_skill_bytes"],
            f"{context}: content exceeds per-skill limit",
        )
        _verify_digest(
            skill.get("digest"), canonical_sha256(payload_without_digest(skill)), context
        )
        total_files += len(files)
        total_bytes += skill_bytes

    _require(skill_ids == sorted(skill_ids), "skill contexts must be sorted by id")
    _require(len(skill_ids) == len(set(skill_ids)), "duplicate skill context ids")
    _require(payload.get("file_count") == total_files, "file_count mismatch")
    _require(payload.get("total_bytes") == total_bytes, "total_bytes mismatch")
    _require(total_bytes <= limits["max_total_bytes"], "bundle exceeds total byte limit")
    _verify_digest(
        payload.get("digest"), canonical_sha256(payload_without_digest(payload)), "bundle"
    )


def _repository_root() -> Optional[Path]:
    candidates = []
    env_root = os.environ.get("HPC_SKILL_HUB_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser())
    candidates.append(Path.cwd())
    candidates.extend(Path(__file__).resolve().parents)
    for candidate in candidates:
        if (
            (candidate / "registry" / "index.json").is_file()
            and (candidate / "skills").is_dir()
        ):
            return candidate
    return None


def _registry_bytes(filename: str) -> Tuple[bytes, str]:
    repository_root = _repository_root()
    if repository_root:
        repository_path = repository_root / "registry" / filename
        if not repository_path.is_file():
            raise ContextBundleError(
                f"repository registry data is missing: registry/{filename}"
            )
        return repository_path.read_bytes(), "repository"
    try:
        data_path = resources.files(PACKAGE_NAME).joinpath("data", "registry", filename)
        return data_path.read_bytes(), "packaged-context"
    except FileNotFoundError as exc:
        raise ContextBundleError(
            f"packaged registry data is missing: data/registry/{filename}"
        ) from exc


def load_context_bundle() -> Dict[str, Any]:
    """Load a repository or packaged context bundle and verify it before use."""
    raw, _ = _registry_bytes(CONTEXT_FILENAME)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContextBundleError(f"context bundle is not valid UTF-8 JSON: {exc}") from exc
    verify_context_bundle(payload)

    index_raw, _ = _registry_bytes("index.json")
    expected = payload["source_index"]["digest"]["value"]
    actual = hashlib.sha256(index_raw).hexdigest()
    _require(actual == expected, "context bundle does not match registry/index.json")
    return payload


def find_skill_context(
    payload: Dict[str, Any], skill_id: str
) -> Optional[Dict[str, Any]]:
    for skill in payload["skills"]:
        if skill["id"] == skill_id:
            return skill
    return None


def skill_resource_uri(skill_id: str) -> str:
    return RESOURCE_URI_TEMPLATE.format(skill_id=skill_id)


def context_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_version": payload["schema_version"],
        "skill_count": payload["skill_count"],
        "file_count": payload["file_count"],
        "total_bytes": payload["total_bytes"],
        "digest": payload["digest"],
        "limits": payload["limits"],
        "resource_uri_template": RESOURCE_URI_TEMPLATE,
    }
