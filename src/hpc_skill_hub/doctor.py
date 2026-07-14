"""Installed-runtime diagnostics for HPC Skill Hub and its MCP integration."""

from __future__ import annotations

import asyncio
import importlib.metadata as metadata
import importlib.resources as resources
import json
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from . import __version__
from .cli import discover_repo_root, load_health, load_index, load_review_status
from .client_contract import (
    CONTRACT_FILENAME,
    ClientContractError,
    contract_source_mode,
    load_client_contract,
)
from .context import ContextBundleError, context_summary, load_context_bundle
from .mcp_server import (
    RESOURCE_NAMES,
    TOOL_ARGUMENT_ALLOWLIST,
    TOOL_NAMES,
    create_server,
    skill_resource_uri,
)
from .release_status import ReleaseStatusError, load_release_status
from .release_provenance import ReleaseProvenanceError, validate_release_provenance
from .security import RULE_CATALOG
from .security_policy import SecurityPolicyError, load_effective_policy


DOCTOR_SCHEMA_VERSION = "0.1.0"
CORE_MINIMUM = (3, 9)
MCP_PYTHON_MINIMUM = (3, 10)
MCP_MINIMUM = (1, 27)
MCP_MAXIMUM_MAJOR = 2
REGISTRY_SCHEMA_VERSION = "0.2.0"
PROBE_SKILL_ID = "slurm-submit-job"
REGISTRY_DATA_FILES = (
    "index.json",
    "health.json",
    "release-provenance.json",
    "release-status.json",
    "review-status.json",
    "skill-context.json",
)
SECURITY_POLICY_FILENAME = "community-default.json"


@dataclass(frozen=True)
class DoctorCheck:
    id: str
    status: str
    summary: str
    details: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "summary": self.summary,
            "details": self.details,
        }


def passed(check_id: str, summary: str, **details: Any) -> DoctorCheck:
    return DoctorCheck(check_id, "pass", summary, details)


def warned(check_id: str, summary: str, **details: Any) -> DoctorCheck:
    return DoctorCheck(check_id, "warn", summary, details)


def failed(check_id: str, summary: str, **details: Any) -> DoctorCheck:
    return DoctorCheck(check_id, "fail", summary, details)


def _check_python() -> DoctorCheck:
    version = ".".join(str(part) for part in sys.version_info[:3])
    details = {
        "version": version,
        "executable": sys.executable,
        "minimum": ".".join(str(part) for part in CORE_MINIMUM),
    }
    if sys.version_info[:2] < CORE_MINIMUM:
        return failed("python", "Python is older than the core minimum", **details)
    return passed("python", "Python satisfies the core runtime contract", **details)


def _check_package_version() -> DoctorCheck:
    try:
        installed = metadata.version("hpc-skill-hub")
    except metadata.PackageNotFoundError:
        return warned(
            "package-version",
            "Distribution metadata is unavailable in this source-only runtime",
            module_version=__version__,
        )
    details = {"module_version": __version__, "distribution_version": installed}
    if installed != __version__:
        if discover_repo_root():
            return warned(
                "package-version",
                "Source checkout differs from the installed distribution",
                source_mode="repository",
                **details,
            )
        return failed(
            "package-version",
            "Module and distribution versions do not match",
            source_mode="packaged",
            **details,
        )
    return passed("package-version", "Package version metadata is consistent", **details)


def _packaged_path(*parts: str) -> Any:
    return resources.files("hpc_skill_hub").joinpath("data", *parts)


def _check_package_data() -> DoctorCheck:
    packaged: Dict[str, int] = {}
    errors: List[str] = []
    for filename in REGISTRY_DATA_FILES:
        relative = f"registry/{filename}"
        try:
            raw = _packaged_path("registry", filename).read_bytes()
            payload = json.loads(raw.decode("utf-8"))
            if filename == "release-provenance.json":
                validate_release_provenance(payload, f"v{__version__}")
            packaged[relative] = len(raw)
        except (
            FileNotFoundError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            ReleaseProvenanceError,
        ) as exc:
            errors.append(f"{relative}: {exc}")
    contract_relative = f"integrations/{CONTRACT_FILENAME}"
    try:
        raw = _packaged_path("integrations", CONTRACT_FILENAME).read_bytes()
        json.loads(raw.decode("utf-8"))
        packaged[contract_relative] = len(raw)
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{contract_relative}: {exc}")
    policy_relative = f"security/{SECURITY_POLICY_FILENAME}"
    try:
        raw = _packaged_path("security", SECURITY_POLICY_FILENAME).read_bytes()
        json.loads(raw.decode("utf-8"))
        packaged[policy_relative] = len(raw)
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{policy_relative}: {exc}")

    repository_root = discover_repo_root()
    stale: List[str] = []
    if repository_root:
        for filename in REGISTRY_DATA_FILES:
            source = (
                repository_root / "registry" / "provenance" / f"v{__version__}.json"
                if filename == "release-provenance.json"
                else repository_root / "registry" / filename
            )
            packaged_path = _packaged_path("registry", filename)
            if not source.is_file():
                stale.append(f"registry/{filename} (source missing)")
            elif packaged_path.is_file() and source.read_bytes() != packaged_path.read_bytes():
                stale.append(f"registry/{filename}")
        source = repository_root / "integrations" / CONTRACT_FILENAME
        packaged_path = _packaged_path("integrations", CONTRACT_FILENAME)
        if not source.is_file():
            stale.append(f"{contract_relative} (source missing)")
        elif packaged_path.is_file() and source.read_bytes() != packaged_path.read_bytes():
            stale.append(contract_relative)
        source = repository_root / "security" / "policies" / SECURITY_POLICY_FILENAME
        packaged_path = _packaged_path("security", SECURITY_POLICY_FILENAME)
        if not source.is_file():
            stale.append(f"{policy_relative} (source missing)")
        elif packaged_path.is_file() and source.read_bytes() != packaged_path.read_bytes():
            stale.append(policy_relative)

    if errors or stale:
        return failed(
            "package-data",
            "Packaged runtime data is missing, invalid, or stale",
            files=packaged,
            errors=errors,
            stale=stale,
        )
    return passed(
        "package-data",
        f"{len(packaged)} packaged JSON artifacts are available",
        files=packaged,
        repository_snapshot_match=repository_root is not None,
    )


def _check_registry() -> DoctorCheck:
    try:
        index = load_index()
        health = load_health()
        reviews = load_review_status()
    except (Exception, SystemExit) as exc:
        return failed("registry", "Registry metadata could not be loaded", error=str(exc))

    if not all(isinstance(item, dict) for item in (index, health, reviews)):
        return failed("registry", "Registry metadata roots must be JSON objects")

    errors = []
    if index.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        errors.append("registry schema_version mismatch")
    for field in ("skill_count", "collection_count", "site_adapter_count"):
        if index.get(field) != health.get(field):
            errors.append(f"{field} differs between index and health")
    skills = index.get("skills")
    if not isinstance(skills, list):
        errors.append("index skills must be an array")
    elif index.get("skill_count") != len(skills):
        errors.append("skill_count does not match index skills")
    review_skills = reviews.get("skills")
    if not isinstance(review_skills, list):
        errors.append("review skills must be an array")
    elif reviews.get("candidate_count") != len(review_skills):
        errors.append("review candidate_count does not match review skills")

    details = {
        "schema_version": index.get("schema_version"),
        "skill_count": index.get("skill_count"),
        "collection_count": index.get("collection_count"),
        "site_adapter_count": index.get("site_adapter_count"),
        "review_release": reviews.get("release"),
    }
    if errors:
        return failed("registry", "Registry metadata is inconsistent", errors=errors, **details)
    return passed("registry", "Registry metadata and counts are consistent", **details)


def _check_release_status() -> DoctorCheck:
    try:
        status = load_release_status()
    except (ReleaseStatusError, OSError) as exc:
        return failed(
            "release-status",
            "Generated release capability status failed closed",
            error=str(exc),
        )
    capabilities = status["capabilities"]
    gates = status["gates"]
    return passed(
        "release-status",
        "Release capability artifact matches the installed package",
        release=status["release"],
        repository_capability_ready=status["repository_capability_ready"],
        external_evidence_ready=status["external_evidence_ready"],
        capability_statuses={
            name: capability["status"] for name, capability in capabilities.items()
        },
        gate_statuses={name: gate["status"] for name, gate in gates.items()},
    )


def _check_security_policy() -> DoctorCheck:
    try:
        policy = load_effective_policy(RULE_CATALOG)
    except (SecurityPolicyError, OSError) as exc:
        return failed(
            "security-policy",
            "Packaged trust policy failed closed",
            error=str(exc),
        )
    return passed(
        "security-policy",
        "Versioned trust policy matches the scanner rule catalog",
        policy_id=policy.policy_id,
        version=policy.version,
        source=policy.source,
        effective_digest=policy.effective_digest,
        fail_on=policy.fail_on,
        enabled_rule_count=len(policy.enabled_rules),
        severity_override_count=len(policy.severity_overrides),
        exception_count=len(policy.exceptions),
    )


def _check_context() -> DoctorCheck:
    try:
        bundle = load_context_bundle()
    except (ContextBundleError, OSError) as exc:
        return failed(
            "context-digests",
            "Verified skill context failed closed",
            error=str(exc),
        )
    summary = context_summary(bundle)
    return passed(
        "context-digests",
        "All file, skill, bundle, and source-index digests are valid",
        **summary,
    )


def _check_contract() -> DoctorCheck:
    try:
        contract = load_client_contract()
        source_mode = contract_source_mode()
    except (ClientContractError, OSError) as exc:
        return failed(
            "client-contract",
            "Canonical MCP client contract is invalid",
            error=str(exc),
        )

    server = contract["server"]
    resources_by_name = {item["name"]: item for item in server["resources"]}
    errors = []
    if tuple(server["tools"]) != TOOL_NAMES:
        errors.append("contract tools differ from the server allowlist")
    contract_arguments = {
        name: tuple(arguments)
        for name, arguments in server["tool_arguments"].items()
    }
    if contract_arguments != TOOL_ARGUMENT_ALLOWLIST:
        errors.append("contract tool arguments differ from the server allowlist")
    if server["registry_schema_version"] != REGISTRY_SCHEMA_VERSION:
        errors.append("contract registry schema differs from the runtime contract")
    if tuple(resources_by_name) != RESOURCE_NAMES:
        errors.append("contract resources differ from the server allowlist")
    skill_context = resources_by_name.get("skill_context", {})
    if skill_context.get("uri_template") != "hpc-skill://skills/{skill_id}":
        errors.append("skill context URI template mismatch")

    details = {
        "schema_version": contract["schema_version"],
        "source_mode": source_mode,
        "server_id": server["id"],
        "tools": server["tools"],
        "tool_arguments": server["tool_arguments"],
        "resources": list(resources_by_name),
        "providers": sorted(contract["providers"]),
    }
    if errors:
        return failed(
            "client-contract",
            "Canonical contract and runtime capability allowlists differ",
            errors=errors,
            **details,
        )
    return passed(
        "client-contract",
        "Canonical client contract matches the runtime capability allowlists",
        **details,
    )


def _parse_release(value: str) -> Optional[Tuple[int, int, int]]:
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?", value)
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())


def _check_mcp_dependency(require_mcp: bool) -> DoctorCheck:
    required_status = failed if require_mcp else warned
    if sys.version_info[:2] < MCP_PYTHON_MINIMUM:
        return required_status(
            "mcp-dependency",
            "Optional MCP integration requires Python 3.10 or later",
            python_version=".".join(str(part) for part in sys.version_info[:3]),
            required=require_mcp,
        )
    try:
        version = metadata.version("mcp")
    except metadata.PackageNotFoundError:
        return required_status(
            "mcp-dependency",
            "Optional MCP SDK is not installed",
            requirement="mcp>=1.27,<2",
            required=require_mcp,
        )
    parsed = _parse_release(version)
    if parsed is None or parsed[:2] < MCP_MINIMUM or parsed[0] >= MCP_MAXIMUM_MAJOR:
        return failed(
            "mcp-dependency",
            "Installed MCP SDK is outside the supported stable v1 range",
            version=version,
            requirement="mcp>=1.27,<2",
            required=require_mcp,
        )
    try:
        import mcp  # noqa: F401
    except ImportError as exc:
        return failed(
            "mcp-dependency",
            "MCP distribution metadata exists but the module cannot be imported",
            version=version,
            error=str(exc),
        )
    return passed(
        "mcp-dependency",
        "Optional MCP SDK is installed and supported",
        version=version,
        requirement="mcp>=1.27,<2",
        required=require_mcp,
    )


async def _protocol_probe() -> Dict[str, Any]:
    from mcp.shared.memory import create_connected_server_and_client_session
    from pydantic import AnyUrl

    server = create_server()
    async with create_connected_server_and_client_session(
        server, raise_exceptions=True
    ) as session:
        listed = await session.list_tools()
        tools = {tool.name: tool for tool in listed.tools}
        if set(tools) != set(TOOL_NAMES):
            raise RuntimeError("protocol tool names differ from the server allowlist")
        for name, tool in tools.items():
            annotations = tool.annotations
            if annotations is None:
                raise RuntimeError(f"{name}: protocol annotations are missing")
            if not (
                annotations.readOnlyHint
                and not annotations.destructiveHint
                and annotations.idempotentHint
                and not annotations.openWorldHint
            ):
                raise RuntimeError(f"{name}: protocol annotations are not read-only")
            properties = tool.inputSchema.get("properties", {})
            if set(properties) != set(TOOL_ARGUMENT_ALLOWLIST[name]):
                raise RuntimeError(f"{name}: protocol arguments differ from the allowlist")

        templates = await session.list_resource_templates()
        by_name = {item.name: item for item in templates.resourceTemplates}
        if set(by_name) != set(RESOURCE_NAMES):
            raise RuntimeError("protocol resource names differ from the server allowlist")

        status_result = await session.call_tool("registry_status", {})
        if status_result.isError:
            raise RuntimeError("registry_status returned a protocol error")
        status = status_result.structuredContent["result"]
        if status["server"]["tools"] != list(TOOL_NAMES):
            raise RuntimeError("registry_status tool allowlist mismatch")

        resource = await session.read_resource(
            AnyUrl(skill_resource_uri(PROBE_SKILL_ID))
        )
        payload = json.loads(resource.contents[0].text)
        context = payload.get("skill_context", {})
        if not payload.get("ok") or context.get("id") != PROBE_SKILL_ID:
            raise RuntimeError("verified context resource probe failed")
        if not context.get("files"):
            raise RuntimeError("verified context resource returned no files")

        return {
            "tools": sorted(tools),
            "tool_arguments": {
                name: list(TOOL_ARGUMENT_ALLOWLIST[name]) for name in sorted(tools)
            },
            "resources": sorted(by_name),
            "probe_skill_id": PROBE_SKILL_ID,
            "probe_file_count": context["file_count"],
            "probe_total_bytes": context["total_bytes"],
        }


def _check_mcp_protocol(dependency: DoctorCheck, require_mcp: bool) -> DoctorCheck:
    if dependency.status != "pass":
        status = "fail" if require_mcp or dependency.status == "fail" else "warn"
        return DoctorCheck(
            "mcp-protocol",
            status,
            "In-memory MCP protocol probe was not run",
            {"dependency_status": dependency.status, "required": require_mcp},
        )
    try:
        details = asyncio.run(_protocol_probe())
    except Exception as exc:
        return failed(
            "mcp-protocol",
            "In-memory MCP protocol and context-resource probe failed",
            error=str(exc),
        )
    return passed(
        "mcp-protocol",
        "Exact read-only tool and verified-resource surface passed in memory",
        **details,
    )


def doctor_report(require_mcp: bool = False) -> Dict[str, Any]:
    checks = [
        _check_python(),
        _check_package_version(),
        _check_package_data(),
        _check_security_policy(),
        _check_registry(),
        _check_release_status(),
        _check_context(),
        _check_contract(),
    ]
    dependency = _check_mcp_dependency(require_mcp)
    checks.append(dependency)
    checks.append(_check_mcp_protocol(dependency, require_mcp))

    counts = {
        status: sum(check.status == status for check in checks)
        for status in ("pass", "warn", "fail")
    }
    status = "fail" if counts["fail"] else "warn" if counts["warn"] else "pass"
    return {
        "schema_version": DOCTOR_SCHEMA_VERSION,
        "ok": counts["fail"] == 0,
        "status": status,
        "source_mode": "repository" if discover_repo_root() else "packaged",
        "require_mcp": require_mcp,
        "summary": counts,
        "checks": [check.as_dict() for check in checks],
    }


def doctor_text(report: Dict[str, Any]) -> str:
    lines = [f"HPC Skill Hub doctor: {report['status'].upper()}"]
    for check in report["checks"]:
        lines.append(
            f"[{check['status'].upper():4}] {check['id']}: {check['summary']}"
        )
    summary = report["summary"]
    lines.append(
        "Summary: "
        f"{summary['pass']} passed, {summary['warn']} warning(s), "
        f"{summary['fail']} failed."
    )
    return "\n".join(lines)
