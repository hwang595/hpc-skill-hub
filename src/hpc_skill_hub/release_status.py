"""Load and validate the packaged release capability status."""

from __future__ import annotations

import importlib.resources as resources
import json
from pathlib import Path
from typing import Any, Dict

from . import __version__
from .cli import discover_repo_root


RELEASE_STATUS_SCHEMA_VERSION = "0.1.0"
RELEASE_STATUS_FILENAME = "release-status.json"
CAPABILITY_IDS = {
    "compatibility",
    "context_bundle",
    "mcp",
    "benchmark",
    "community_pilot",
    "review",
    "security",
}
GATE_IDS = {
    "repository",
    "community_intake_pilot",
    "comparative_evidence",
    "maturity_promotion",
    "release_provenance",
}


class ReleaseStatusError(ValueError):
    """Raised when release status is missing or violates its runtime contract."""


def _status_path() -> Any:
    root = discover_repo_root()
    if root:
        return root / "registry" / RELEASE_STATUS_FILENAME
    return resources.files("hpc_skill_hub").joinpath(
        "data", "registry", RELEASE_STATUS_FILENAME
    )


def validate_release_status(payload: Dict[str, Any]) -> None:
    if payload.get("$schema") != "../schemas/release-status.schema.json":
        raise ReleaseStatusError("release status schema pointer mismatch")
    if payload.get("schema_version") != RELEASE_STATUS_SCHEMA_VERSION:
        raise ReleaseStatusError("unsupported release status schema version")
    if payload.get("generated_by") != "tools/build_release_status.py":
        raise ReleaseStatusError("release status generator mismatch")
    if payload.get("package_version") != __version__:
        raise ReleaseStatusError("release status package version mismatch")
    if payload.get("release") != f"v{__version__}":
        raise ReleaseStatusError("release status release version mismatch")
    capabilities = payload.get("capabilities")
    if not isinstance(capabilities, dict) or set(capabilities) != CAPABILITY_IDS:
        raise ReleaseStatusError("release status capability set mismatch")
    gates = payload.get("gates")
    if not isinstance(gates, dict) or set(gates) != GATE_IDS:
        raise ReleaseStatusError("release status gate set mismatch")
    repository_ready = payload.get("repository_capability_ready")
    external_ready = payload.get("external_evidence_ready")
    if not isinstance(repository_ready, bool) or not isinstance(external_ready, bool):
        raise ReleaseStatusError("release status readiness flags must be boolean")
    if repository_ready != (gates["repository"].get("status") == "open"):
        raise ReleaseStatusError("repository readiness differs from its gate")
    pilot = capabilities["community_pilot"]
    if (pilot.get("status") == "ready") != (
        gates["community_intake_pilot"].get("status") == "open"
    ):
        raise ReleaseStatusError("community pilot capability differs from its gate")
    if pilot.get("synthetic_only") is not True or pilot.get(
        "external_evidence_claimed"
    ) is not False:
        raise ReleaseStatusError("community pilot overclaims external evidence")
    expected_external = all(
        gates[gate_id].get("status") == "open"
        for gate_id in ("comparative_evidence", "maturity_promotion")
    )
    if external_ready != expected_external:
        raise ReleaseStatusError("external evidence readiness differs from its gates")


def load_release_status() -> Dict[str, Any]:
    path = _status_path()
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ReleaseStatusError(f"release status could not be loaded: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReleaseStatusError("release status root must be an object")
    validate_release_status(payload)
    return payload
