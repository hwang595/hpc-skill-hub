#!/usr/bin/env python3
"""Build registry health reports from registry/index.json."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
INDEX_JSON = ROOT / "registry" / "index.json"
HEALTH_JSON = ROOT / "registry" / "health.json"
HEALTH_MD = ROOT / "docs" / "REGISTRY_HEALTH.md"


def load_index() -> Dict[str, Any]:
    with INDEX_JSON.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def count_values(skills: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    return dict(sorted(Counter(skill[field] for skill in skills).items()))


def build_health(index: Dict[str, Any]) -> Dict[str, Any]:
    skills = index["skills"]
    collections = index.get("collections", [])
    collected_skill_ids = {
        skill_id
        for collection in collections
        for skill_id in collection.get("skill_ids", [])
    }
    all_skill_ids = {skill["id"] for skill in skills}
    uncollected = sorted(all_skill_ids - collected_skill_ids)

    risk_by_skill = {
        skill["id"]: skill["risk_level"]
        for skill in sorted(skills, key=lambda item: item["id"])
    }
    collection_coverage = [
        {
            "id": collection["id"],
            "skill_count": len(collection["skill_ids"]),
            "skill_ids": collection["skill_ids"],
        }
        for collection in collections
    ]

    return {
        "$schema": "../schemas/registry-health.schema.json",
        "schema_version": "0.1.0",
        "generated_by": "tools/build_health.py",
        "skill_count": index["skill_count"],
        "site_adapter_count": index["site_adapter_count"],
        "collection_count": index.get("collection_count", len(collections)),
        "risk_counts": count_values(skills, "risk_level"),
        "maturity_counts": count_values(skills, "maturity"),
        "status_counts": count_values(skills, "status"),
        "category_counts": index["categories"],
        "collection_coverage": collection_coverage,
        "uncollected_skill_ids": uncollected,
        "risk_by_skill": risk_by_skill,
    }


def markdown_table(mapping: Dict[str, int], first_header: str) -> List[str]:
    lines = [f"| {first_header} | Count |", "| --- | ---: |"]
    for key, value in mapping.items():
        lines.append(f"| `{key}` | {value} |")
    return lines


def build_markdown(health: Dict[str, Any]) -> str:
    lines = [
        "# Registry Health",
        "",
        "This report is generated from `registry/index.json` by `tools/build_health.py`.",
        "",
        "## Summary",
        "",
        f"- Skills: {health['skill_count']}",
        f"- Site adapters: {health['site_adapter_count']}",
        f"- Collections: {health['collection_count']}",
        f"- Uncollected skills: {len(health['uncollected_skill_ids'])}",
        "",
        "## Risk Distribution",
        "",
        *markdown_table(health["risk_counts"], "Risk"),
        "",
        "## Maturity Distribution",
        "",
        *markdown_table(health["maturity_counts"], "Maturity"),
        "",
        "## Status Distribution",
        "",
        *markdown_table(health["status_counts"], "Status"),
        "",
        "## Collection Coverage",
        "",
        "| Collection | Skills |",
        "| --- | ---: |",
    ]
    for collection in health["collection_coverage"]:
        lines.append(f"| `{collection['id']}` | {collection['skill_count']} |")

    lines.extend(["", "## Uncollected Skills", ""])
    if health["uncollected_skill_ids"]:
        for skill_id in health["uncollected_skill_ids"]:
            lines.append(f"- `{skill_id}`")
    else:
        lines.append("All skills are included in at least one collection.")

    lines.extend(["", "## Risk By Skill", "", "| Skill | Risk |", "| --- | --- |"])
    for skill_id, risk in health["risk_by_skill"].items():
        lines.append(f"| `{skill_id}` | {risk} |")

    lines.append("")
    return "\n".join(lines)


def write_outputs(health: Dict[str, Any]) -> None:
    HEALTH_JSON.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_JSON.write_text(json.dumps(health, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    HEALTH_MD.write_text(build_markdown(health), encoding="utf-8")


def check_outputs(health: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected_json = json.dumps(health, indent=2, sort_keys=True) + "\n"
    expected_markdown = build_markdown(health)

    if not HEALTH_JSON.exists():
        errors.append(f"{HEALTH_JSON.relative_to(ROOT)} is missing")
    elif HEALTH_JSON.read_text(encoding="utf-8") != expected_json:
        errors.append(f"{HEALTH_JSON.relative_to(ROOT)} is stale; run tools/build_health.py")

    if not HEALTH_MD.exists():
        errors.append(f"{HEALTH_MD.relative_to(ROOT)} is missing")
    elif HEALTH_MD.read_text(encoding="utf-8") != expected_markdown:
        errors.append(f"{HEALTH_MD.relative_to(ROOT)} is stale; run tools/build_health.py")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Build registry health reports")
    parser.add_argument("--check", action="store_true", help="Fail if generated reports are stale")
    args = parser.parse_args()

    health = build_health(load_index())
    if args.check:
        errors = check_outputs(health)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(
            f"Registry health is current for {health['skill_count']} skill(s), "
            f"{health['site_adapter_count']} site adapter(s), and "
            f"{health['collection_count']} collection(s)."
        )
        return 0

    write_outputs(health)
    print(f"Wrote {HEALTH_JSON.relative_to(ROOT)} and {HEALTH_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
