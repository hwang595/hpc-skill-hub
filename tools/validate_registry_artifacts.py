#!/usr/bin/env python3
"""Validate generated registry artifacts and their public contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set


ROOT = Path(__file__).resolve().parents[1]
INDEX_JSON = ROOT / "registry" / "index.json"
HEALTH_JSON = ROOT / "registry" / "health.json"
RELEASE_MANIFEST = ROOT / "registry" / "releases" / "v0.1.0.json"
PACKAGE_DATA_DIR = ROOT / "src" / "hpc_skill_hub" / "data" / "registry"
SCHEMAS = {
    "index": ROOT / "schemas" / "registry-index.schema.json",
    "health": ROOT / "schemas" / "registry-health.schema.json",
    "release": ROOT / "schemas" / "release-manifest.schema.json",
}
PUBLIC_BASELINE_DOCS = [
    ROOT / "CHANGELOG.md",
    ROOT / "ROADMAP.md",
    ROOT / "docs" / "COMPATIBILITY.md",
    ROOT / "docs" / "OPEN_SOURCE_PROPOSAL.md",
    ROOT / "docs" / "PUBLIC_LAUNCH_PACKET.md",
    ROOT / "docs" / "REGISTRY_HEALTH.md",
    ROOT / "docs" / "RELEASE_NOTES_v0.1.0.md",
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
        for override_id in adapter.get("skill_overrides", []):
            require(
                override_id in known_skills,
                errors,
                f"{adapter_context}: unknown skill override {override_id}",
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


def validate_release(
    index: Dict[str, Any], health: Dict[str, Any], release: Dict[str, Any], errors: List[str]
) -> None:
    context = relative(RELEASE_MANIFEST)
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
    registry = release.get("registry", {})
    require(registry.get("skill_count") == index.get("skill_count"), errors, f"{context}: skill_count mismatch")
    require(
        registry.get("collection_count") == index.get("collection_count"),
        errors,
        f"{context}: collection_count mismatch",
    )
    require(
        registry.get("site_adapter_count") == index.get("site_adapter_count"),
        errors,
        f"{context}: site_adapter_count mismatch",
    )
    require(
        registry.get("risk_counts") == health.get("risk_counts"),
        errors,
        f"{context}: risk_counts mismatch",
    )

    files = release.get("files", [])
    require(release.get("file_count") == len(files), errors, f"{context}: file_count mismatch")
    require(
        release.get("total_bytes") == sum(entry.get("bytes", 0) for entry in files),
        errors,
        f"{context}: total_bytes mismatch",
    )
    for entry in files:
        path = entry.get("path")
        if not isinstance(path, str):
            errors.append(f"{context}: file entry missing path")
            continue
        source = ROOT / path
        require(source.exists(), errors, f"{context}: listed file missing {path}")
        if source.exists():
            data = source.read_bytes()
            require(entry.get("bytes") == len(data), errors, f"{context}: byte count mismatch for {path}")
            require(
                entry.get("sha256") == hashlib.sha256(data).hexdigest(),
                errors,
                f"{context}: sha256 mismatch for {path}",
            )


def validate_package_data(errors: List[str]) -> None:
    for filename, source_path in {
        "index.json": INDEX_JSON,
        "health.json": HEALTH_JSON,
    }.items():
        package_path = PACKAGE_DATA_DIR / filename
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
        "docs/RELEASE_NOTES_v0.1.0.md": [
            f"- Skills: {skill_count}.",
            f"- Collections: {collection_count}.",
            f"- Site adapters: {site_adapter_count},",
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate generated registry artifacts and package snapshots"
    )
    parser.parse_args()

    errors: List[str] = []
    validate_schemas(errors)
    index = load_json(INDEX_JSON)
    health = load_json(HEALTH_JSON)
    release = load_json(RELEASE_MANIFEST)
    validate_index(index, errors)
    validate_health(index, health, errors)
    validate_release(index, health, release, errors)
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
