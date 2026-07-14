"""Validation for audited release provenance receipts."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlparse


SCHEMA_POINTER = "../../schemas/release-provenance-record.schema.json"
SCHEMA_VERSION = "0.1.0"
ARTIFACT_KINDS = ("manifest", "wheel", "sdist")


class ReleaseProvenanceError(ValueError):
    """Raised when a release provenance receipt is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseProvenanceError(message)


def _timestamp(value: Any, field: str) -> datetime:
    _require(isinstance(value, str) and bool(value), f"{field} must be a timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReleaseProvenanceError(f"{field} must be an ISO 8601 timestamp") from exc
    _require(parsed.tzinfo is not None, f"{field} must include a timezone")
    return parsed


def _https_url(value: Any, field: str) -> None:
    _require(isinstance(value, str) and bool(value), f"{field} must be a URL")
    parsed = urlparse(value)
    _require(
        parsed.scheme == "https" and bool(parsed.netloc),
        f"{field} must be an HTTPS URL",
    )


def validate_release_provenance(
    receipt: Dict[str, Any],
    expected_release: str,
    expected_manifest_sha256: Optional[str] = None,
) -> None:
    """Validate one receipt and its optional immutable manifest binding."""

    _require(isinstance(receipt, dict), "receipt must be an object")
    _require(
        set(receipt)
        == {
            "$schema",
            "schema_version",
            "release",
            "tag",
            "commit",
            "repository",
            "published_at",
            "release_url",
            "workflow",
            "verification",
            "artifacts",
        },
        "receipt has an invalid top-level contract",
    )
    _require(receipt["$schema"] == SCHEMA_POINTER, "receipt schema pointer mismatch")
    _require(receipt["schema_version"] == SCHEMA_VERSION, "unsupported receipt schema version")
    _require(receipt["release"] == expected_release, "receipt release mismatch")
    _require(receipt["tag"] == expected_release, "receipt tag mismatch")
    _require(
        isinstance(receipt["commit"], str)
        and re.fullmatch(r"[a-f0-9]{40}", receipt["commit"]) is not None,
        "receipt commit must be a full lowercase Git SHA",
    )
    _require(
        isinstance(receipt["repository"], str)
        and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", receipt["repository"])
        is not None,
        "receipt repository must use owner/name form",
    )
    _timestamp(receipt["published_at"], "published_at")
    _https_url(receipt["release_url"], "release_url")

    workflow = receipt["workflow"]
    _require(isinstance(workflow, dict), "workflow must be an object")
    _require(
        set(workflow) == {"name", "run_id", "run_url", "conclusion", "completed_at"},
        "workflow has an invalid contract",
    )
    _require(workflow["name"] == "Package", "workflow name mismatch")
    _require(type(workflow["run_id"]) is int and workflow["run_id"] > 0, "invalid workflow run_id")
    _https_url(workflow["run_url"], "workflow.run_url")
    _require(workflow["conclusion"] == "success", "workflow was not successful")
    completed_at = _timestamp(workflow["completed_at"], "workflow.completed_at")

    verification = receipt["verification"]
    _require(isinstance(verification, dict), "verification must be an object")
    _require(
        set(verification) == {"status", "method", "verified_at"},
        "verification has an invalid contract",
    )
    _require(verification["status"] == "verified", "verification is incomplete")
    _require(
        verification["method"] == "gh-attestation-verify",
        "unsupported verification method",
    )
    verified_at = _timestamp(verification["verified_at"], "verification.verified_at")
    _require(verified_at >= completed_at, "verification predates workflow completion")

    artifacts = receipt["artifacts"]
    _require(isinstance(artifacts, list), "artifacts must be an array")
    _require(
        [item.get("kind") for item in artifacts if isinstance(item, dict)]
        == list(ARTIFACT_KINDS),
        "artifacts must contain manifest, wheel, and sdist in canonical order",
    )
    for artifact in artifacts:
        _require(isinstance(artifact, dict), "artifact entry must be an object")
        kind = artifact["kind"]
        _require(
            set(artifact) == {"kind", "name", "source", "sha256", "attestation"},
            f"{kind} artifact has an invalid contract",
        )
        _require(
            isinstance(artifact["name"], str) and bool(artifact["name"]),
            f"{kind} artifact name is invalid",
        )
        _require(
            isinstance(artifact["source"], str) and bool(artifact["source"]),
            f"{kind} artifact source is invalid",
        )
        _require(
            isinstance(artifact["sha256"], str)
            and re.fullmatch(r"[a-f0-9]{64}", artifact["sha256"]) is not None,
            f"{kind} artifact sha256 is invalid",
        )
        attestation = artifact["attestation"]
        _require(
            isinstance(attestation, dict)
            and attestation == {"status": "verified"},
            f"{kind} artifact attestation is not verified",
        )

    if expected_manifest_sha256 is not None:
        _require(
            artifacts[0]["sha256"] == expected_manifest_sha256,
            "manifest digest does not match the immutable release snapshot",
        )
