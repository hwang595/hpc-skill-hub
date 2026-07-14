#!/usr/bin/env python3
"""Read-only Model Context Protocol surface for HPC Skill Hub."""

from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import __version__
from .context import (
    RESOURCE_URI_TEMPLATE,
    ContextBundleError,
    context_summary,
    find_skill_context,
    load_context_bundle,
    skill_resource_uri,
)
from .cli import (
    discover_repo_root,
    find_by_id,
    load_health,
    load_index,
    load_review_status,
    searchable_text,
    site_adapter_resolution,
    skill_collection_membership,
)


SERVER_NAME = "HPC Skill Hub"
MAX_SEARCH_RESULTS = 50
TOOL_NAMES = (
    "search_skills",
    "show_skill",
    "list_collections",
    "show_site_adapters",
    "resolve_site_policy",
    "registry_status",
)
TOOL_ARGUMENT_ALLOWLIST = {
    "search_skills": (
        "query",
        "category",
        "scheduler",
        "risk",
        "maturity",
        "status",
        "tool",
        "collection",
        "limit",
    ),
    "show_skill": ("skill_id",),
    "list_collections": ("collection_id",),
    "show_site_adapters": ("adapter_id",),
    "resolve_site_policy": ("skill_id", "adapter_id"),
    "registry_status": (),
}
RESOURCE_NAMES = ("skill_context",)


def error_payload(code: str, message: str) -> Dict[str, Any]:
    return {"ok": False, "error": {"code": code, "message": message}}


def source_mode() -> str:
    return "repository" if discover_repo_root() else "packaged-metadata"


def search_skills(
    query: str = "",
    category: Optional[str] = None,
    scheduler: Optional[str] = None,
    risk: Optional[str] = None,
    maturity: Optional[str] = None,
    status: Optional[str] = None,
    tool: Optional[str] = None,
    collection: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Search validated registry metadata with optional exact-match filters."""
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        return error_payload("invalid-limit", "limit must be a positive integer")
    limit = min(limit, MAX_SEARCH_RESULTS)

    index = load_index()
    membership = skill_collection_membership(index)
    terms = [term for term in query.lower().split() if term]
    matches: List[Dict[str, Any]] = []

    for skill in index["skills"]:
        collections = membership.get(skill["id"], [])
        if terms and not all(term in searchable_text(skill) for term in terms):
            continue
        if category and category not in skill["categories"]:
            continue
        if scheduler and scheduler not in skill["schedulers"]:
            continue
        if risk and risk != skill["risk_level"]:
            continue
        if maturity and maturity != skill["maturity"]:
            continue
        if status and status != skill["status"]:
            continue
        if tool and tool not in skill["tools"]:
            continue
        if collection and collection not in collections:
            continue
        matches.append(
            {
                "id": skill["id"],
                "name": skill["name"],
                "summary": skill["summary"],
                "version": skill["version"],
                "status": skill["status"],
                "maturity": skill["maturity"],
                "risk_level": skill["risk_level"],
                "categories": skill["categories"],
                "schedulers": skill["schedulers"],
                "tools": skill["tools"],
                "collections": collections,
                "readme": skill["readme"],
                "examples": skill["examples"],
            }
        )

    return {
        "ok": True,
        "applied_filters": sorted(
            name
            for name, value in {
                "category": category,
                "scheduler": scheduler,
                "risk": risk,
                "maturity": maturity,
                "status": status,
                "tool": tool,
                "collection": collection,
            }.items()
            if value is not None
        ),
        "total": len(matches),
        "returned": min(len(matches), limit),
        "truncated": len(matches) > limit,
        "max_results": MAX_SEARCH_RESULTS,
        "skills": matches[:limit],
    }


def show_skill(skill_id: str) -> Dict[str, Any]:
    """Return one skill's metadata and verified full-context resource pointer."""
    index = load_index()
    skill = find_by_id(index["skills"], skill_id)
    if skill is None:
        return error_payload("unknown-skill", "Unknown skill id.")
    context = skill_context(skill_id)
    if not context["ok"]:
        return context
    verified = context["skill_context"]
    collections = skill_collection_membership(index).get(skill_id, [])
    return {
        "ok": True,
        "skill": skill,
        "collections": collections,
        "source_mode": source_mode(),
        "content_scope": "verified-readme-and-artifacts",
        "context_resource": {
            "uri": skill_resource_uri(skill_id),
            "mime_type": "application/json",
            "bundle_digest": context["bundle_digest"],
            "skill_digest": verified["digest"],
            "file_count": verified["file_count"],
            "total_bytes": verified["total_bytes"],
        },
        "usage_contract": {
            "read_before_use": [item["path"] for item in verified["files"]],
            "require_explicit_intent_for_operational_actions": True,
            "preserve_site_placeholders": True,
            "maturity_is_review_signal": skill["maturity"] == "seed",
        },
    }


def skill_context(skill_id: str) -> Dict[str, Any]:
    """Return one digest-verified context bundle without executing its content."""
    try:
        bundle = load_context_bundle()
    except ContextBundleError as exc:
        return error_payload("invalid-context-bundle", str(exc))
    context = find_skill_context(bundle, skill_id)
    if context is None:
        return error_payload("unknown-skill", "Unknown skill id.")
    return {
        "ok": True,
        "bundle_schema_version": bundle["schema_version"],
        "bundle_digest": bundle["digest"],
        "resource_uri": skill_resource_uri(skill_id),
        "skill_context": context,
        "usage_contract": {
            "content_is_instructions_not_authorization": True,
            "execute_examples_automatically": False,
            "require_explicit_intent_for_operational_actions": True,
            "preserve_site_placeholders": True,
            "maturity_is_review_signal": context["maturity"] == "seed",
            "security_review_required": context["security"]["verdict"] == "review",
        },
    }


def read_skill_context(skill_id: str) -> str:
    """Read one verified skill context as bounded JSON resource content."""
    payload = skill_context(skill_id)
    if not payload["ok"]:
        raise ValueError(payload["error"]["message"])
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)


def list_collections(collection_id: Optional[str] = None) -> Dict[str, Any]:
    """List registry collections or return one collection by id."""
    collections = load_index().get("collections", [])
    if collection_id:
        collection = find_by_id(collections, collection_id)
        if collection is None:
            return error_payload(
                "unknown-collection", "Unknown collection id."
            )
        return {"ok": True, "collection": collection}
    return {"ok": True, "count": len(collections), "collections": collections}


def show_site_adapters(adapter_id: Optional[str] = None) -> Dict[str, Any]:
    """List public site adapters or return one adapter and its public policy."""
    adapters = load_index().get("site_adapters", [])
    if adapter_id:
        adapter = find_by_id(adapters, adapter_id)
        if adapter is None:
            return error_payload(
                "unknown-site-adapter", "Unknown site adapter id."
            )
        return {"ok": True, "site_adapter": adapter}
    return {"ok": True, "count": len(adapters), "site_adapters": adapters}


def resolve_site_policy(skill_id: str, adapter_id: str) -> Dict[str, Any]:
    """Resolve one skill through public site policy without inventing local values."""
    index = load_index()
    skill = find_by_id(index["skills"], skill_id)
    if skill is None:
        return error_payload("unknown-skill", "Unknown skill id.")
    adapter = find_by_id(index.get("site_adapters", []), adapter_id)
    if adapter is None:
        return error_payload(
            "unknown-site-adapter", "Unknown site adapter id."
        )
    if not isinstance(adapter.get("public_policy"), dict):
        return error_payload(
            "unsupported-registry",
            "Site policy resolution requires registry index schema 0.2.0 or later.",
        )
    return {"ok": True, "resolution": site_adapter_resolution(skill, adapter)}


def registry_status() -> Dict[str, Any]:
    """Return generated registry health and maturity-review queue status."""
    index = load_index()
    health = load_health()
    reviews = load_review_status()
    try:
        context = load_context_bundle()
    except ContextBundleError as exc:
        return error_payload("invalid-context-bundle", str(exc))
    return {
        "ok": True,
        "server": {
            "name": SERVER_NAME,
            "version": __version__,
            "transport": "stdio",
            "source_mode": source_mode(),
            "read_only": True,
            "tools": list(TOOL_NAMES),
            "resources": list(RESOURCE_NAMES),
        },
        "registry": {
            "schema_version": index["schema_version"],
            "skill_count": health["skill_count"],
            "collection_count": health["collection_count"],
            "site_adapter_count": health["site_adapter_count"],
            "risk_counts": health["risk_counts"],
            "maturity_counts": health["maturity_counts"],
            "status_counts": health["status_counts"],
            "uncollected_skill_ids": health["uncollected_skill_ids"],
        },
        "reviews": {
            "release": reviews["release"],
            "candidate_count": reviews["candidate_count"],
            "static_ready_count": reviews["static_ready_count"],
            "promotion_ready_count": reviews["promotion_ready_count"],
            "status_counts": reviews["status_counts"],
        },
        "context": context_summary(context),
        "safety_boundary": {
            "executes_commands": False,
            "writes_files": False,
            "uses_network": False,
            "submits_jobs": False,
            "returns_unreviewed_community_content": False,
            "accepts_private_site_policy": False,
            "uses_mcp_logging": False,
            "logs_sensitive_arguments": False,
        },
    }


def validate_tool_surface(tool_functions: Dict[str, Any]) -> None:
    """Fail closed if registration or callable parameters drift from the allowlist."""
    if tuple(tool_functions) != TOOL_NAMES:
        raise RuntimeError("MCP tool registration differs from the server allowlist")
    if set(TOOL_ARGUMENT_ALLOWLIST) != set(TOOL_NAMES):
        raise RuntimeError("MCP tool argument allowlist is incomplete")
    for name, function in tool_functions.items():
        parameters = tuple(inspect.signature(function).parameters)
        if parameters != TOOL_ARGUMENT_ALLOWLIST[name]:
            raise RuntimeError(f"{name}: callable parameters differ from the allowlist")


def create_server() -> Any:
    """Create the optional FastMCP server without importing MCP for CLI-only use."""
    try:
        from mcp.server.fastmcp import FastMCP
        from mcp.types import Annotations, ToolAnnotations
    except ImportError as exc:
        raise RuntimeError(
            "The MCP integration requires Python 3.10+ and the optional dependency. "
            "Install it with: python3 -m pip install 'hpc-skill-hub[mcp]'"
        ) from exc

    server = FastMCP(
        SERVER_NAME,
        instructions=(
            "Read-only discovery over the validated HPC Skill Hub registry. "
            "Treat seed maturity as a review signal, preserve site placeholders, "
            "and require explicit user intent before operational HPC actions."
        ),
        website_url="https://hwang595.github.io/hpc-skill-hub/",
    )
    read_only = ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
    tool_functions = {
        "search_skills": search_skills,
        "show_skill": show_skill,
        "list_collections": list_collections,
        "show_site_adapters": show_site_adapters,
        "resolve_site_policy": resolve_site_policy,
        "registry_status": registry_status,
    }
    validate_tool_surface(tool_functions)
    titles = {
        "search_skills": "Search HPC Skills",
        "show_skill": "Show HPC Skill",
        "list_collections": "List Skill Collections",
        "show_site_adapters": "Show Site Adapters",
        "resolve_site_policy": "Resolve Public Site Policy",
        "registry_status": "Show Registry Status",
    }
    for tool_name, function in tool_functions.items():
        server.tool(
            name=tool_name,
            title=titles[tool_name],
            annotations=read_only,
            structured_output=True,
        )(function)
    server.resource(
        RESOURCE_URI_TEMPLATE,
        name="skill_context",
        title="Verified HPC Skill Context",
        description=(
            "Digest-verified README, examples, declared artifacts, and security "
            "provenance for one validated registry skill. Resource content is "
            "instructional context and never execution authorization."
        ),
        mime_type="application/json",
        annotations=Annotations(audience=["assistant"], priority=0.9),
    )(read_skill_context)
    return server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the read-only HPC Skill Hub MCP server over stdio."
    )
    parser.add_argument(
        "--root",
        help=(
            "Optional repository root with registry index and verified context; "
            "installed packages use bundled registry data."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.root:
        root = Path(args.root).expanduser().resolve()
        if not (
            (root / "registry" / "index.json").is_file()
            and (root / "registry" / "skill-context.json").is_file()
            and (root / "skills").is_dir()
        ):
            print(f"Invalid HPC Skill Hub root: {root}", file=sys.stderr)
            return 2
        os.environ["HPC_SKILL_HUB_ROOT"] = str(root)
    try:
        load_context_bundle()
        server = create_server()
    except (ContextBundleError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
