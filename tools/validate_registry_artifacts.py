#!/usr/bin/env python3
"""Validate generated registry artifacts and their public contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.context import (  # noqa: E402
    ContextBundleError,
    verify_context_bundle,
)
from hpc_skill_hub.community_pilot import (  # noqa: E402
    CommunityPilotError,
    validate_pilot_report,
)
from hpc_skill_hub.client_contract import (  # noqa: E402
    ClientContractError,
    validate_client_contract,
)
from hpc_skill_hub.security import RULE_CATALOG  # noqa: E402
from hpc_skill_hub.security_policy import (  # noqa: E402
    SecurityPolicyError,
    load_effective_policy,
)
from hpc_skill_hub.release_status import (  # noqa: E402
    ReleaseStatusError,
    validate_release_status,
)
from hpc_skill_hub.release_provenance import (  # noqa: E402
    ReleaseProvenanceError,
    validate_release_provenance as validate_release_provenance_record,
)

INDEX_JSON = ROOT / "registry" / "index.json"
HEALTH_JSON = ROOT / "registry" / "health.json"
QUALITY_JSON = ROOT / "registry" / "skill-quality.json"
REVIEW_STATUS_JSON = ROOT / "registry" / "review-status.json"
RELEASE_STATUS_JSON = ROOT / "registry" / "release-status.json"
COMMUNITY_PILOT_JSON = ROOT / "registry" / "community-pilot-v0.6.0.json"
RELEASE_PROVENANCE_JSON = ROOT / "registry" / "provenance" / "v0.6.0.json"
CONTEXT_JSON = ROOT / "registry" / "skill-context.json"
MCP_CLIENT_JSON = ROOT / "integrations" / "mcp-client.json"
SECURITY_POLICY_JSON = ROOT / "security" / "policies" / "community-default.json"
RELEASE_DIR = ROOT / "registry" / "releases"
PACKAGE_DATA_DIR = ROOT / "src" / "hpc_skill_hub" / "data" / "registry"
PACKAGE_INTEGRATION_DIR = ROOT / "src" / "hpc_skill_hub" / "data" / "integrations"
PACKAGE_SECURITY_DIR = ROOT / "src" / "hpc_skill_hub" / "data" / "security"
SCHEMAS = {
    "agent-benchmark-plan": ROOT / "schemas" / "agent-benchmark-plan.schema.json",
    "agent-benchmark-result": ROOT / "schemas" / "agent-benchmark-result.schema.json",
    "agent-benchmark-review": ROOT / "schemas" / "agent-benchmark-review.schema.json",
    "agent-benchmark-review-packet": ROOT / "schemas" / "agent-benchmark-review-packet.schema.json",
    "agent-benchmark-reconciliation": ROOT / "schemas" / "agent-benchmark-reconciliation.schema.json",
    "agent-benchmark-task": ROOT / "schemas" / "agent-benchmark-task.schema.json",
    "benchmark": ROOT / "schemas" / "benchmark.schema.json",
    "community-skill-intake-report": ROOT / "schemas" / "community-skill-intake-report.schema.json",
    "community-skill-context-bundle": ROOT / "schemas" / "community-skill-context-bundle.schema.json",
    "community-pilot-report": ROOT / "schemas" / "community-pilot-report.schema.json",
    "index": ROOT / "schemas" / "registry-index.schema.json",
    "health": ROOT / "schemas" / "registry-health.schema.json",
    "mcp-client-contract": ROOT / "schemas" / "mcp-client-contract.schema.json",
    "release": ROOT / "schemas" / "release-manifest.schema.json",
    "release-provenance-record": ROOT / "schemas" / "release-provenance-record.schema.json",
    "release-status": ROOT / "schemas" / "release-status.schema.json",
    "skill-security-report": ROOT / "schemas" / "skill-security-report.schema.json",
    "skill-security-policy": ROOT / "schemas" / "skill-security-policy.schema.json",
    "skill-context-bundle": ROOT / "schemas" / "skill-context-bundle.schema.json",
    "skill-quality-report": ROOT / "schemas" / "skill-quality-report.schema.json",
    "skill-review": ROOT / "schemas" / "skill-review.schema.json",
    "skill-review-status": ROOT / "schemas" / "skill-review-status.schema.json",
    "site-adapter-resolution": ROOT / "schemas" / "site-adapter-resolution.schema.json",
}
PUBLIC_BASELINE_DOCS = [
    ROOT / "CHANGELOG.md",
    ROOT / "ROADMAP.md",
    ROOT / "docs" / "COMPATIBILITY.md",
    ROOT / "docs" / "OPEN_SOURCE_PROPOSAL.md",
    ROOT / "docs" / "PUBLIC_LAUNCH_PACKET.md",
    ROOT / "docs" / "REGISTRY_HEALTH.md",
    ROOT / "docs" / "RELEASE_NOTES_v0.2.0.md",
    ROOT / "docs" / "RELEASE_NOTES_v0.3.0.md",
    ROOT / "docs" / "RELEASE_NOTES_v0.4.0.md",
    ROOT / "docs" / "RELEASE_NOTES_v0.5.0.md",
    ROOT / "docs" / "RELEASE_NOTES_v0.6.0.md",
    ROOT / "docs" / "REVIEW_PACKET_v0.2.0.md",
    ROOT / "docs" / "SKILL_CATALOG.md",
]


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def require(condition: bool, errors: List[str], message: str) -> None:
    if not condition:
        errors.append(message)


def require_keys(
    payload: Dict[str, Any], keys: Iterable[str], errors: List[str], context: str
) -> None:
    for key in keys:
        require(key in payload, errors, f"{context}: missing key {key}")


def require_schema_pointer(
    payload: Dict[str, Any], expected: str, errors: List[str], context: str
) -> None:
    require(
        payload.get("$schema") == expected,
        errors,
        f"{context}: expected $schema {expected}",
    )


def validate_index(index: Dict[str, Any], errors: List[str]) -> None:
    context = relative(INDEX_JSON)
    require_schema_pointer(index, "../schemas/registry-index.schema.json", errors, context)
    require(index.get("schema_version") == "0.2.0", errors, f"{context}: schema_version mismatch")
    require_keys(
        index,
        [
            "schema_version",
            "generated_by",
            "skill_count",
            "site_adapter_count",
            "collection_count",
            "skills",
            "site_adapters",
            "collections",
            "categories",
            "tags",
            "schedulers",
            "tools",
        ],
        errors,
        context,
    )
    require(index.get("generated_by") == "tools/build_index.py", errors, f"{context}: generated_by mismatch")

    skills = index.get("skills", [])
    adapters = index.get("site_adapters", [])
    collections = index.get("collections", [])
    require(index.get("skill_count") == len(skills), errors, f"{context}: skill_count mismatch")
    require(
        index.get("site_adapter_count") == len(adapters),
        errors,
        f"{context}: site_adapter_count mismatch",
    )
    require(
        index.get("collection_count") == len(collections),
        errors,
        f"{context}: collection_count mismatch",
    )

    skill_ids = [skill.get("id") for skill in skills]
    adapter_ids = [adapter.get("id") for adapter in adapters]
    collection_ids = [collection.get("id") for collection in collections]
    require(len(skill_ids) == len(set(skill_ids)), errors, f"{context}: duplicate skill ids")
    require(
        len(adapter_ids) == len(set(adapter_ids)),
        errors,
        f"{context}: duplicate site adapter ids",
    )
    require(
        len(collection_ids) == len(set(collection_ids)),
        errors,
        f"{context}: duplicate collection ids",
    )

    known_skills: Set[str] = {skill_id for skill_id in skill_ids if isinstance(skill_id, str)}
    for skill in skills:
        skill_context = f"{context}: skills/{skill.get('id')}"
        require_keys(
            skill,
            [
                "id",
                "name",
                "summary",
                "description",
                "version",
                "status",
                "maturity",
                "risk_level",
                "categories",
                "tags",
                "schedulers",
                "tools",
                "path",
                "readme",
                "examples",
                "references",
            ],
            errors,
            skill_context,
        )
        readme = skill.get("readme")
        if isinstance(readme, str):
            require((ROOT / readme).exists(), errors, f"{skill_context}: missing README path {readme}")
        for example in skill.get("examples", []):
            path = example.get("path")
            if isinstance(path, str):
                require((ROOT / path).exists(), errors, f"{skill_context}: missing example path {path}")

    for adapter in adapters:
        adapter_context = f"{context}: site_adapters/{adapter.get('id')}"
        public_policy = adapter.get("public_policy")
        require(
            isinstance(public_policy, dict),
            errors,
            f"{adapter_context}: missing public_policy contract",
        )
        if isinstance(public_policy, dict):
            require_keys(
                public_policy,
                [
                    "contacts",
                    "scheduler",
                    "partitions",
                    "modules",
                    "storage",
                    "policies",
                    "skill_overrides",
                ],
                errors,
                f"{adapter_context}: public_policy",
            )
        for override_id in adapter.get("skill_overrides", []):
            require(
                override_id in known_skills,
                errors,
                f"{adapter_context}: unknown skill override {override_id}",
            )
        if isinstance(public_policy, dict):
            detail_ids = [
                item.get("skill_id")
                for item in public_policy.get("skill_overrides", [])
                if isinstance(item, dict)
            ]
            require(
                detail_ids == adapter.get("skill_overrides", []),
                errors,
                f"{adapter_context}: public_policy skill overrides mismatch",
            )

    for collection in collections:
        collection_context = f"{context}: collections/{collection.get('id')}"
        for skill_id in collection.get("skill_ids", []):
            require(
                skill_id in known_skills,
                errors,
                f"{collection_context}: unknown skill id {skill_id}",
            )


def validate_health(index: Dict[str, Any], health: Dict[str, Any], errors: List[str]) -> None:
    context = relative(HEALTH_JSON)
    require_schema_pointer(health, "../schemas/registry-health.schema.json", errors, context)
    require(health.get("generated_by") == "tools/build_health.py", errors, f"{context}: generated_by mismatch")
    require(health.get("skill_count") == index.get("skill_count"), errors, f"{context}: skill_count mismatch")
    require(
        health.get("site_adapter_count") == index.get("site_adapter_count"),
        errors,
        f"{context}: site_adapter_count mismatch",
    )
    require(
        health.get("collection_count") == index.get("collection_count"),
        errors,
        f"{context}: collection_count mismatch",
    )

    skill_ids = {skill["id"] for skill in index["skills"]}
    risk_by_skill = health.get("risk_by_skill", {})
    require(set(risk_by_skill) == skill_ids, errors, f"{context}: risk_by_skill ids mismatch")
    for skill in index["skills"]:
        require(
            risk_by_skill.get(skill["id"]) == skill["risk_level"],
            errors,
            f"{context}: risk mismatch for {skill['id']}",
        )
    for collection in health.get("collection_coverage", []):
        require(
            collection.get("skill_count") == len(collection.get("skill_ids", [])),
            errors,
            f"{context}: collection coverage count mismatch for {collection.get('id')}",
        )


def validate_skill_quality(
    index: Dict[str, Any], quality: Dict[str, Any], errors: List[str]
) -> None:
    context = relative(QUALITY_JSON)
    require_schema_pointer(
        quality, "../schemas/skill-quality-report.schema.json", errors, context
    )
    require(
        quality.get("generated_by") == "tools/build_skill_quality.py",
        errors,
        f"{context}: generated_by mismatch",
    )
    skills = quality.get("skills", [])
    require(
        quality.get("skill_count") == len(skills),
        errors,
        f"{context}: skill_count mismatch",
    )
    require(
        {item.get("id") for item in skills if isinstance(item, dict)}
        == {item["id"] for item in index["skills"]},
        errors,
        f"{context}: skill ids mismatch",
    )


def validate_review_status(
    index: Dict[str, Any], review_status: Dict[str, Any], errors: List[str]
) -> None:
    context = relative(REVIEW_STATUS_JSON)
    require_schema_pointer(
        review_status, "../schemas/skill-review-status.schema.json", errors, context
    )
    require(
        review_status.get("generated_by") == "tools/build_skill_reviews.py",
        errors,
        f"{context}: generated_by mismatch",
    )
    skills = review_status.get("skills", [])
    require(
        review_status.get("candidate_count") == len(skills),
        errors,
        f"{context}: candidate_count mismatch",
    )
    known_ids = {item["id"] for item in index["skills"]}
    review_ids = [item.get("id") for item in skills if isinstance(item, dict)]
    require(len(review_ids) == len(set(review_ids)), errors, f"{context}: duplicate skill ids")
    require(set(review_ids) <= known_ids, errors, f"{context}: unknown skill ids")
    require(
        review_status.get("static_ready_count")
        == sum(bool(item.get("static_ready")) for item in skills),
        errors,
        f"{context}: static_ready_count mismatch",
    )
    require(
        review_status.get("promotion_ready_count")
        == sum(bool(item.get("promotion_ready")) for item in skills),
        errors,
        f"{context}: promotion_ready_count mismatch",
    )


def validate_context_bundle(
    index: Dict[str, Any], context_bundle: Dict[str, Any], errors: List[str]
) -> None:
    context = relative(CONTEXT_JSON)
    require_schema_pointer(
        context_bundle,
        "../schemas/skill-context-bundle.schema.json",
        errors,
        context,
    )
    try:
        verify_context_bundle(context_bundle)
    except ContextBundleError as exc:
        errors.append(f"{context}: {exc}")
        return

    source_digest = hashlib.sha256(INDEX_JSON.read_bytes()).hexdigest()
    require(
        context_bundle["source_index"]["digest"]["value"] == source_digest,
        errors,
        f"{context}: source index digest mismatch",
    )
    indexed = {skill["id"]: skill for skill in index["skills"]}
    bundled = {skill["id"]: skill for skill in context_bundle["skills"]}
    require(set(bundled) == set(indexed), errors, f"{context}: skill ids mismatch")
    for skill_id, bundle_skill in bundled.items():
        index_skill = indexed.get(skill_id)
        if index_skill is None:
            continue
        for field in ("name", "version", "status", "maturity", "risk_level"):
            require(
                bundle_skill.get(field) == index_skill.get(field),
                errors,
                f"{context}: {skill_id} {field} mismatch",
            )


def validate_mcp_client_contract(
    contract: Dict[str, Any], errors: List[str]
) -> None:
    context = relative(MCP_CLIENT_JSON)
    require_schema_pointer(
        contract,
        "../schemas/mcp-client-contract.schema.json",
        errors,
        context,
    )
    try:
        validate_client_contract(contract)
    except ClientContractError as exc:
        errors.append(f"{context}: {exc}")


def validate_generated_release_status(
    status: Dict[str, Any], errors: List[str]
) -> None:
    context = relative(RELEASE_STATUS_JSON)
    require_schema_pointer(
        status,
        "../schemas/release-status.schema.json",
        errors,
        context,
    )
    try:
        validate_release_status(status)
    except ReleaseStatusError as exc:
        errors.append(f"{context}: {exc}")


def validate_community_pilot(report: Dict[str, Any], errors: List[str]) -> None:
    context = relative(COMMUNITY_PILOT_JSON)
    require_schema_pointer(
        report,
        "../schemas/community-pilot-report.schema.json",
        errors,
        context,
    )
    try:
        validate_pilot_report(report)
    except CommunityPilotError as exc:
        errors.append(f"{context}: {exc}")


def validate_release(path: Path, release: Dict[str, Any], errors: List[str]) -> None:
    context = relative(path)
    require_schema_pointer(
        release,
        "../../schemas/release-manifest.schema.json",
        errors,
        context,
    )
    require(
        release.get("generated_by") == "tools/build_release_manifest.py",
        errors,
        f"{context}: generated_by mismatch",
    )
    require(
        release.get("version") == path.stem,
        errors,
        f"{context}: version must match snapshot filename",
    )
    registry = release.get("registry", {})
    require(isinstance(registry, dict), errors, f"{context}: registry must be an object")
    if not isinstance(registry, dict):
        return
    for field in (
        "skill_count",
        "collection_count",
        "site_adapter_count",
        "category_count",
        "scheduler_count",
        "tool_count",
        "uncollected_skill_count",
    ):
        require(
            isinstance(registry.get(field), int) and registry.get(field, -1) >= 0,
            errors,
            f"{context}: registry.{field} must be a non-negative integer",
        )

    files = release.get("files", [])
    require(isinstance(files, list), errors, f"{context}: files must be an array")
    if not isinstance(files, list):
        return
    require(release.get("file_count") == len(files), errors, f"{context}: file_count mismatch")
    byte_total = sum(
        entry.get("bytes", 0) for entry in files if isinstance(entry, dict)
    )
    require(
        release.get("total_bytes") == byte_total,
        errors,
        f"{context}: total_bytes mismatch",
    )
    paths: List[str] = []
    for entry in files:
        if not isinstance(entry, dict):
            errors.append(f"{context}: file entry must be an object")
            continue
        path = entry.get("path")
        if not isinstance(path, str):
            errors.append(f"{context}: file entry missing path")
            continue
        paths.append(path)
        require(
            isinstance(entry.get("bytes"), int) and entry.get("bytes", -1) >= 0,
            errors,
            f"{context}: invalid byte count for {path}",
        )
        require(
            isinstance(entry.get("sha256"), str)
            and re.fullmatch(r"[a-f0-9]{64}", entry.get("sha256", "")) is not None,
            errors,
            f"{context}: invalid sha256 for {path}",
        )
    require(len(paths) == len(set(paths)), errors, f"{context}: duplicate file paths")
    require(paths == sorted(paths), errors, f"{context}: file paths must be sorted")


def validate_release_provenance(
    provenance: Dict[str, Any], errors: List[str]
) -> None:
    context = relative(RELEASE_PROVENANCE_JSON)
    release = RELEASE_PROVENANCE_JSON.stem
    manifest_path = RELEASE_DIR / f"{release}.json"
    if not manifest_path.exists():
        errors.append(f"{relative(manifest_path)} is missing")
        return
    try:
        validate_release_provenance_record(
            provenance,
            release,
            hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        )
    except ReleaseProvenanceError as exc:
        errors.append(f"{context}: {exc}")


def validate_package_data(errors: List[str]) -> None:
    snapshots = {
        PACKAGE_DATA_DIR / "index.json": INDEX_JSON,
        PACKAGE_DATA_DIR / "health.json": HEALTH_JSON,
        PACKAGE_DATA_DIR / "community-pilot-v0.6.0.json": COMMUNITY_PILOT_JSON,
        PACKAGE_DATA_DIR / "release-provenance.json": RELEASE_PROVENANCE_JSON,
        PACKAGE_DATA_DIR / "release-status.json": RELEASE_STATUS_JSON,
        PACKAGE_DATA_DIR / "review-status.json": REVIEW_STATUS_JSON,
        PACKAGE_DATA_DIR / "skill-context.json": CONTEXT_JSON,
        PACKAGE_INTEGRATION_DIR / "mcp-client.json": MCP_CLIENT_JSON,
        PACKAGE_SECURITY_DIR / "community-default.json": SECURITY_POLICY_JSON,
    }
    for package_path, source_path in snapshots.items():
        require(package_path.exists(), errors, f"{relative(package_path)} is missing")
        if package_path.exists():
            require(
                package_path.read_text(encoding="utf-8")
                == source_path.read_text(encoding="utf-8"),
                errors,
                f"{relative(package_path)} does not match {relative(source_path)}",
            )


def public_count_expectations(index: Dict[str, Any]) -> Dict[str, List[str]]:
    skill_count = index.get("skill_count")
    collection_count = index.get("collection_count")
    site_adapter_count = index.get("site_adapter_count")
    return {
        "CHANGELOG.md": [f"- {skill_count} seed HPC skills"],
        "ROADMAP.md": [
            f"- {skill_count} seed skills.",
            f"- {collection_count} curated collections.",
            f"- {site_adapter_count} site adapters:",
        ],
        "docs/COMPATIBILITY.md": [
            f"| Skills | {skill_count} |",
            f"| Collections | {collection_count} |",
            f"| Site adapters | {site_adapter_count} |",
        ],
        "docs/OPEN_SOURCE_PROPOSAL.md": [
            f"The seed registry includes {skill_count} skills",
            f"{collection_count} curated collections",
            f"{site_adapter_count} site adapters",
        ],
        "docs/PUBLIC_LAUNCH_PACKET.md": [
            f"- Seed skills: {skill_count}.",
            f"- Curated collections: {collection_count}.",
            f"- Site adapters: {site_adapter_count},",
        ],
        "docs/REGISTRY_HEALTH.md": [
            f"- Skills: {skill_count}",
            f"- Site adapters: {site_adapter_count}",
            f"- Collections: {collection_count}",
        ],
        "docs/RELEASE_NOTES_v0.2.0.md": [
            f"- Skills: {skill_count}.",
            f"- Collections: {collection_count}.",
            f"- Site adapters: {site_adapter_count},",
        ],
        "docs/RELEASE_NOTES_v0.3.0.md": [
            f"- Skills: {skill_count}.",
            f"- Collections: {collection_count}.",
            f"- Site adapters: {site_adapter_count},",
        ],
        "docs/RELEASE_NOTES_v0.4.0.md": [
            f"- Skills: {skill_count}.",
            f"- Collections: {collection_count}.",
            f"- Site adapters: {site_adapter_count},",
        ],
        "docs/RELEASE_NOTES_v0.5.0.md": [
            f"- Skills: {skill_count}.",
            f"- Collections: {collection_count}.",
            f"- Site adapters: {site_adapter_count}.",
        ],
        "docs/RELEASE_NOTES_v0.6.0.md": [
            f"- Skills: {skill_count}.",
            f"- Collections: {collection_count}.",
            f"- Site adapters: {site_adapter_count}.",
        ],
        "docs/REVIEW_PACKET_v0.2.0.md": [
            f"- Skills: {skill_count}",
        ],
        "docs/SKILL_CATALOG.md": [
            f"Current registry size: {skill_count} skills.",
        ],
    }


def validate_public_count_mentions(index: Dict[str, Any], errors: List[str]) -> None:
    expected_mentions = public_count_expectations(index)

    for path in PUBLIC_BASELINE_DOCS:
        rel = relative(path)
        text = path.read_text(encoding="utf-8")
        for expected in expected_mentions[rel]:
            require(
                expected in text,
                errors,
                f"{rel}: expected public registry baseline mention {expected!r}",
            )


def validate_schemas(errors: List[str]) -> None:
    for name, path in SCHEMAS.items():
        require(path.exists(), errors, f"schema {name} is missing at {relative(path)}")
        if path.exists():
            payload = load_json(path)
            require(payload.get("$schema"), errors, f"{relative(path)}: missing $schema")
            require(payload.get("$id"), errors, f"{relative(path)}: missing $id")
            require(payload.get("title"), errors, f"{relative(path)}: missing title")


def validate_security_policy(errors: List[str]) -> None:
    try:
        policy = load_effective_policy(RULE_CATALOG)
    except (SecurityPolicyError, OSError) as exc:
        errors.append(f"{relative(SECURITY_POLICY_JSON)}: {exc}")
        return
    require(
        policy.policy_id == "community-default" and policy.version == "0.1.0",
        errors,
        f"{relative(SECURITY_POLICY_JSON)}: default policy identity mismatch",
    )
    require(
        set(policy.enabled_rules) == set(RULE_CATALOG),
        errors,
        f"{relative(SECURITY_POLICY_JSON)}: rule catalog mismatch",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate generated registry artifacts and package snapshots"
    )
    parser.add_argument(
        "--release-only",
        action="store_true",
        help="Validate immutable published release snapshots only",
    )
    args = parser.parse_args()

    errors: List[str] = []
    validate_schemas(errors)
    validate_security_policy(errors)
    releases = sorted(RELEASE_DIR.glob("v*.json"))
    require(bool(releases), errors, "registry/releases has no versioned snapshots")
    for release_path in releases:
        validate_release(release_path, load_json(release_path), errors)
    if args.release_only:
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Validated {len(releases)} versioned release snapshot(s).")
        return 0

    index = load_json(INDEX_JSON)
    health = load_json(HEALTH_JSON)
    quality = load_json(QUALITY_JSON)
    review_status = load_json(REVIEW_STATUS_JSON)
    release_status = load_json(RELEASE_STATUS_JSON)
    community_pilot = load_json(COMMUNITY_PILOT_JSON)
    release_provenance = load_json(RELEASE_PROVENANCE_JSON)
    context_bundle = load_json(CONTEXT_JSON)
    mcp_client_contract = load_json(MCP_CLIENT_JSON)
    validate_index(index, errors)
    validate_health(index, health, errors)
    validate_skill_quality(index, quality, errors)
    validate_review_status(index, review_status, errors)
    validate_generated_release_status(release_status, errors)
    validate_community_pilot(community_pilot, errors)
    validate_release_provenance(release_provenance, errors)
    validate_context_bundle(index, context_bundle, errors)
    validate_mcp_client_contract(mcp_client_contract, errors)
    validate_package_data(errors)
    validate_public_count_mentions(index, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        "Validated registry artifacts: "
        f"{index['skill_count']} skill(s), "
        f"{index['collection_count']} collection(s), "
        f"{index['site_adapter_count']} site adapter(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
