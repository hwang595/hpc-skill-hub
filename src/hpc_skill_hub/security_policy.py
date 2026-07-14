"""Versioned, fail-closed policy packs for community skill scanning."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Dict, Mapping, Optional, Tuple


POLICY_SCHEMA_URL = "https://hpc-skill-hub.org/schemas/skill-security-policy.schema.json"
POLICY_SCHEMA_VERSION = "0.1.0"
DEFAULT_POLICY_ID = "community-default"
DEFAULT_POLICY_VERSION = "0.1.0"
DEFAULT_POLICY_REF = f"{DEFAULT_POLICY_ID}@{DEFAULT_POLICY_VERSION}"
SEVERITIES = ("low", "medium", "high", "critical")
SEVERITY_RANK = {severity: index for index, severity in enumerate(SEVERITIES)}
POLICY_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SKILL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SecurityPolicyError(ValueError):
    """Raised when a policy pack is invalid or weakens the trusted baseline."""


@dataclass(frozen=True)
class ReviewedException:
    exception_id: str
    rule_id: str
    skill_id: Optional[str]
    path: str
    finding_digest: str
    expires_on: str
    review_digest: str


@dataclass(frozen=True)
class EffectivePolicy:
    policy_id: str
    version: str
    source: str
    source_digest: str
    effective_digest: str
    fail_on: str
    exception_max_severity: str
    enabled_rules: Tuple[str, ...]
    severity_overrides: Mapping[str, str]
    exceptions: Tuple[ReviewedException, ...]

    def severity_for(self, rule_id: str, base_severity: str) -> str:
        return self.severity_overrides.get(rule_id, base_severity)

    def exception_for(
        self,
        rule_id: str,
        skill_id: Optional[str],
        path: str,
        finding_digest: str,
    ) -> Optional[ReviewedException]:
        for exception in self.exceptions:
            if (
                exception.rule_id == rule_id
                and exception.skill_id == skill_id
                and exception.path == path
                and exception.finding_digest == finding_digest
            ):
                return exception
        return None


def canonical_digest(payload: Any) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def default_policy_path() -> Path:
    source_path = Path(__file__).resolve().parents[2] / "security" / "policies" / "community-default.json"
    if source_path.is_file():
        return source_path
    return Path(__file__).resolve().parent / "data" / "security" / "community-default.json"


def load_policy_payload(path: Path) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SecurityPolicyError(f"cannot read security policy {path.name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SecurityPolicyError("security policy must be a JSON object")
    return payload


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SecurityPolicyError(message)


def _date(value: Any, field: str) -> date:
    _require(isinstance(value, str), f"{field} must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SecurityPolicyError(f"{field} must be an ISO date") from exc


def _inside(path: Path, target: Path) -> bool:
    try:
        path.resolve().relative_to(target.resolve())
        return True
    except ValueError:
        return False


def _safe_relative_path(value: Any, context: str) -> str:
    _require(isinstance(value, str) and value, f"{context}: path is invalid")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    _require(
        not posix.is_absolute()
        and not windows.is_absolute()
        and ".." not in posix.parts
        and ".." not in windows.parts
        and posix.as_posix() == value,
        f"{context}: path must be normalized and package-relative",
    )
    return value


def _validate_policy_shape(payload: Dict[str, Any], context: str) -> None:
    expected = {
        "$schema",
        "schema_version",
        "id",
        "version",
        "description",
        "extends",
        "enforcement",
        "rules",
        "severity_overrides",
        "exceptions",
    }
    _require(set(payload) == expected, f"{context}: policy fields do not match schema")
    _require(payload["$schema"] == POLICY_SCHEMA_URL, f"{context}: unsupported $schema")
    _require(
        payload["schema_version"] == POLICY_SCHEMA_VERSION,
        f"{context}: unsupported schema_version",
    )
    _require(
        isinstance(payload["id"], str)
        and POLICY_ID_RE.fullmatch(payload["id"]) is not None,
        f"{context}: invalid id",
    )
    _require(
        isinstance(payload["version"], str)
        and SEMVER_RE.fullmatch(payload["version"]) is not None,
        f"{context}: invalid version",
    )
    _require(
        isinstance(payload["description"], str) and payload["description"],
        f"{context}: invalid description",
    )
    enforcement = payload["enforcement"]
    _require(isinstance(enforcement, dict), f"{context}: enforcement must be an object")
    _require(
        set(enforcement) == {"fail_on", "exception_max_severity"},
        f"{context}: enforcement fields do not match schema",
    )
    _require(enforcement["fail_on"] in SEVERITIES, f"{context}: invalid fail_on")
    _require(
        enforcement["exception_max_severity"] in {"low", "medium"},
        f"{context}: invalid exception_max_severity",
    )
    for field in ("rules", "severity_overrides", "exceptions"):
        _require(isinstance(payload[field], list), f"{context}: {field} must be an array")


def _normalize_policy(
    payload: Dict[str, Any],
    rule_catalog: Mapping[str, str],
    *,
    source: str,
    baseline: Optional[EffectivePolicy],
    today: date,
) -> EffectivePolicy:
    context = f"security policy {payload.get('id', '<unknown>')}"
    _validate_policy_shape(payload, context)
    rule_entries = payload["rules"]
    rule_ids = []
    for entry in rule_entries:
        _require(
            isinstance(entry, dict) and set(entry) == {"id", "enabled"},
            f"{context}: each rule must contain only id and enabled",
        )
        rule_id = entry["id"]
        _require(isinstance(rule_id, str), f"{context}: rule id must be a string")
        _require(entry["enabled"] is True, f"{context}: rule {rule_id} cannot be disabled")
        rule_ids.append(rule_id)
    _require(len(rule_ids) == len(set(rule_ids)), f"{context}: duplicate rule ids")
    _require(
        set(rule_ids) == set(rule_catalog),
        f"{context}: explicit rules must exactly match the scanner rule catalog",
    )

    overrides: Dict[str, str] = {}
    for entry in payload["severity_overrides"]:
        _require(
            isinstance(entry, dict) and set(entry) == {"rule_id", "severity"},
            f"{context}: invalid severity override",
        )
        rule_id = entry["rule_id"]
        severity = entry["severity"]
        _require(rule_id in rule_catalog, f"{context}: unknown override rule {rule_id}")
        _require(severity in SEVERITIES, f"{context}: invalid severity for {rule_id}")
        _require(rule_id not in overrides, f"{context}: duplicate override for {rule_id}")
        _require(
            SEVERITY_RANK[severity] >= SEVERITY_RANK[rule_catalog[rule_id]],
            f"{context}: severity override for {rule_id} cannot lower the scanner default",
        )
        overrides[rule_id] = severity

    enforcement = payload["enforcement"]
    fail_on = enforcement["fail_on"]
    exception_max = enforcement["exception_max_severity"]
    if baseline is None:
        _require(payload["id"] == DEFAULT_POLICY_ID, f"{context}: invalid baseline id")
        _require(payload["version"] == DEFAULT_POLICY_VERSION, f"{context}: invalid baseline version")
        _require(payload["extends"] is None, f"{context}: baseline cannot extend another pack")
    else:
        _require(payload["extends"] == DEFAULT_POLICY_REF, f"{context}: must extend {DEFAULT_POLICY_REF}")
        _require(
            SEVERITY_RANK[fail_on] <= SEVERITY_RANK[baseline.fail_on],
            f"{context}: fail_on cannot weaken {DEFAULT_POLICY_REF}",
        )
        _require(
            SEVERITY_RANK[exception_max] <= SEVERITY_RANK[baseline.exception_max_severity],
            f"{context}: exception_max_severity cannot weaken {DEFAULT_POLICY_REF}",
        )

    exceptions = []
    exception_ids = set()
    for entry in payload["exceptions"]:
        required = {
            "id",
            "status",
            "rule_id",
            "skill_id",
            "path",
            "finding_digest",
            "reviewer",
            "reviewed_on",
            "expires_on",
            "justification",
        }
        _require(isinstance(entry, dict) and set(entry) == required, f"{context}: invalid exception")
        exception_id = entry["id"]
        rule_id = entry["rule_id"]
        _require(
            isinstance(exception_id, str)
            and POLICY_ID_RE.fullmatch(exception_id) is not None,
            f"{context}: invalid exception id",
        )
        _require(exception_id not in exception_ids, f"{context}: duplicate exception {exception_id}")
        exception_ids.add(exception_id)
        _require(entry["status"] == "accepted", f"{context}: exception {exception_id} is not accepted")
        _require(rule_id in rule_catalog, f"{context}: exception {exception_id} has unknown rule")
        effective_severity = overrides.get(rule_id, rule_catalog[rule_id])
        _require(
            SEVERITY_RANK[effective_severity] <= SEVERITY_RANK[exception_max],
            f"{context}: exception {exception_id} exceeds exception_max_severity",
        )
        _require(
            entry["skill_id"] is None
            or (
                isinstance(entry["skill_id"], str)
                and SKILL_ID_RE.fullmatch(entry["skill_id"]) is not None
            ),
            f"{context}: invalid skill_id",
        )
        _safe_relative_path(entry["path"], f"{context}: exception {exception_id}")
        _require(
            isinstance(entry["finding_digest"], str)
            and len(entry["finding_digest"]) == 64
            and all(char in "0123456789abcdef" for char in entry["finding_digest"]),
            f"{context}: invalid finding_digest",
        )
        reviewed_on = _date(entry["reviewed_on"], f"{context}: reviewed_on")
        expires_on = _date(entry["expires_on"], f"{context}: expires_on")
        _require(reviewed_on <= expires_on, f"{context}: exception {exception_id} expires before review")
        _require(expires_on >= today, f"{context}: exception {exception_id} expired on {expires_on}")
        _require(isinstance(entry["reviewer"], str) and entry["reviewer"], f"{context}: invalid reviewer")
        _require(
            isinstance(entry["justification"], str) and entry["justification"],
            f"{context}: invalid justification",
        )
        review_digest = canonical_digest(
            {
                "reviewer": entry["reviewer"],
                "reviewed_on": entry["reviewed_on"],
                "expires_on": entry["expires_on"],
                "justification": entry["justification"],
            }
        )
        exceptions.append(
            ReviewedException(
                exception_id=exception_id,
                rule_id=rule_id,
                skill_id=entry["skill_id"],
                path=entry["path"],
                finding_digest=entry["finding_digest"],
                expires_on=entry["expires_on"],
                review_digest=review_digest,
            )
        )

    normalized = {
        "id": payload["id"],
        "version": payload["version"],
        "extends": payload["extends"],
        "enforcement": enforcement,
        "rules": sorted(rule_ids),
        "severity_overrides": sorted(overrides.items()),
        "exceptions": [
            {
                "id": item.exception_id,
                "rule_id": item.rule_id,
                "skill_id": item.skill_id,
                "path": item.path,
                "finding_digest": item.finding_digest,
                "expires_on": item.expires_on,
                "review_digest": item.review_digest,
            }
            for item in exceptions
        ],
    }
    return EffectivePolicy(
        policy_id=payload["id"],
        version=payload["version"],
        source=source,
        source_digest=canonical_digest(payload),
        effective_digest=canonical_digest(normalized),
        fail_on=fail_on,
        exception_max_severity=exception_max,
        enabled_rules=tuple(sorted(rule_ids)),
        severity_overrides=dict(sorted(overrides.items())),
        exceptions=tuple(exceptions),
    )


def load_effective_policy(
    rule_catalog: Mapping[str, str],
    policy_path: Optional[Path] = None,
    target: Optional[Path] = None,
    today: Optional[date] = None,
) -> EffectivePolicy:
    """Load the trusted baseline or a complete, strengthening external policy."""

    evaluated_on = today or date.today()
    baseline_payload = load_policy_payload(default_policy_path())
    baseline = _normalize_policy(
        baseline_payload,
        rule_catalog,
        source="packaged",
        baseline=None,
        today=evaluated_on,
    )
    if policy_path is None:
        return baseline

    resolved_policy = policy_path.expanduser().resolve()
    if target is not None:
        resolved_target = target.expanduser().resolve()
        package_root = resolved_target if resolved_target.is_dir() else resolved_target.parent
        if _inside(resolved_policy, package_root):
            raise SecurityPolicyError(
                "external security policy must not be loaded from inside the scan target"
            )
    payload = load_policy_payload(resolved_policy)
    return _normalize_policy(
        payload,
        rule_catalog,
        source="external",
        baseline=baseline,
        today=evaluated_on,
    )


def policy_receipt(policy: EffectivePolicy) -> Dict[str, Any]:
    return {
        "id": policy.policy_id,
        "version": policy.version,
        "source": policy.source,
        "source_digest": policy.source_digest,
        "effective_digest": policy.effective_digest,
        "enabled_rule_count": len(policy.enabled_rules),
        "severity_override_count": len(policy.severity_overrides),
        "exception_count": len(policy.exceptions),
    }
