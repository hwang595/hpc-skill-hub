#!/usr/bin/env python3
"""Read-only Model Context Protocol surface for HPC Skill Hub."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import __version__
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
        "query": query,
        "filters": {
            "category": category,
            "scheduler": scheduler,
            "risk": risk,
            "maturity": maturity,
            "status": status,
            "tool": tool,
            "collection": collection,
        },
        "total": len(matches),
        "returned": min(len(matches), limit),
        "truncated": len(matches) > limit,
        "max_results": MAX_SEARCH_RESULTS,
        "skills": matches[:limit],
    }


def show_skill(skill_id: str) -> Dict[str, Any]:
    """Return one skill's validated metadata and explicit safety boundary."""
    index = load_index()
    skill = find_by_id(index["skills"], skill_id)
    if skill is None:
        return error_payload("unknown-skill", f"Unknown skill: {skill_id}")
    collections = skill_collection_membership(index).get(skill_id, [])
    return {
        "ok": True,
        "skill": skill,
        "collections": collections,
        "source_mode": source_mode(),
        "content_scope": "metadata-only",
        "usage_contract": {
            "read_before_use": [skill["readme"]]
            + [example["path"] for example in skill["examples"]],
            "require_explicit_intent_for_operational_actions": True,
            "preserve_site_placeholders": True,
            "maturity_is_review_signal": skill["maturity"] == "seed",
        },
    }


def list_collections(collection_id: Optional[str] = None) -> Dict[str, Any]:
    """List registry collections or return one collection by id."""
    collections = load_index().get("collections", [])
    if collection_id:
        collection = find_by_id(collections, collection_id)
        if collection is None:
            return error_payload(
                "unknown-collection", f"Unknown collection: {collection_id}"
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
                "unknown-site-adapter", f"Unknown site adapter: {adapter_id}"
            )
        return {"ok": True, "site_adapter": adapter}
    return {"ok": True, "count": len(adapters), "site_adapters": adapters}


def resolve_site_policy(skill_id: str, adapter_id: str) -> Dict[str, Any]:
    """Resolve one skill through public site policy without inventing local values."""
    index = load_index()
    skill = find_by_id(index["skills"], skill_id)
    if skill is None:
        return error_payload("unknown-skill", f"Unknown skill: {skill_id}")
    adapter = find_by_id(index.get("site_adapters", []), adapter_id)
    if adapter is None:
        return error_payload(
            "unknown-site-adapter", f"Unknown site adapter: {adapter_id}"
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
    return {
        "ok": True,
        "server": {
            "name": SERVER_NAME,
            "version": __version__,
            "transport": "stdio",
            "source_mode": source_mode(),
            "read_only": True,
            "tools": list(TOOL_NAMES),
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
        "safety_boundary": {
            "executes_commands": False,
            "writes_files": False,
            "uses_network": False,
            "submits_jobs": False,
            "returns_unreviewed_community_content": False,
        },
    }


def create_server() -> Any:
    """Create the optional FastMCP server without importing MCP for CLI-only use."""
    try:
        from mcp.server.fastmcp import FastMCP
        from mcp.types import ToolAnnotations
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
    for tool_name, title, function in (
        ("search_skills", "Search HPC Skills", search_skills),
        ("show_skill", "Show HPC Skill", show_skill),
        ("list_collections", "List Skill Collections", list_collections),
        ("show_site_adapters", "Show Site Adapters", show_site_adapters),
        ("resolve_site_policy", "Resolve Public Site Policy", resolve_site_policy),
        ("registry_status", "Show Registry Status", registry_status),
    ):
        server.tool(
            name=tool_name,
            title=title,
            annotations=read_only,
            structured_output=True,
        )(function)
    return server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the read-only HPC Skill Hub MCP server over stdio."
    )
    parser.add_argument(
        "--root",
        help="Optional repository root; installed packages use bundled registry metadata.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.root:
        root = Path(args.root).expanduser().resolve()
        if not (root / "registry" / "index.json").is_file():
            print(f"Invalid HPC Skill Hub root: {root}", file=sys.stderr)
            return 2
        os.environ["HPC_SKILL_HUB_ROOT"] = str(root)
    try:
        server = create_server()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    server.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
