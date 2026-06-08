#!/usr/bin/env python3
"""Build machine-readable and Markdown indexes for the skill registry."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
REGISTRY_DIR = ROOT / "registry"
INDEX_JSON = REGISTRY_DIR / "index.json"
CATALOG_MD = ROOT / "docs" / "SKILL_CATALOG.md"


def load_manifest(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_manifests() -> Iterable[Dict[str, Any]]:
    for manifest_path in sorted(SKILLS_DIR.glob("*/skill.json")):
        manifest = load_manifest(manifest_path)
        skill_dir = manifest_path.parent
        manifest["_path"] = str(skill_dir.relative_to(ROOT))
        yield manifest


def compact_skill(manifest: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": manifest["id"],
        "name": manifest["name"],
        "summary": manifest["summary"],
        "description": manifest["description"],
        "version": manifest["version"],
        "status": manifest["status"],
        "maturity": manifest["maturity"],
        "risk_level": manifest["risk_level"],
        "categories": manifest["categories"],
        "tags": manifest["tags"],
        "schedulers": manifest.get("schedulers", []),
        "tools": [tool["name"] for tool in manifest["tools"]],
        "path": manifest["_path"],
        "readme": f"{manifest['_path']}/README.md",
        "examples": [
            {
                "title": example["title"],
                "path": f"{manifest['_path']}/{example['path']}",
            }
            for example in manifest["examples"]
        ],
        "references": manifest["references"],
    }


def build_index(skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    category_counts: Dict[str, int] = defaultdict(int)
    tag_counts: Dict[str, int] = defaultdict(int)
    scheduler_counts: Dict[str, int] = defaultdict(int)
    tool_counts: Dict[str, int] = defaultdict(int)

    for skill in skills:
        for category in skill["categories"]:
            category_counts[category] += 1
        for tag in skill["tags"]:
            tag_counts[tag] += 1
        for scheduler in skill["schedulers"]:
            scheduler_counts[scheduler] += 1
        for tool in skill["tools"]:
            tool_counts[tool] += 1

    return {
        "schema_version": "0.1.0",
        "generated_by": "tools/build_index.py",
        "skill_count": len(skills),
        "categories": dict(sorted(category_counts.items())),
        "tags": dict(sorted(tag_counts.items())),
        "schedulers": dict(sorted(scheduler_counts.items())),
        "tools": dict(sorted(tool_counts.items())),
        "skills": skills,
    }


def category_title(category: str) -> str:
    acronyms = {
        "gpu": "GPU",
        "mpi": "MPI",
    }
    if category in acronyms:
        return acronyms[category]
    return category.replace("-", " ").replace("_", " ").title()


def build_catalog(index: Dict[str, Any]) -> str:
    skills = index["skills"]
    by_category: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for skill in skills:
        for category in skill["categories"]:
            by_category[category].append(skill)

    lines = [
        "# Skill Catalog",
        "",
        "This catalog is generated from `skills/*/skill.json` by `tools/build_index.py`.",
        "",
        f"Current registry size: {index['skill_count']} skills.",
        "",
        "## Categories",
        "",
        "| Category | Skills |",
        "| --- | ---: |",
    ]

    for category, count in index["categories"].items():
        lines.append(f"| `{category}` | {count} |")

    lines.extend(["", "## Skills By Category", ""])

    for category in sorted(by_category):
        lines.extend(
            [
                f"### {category_title(category)}",
                "",
                "| Skill | Risk | Maturity | Description |",
                "| --- | --- | --- | --- |",
            ]
        )
        for skill in sorted(by_category[category], key=lambda item: item["id"]):
            lines.append(
                f"| [`{skill['id']}`](../{skill['readme']}) | "
                f"{skill['risk_level']} | {skill['maturity']} | {skill['summary']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Next Candidates",
            "",
            "- Open OnDemand app templates.",
            "- PyTorch distributed training on Slurm.",
            "- NCCL multi-node diagnostics.",
            "- Filesystem quota and metadata pressure checks.",
            "- WRF, GROMACS, LAMMPS, OpenFOAM, and Quantum ESPRESSO starter skills.",
            "- Bioinformatics workflows for nf-core, GATK, BLAST, and AlphaFold.",
            "- Facility read-only reports for fairshare, partitions, and node health.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(index: Dict[str, Any]) -> None:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_JSON.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CATALOG_MD.write_text(build_catalog(index), encoding="utf-8")


def check_outputs(index: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    expected_index = json.dumps(index, indent=2, sort_keys=True) + "\n"
    expected_catalog = build_catalog(index)

    if not INDEX_JSON.exists():
        errors.append(f"{INDEX_JSON.relative_to(ROOT)} is missing")
    elif INDEX_JSON.read_text(encoding="utf-8") != expected_index:
        errors.append(f"{INDEX_JSON.relative_to(ROOT)} is stale; run tools/build_index.py")

    if not CATALOG_MD.exists():
        errors.append(f"{CATALOG_MD.relative_to(ROOT)} is missing")
    elif CATALOG_MD.read_text(encoding="utf-8") != expected_catalog:
        errors.append(f"{CATALOG_MD.relative_to(ROOT)} is stale; run tools/build_index.py")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the HPC Skill Hub registry index")
    parser.add_argument("--check", action="store_true", help="Fail if generated outputs are stale")
    args = parser.parse_args()

    skills = [compact_skill(manifest) for manifest in iter_manifests()]
    index = build_index(skills)

    if args.check:
        errors = check_outputs(index)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Registry index is current for {len(skills)} skill(s).")
        return 0

    write_outputs(index)
    print(f"Wrote {INDEX_JSON.relative_to(ROOT)} and {CATALOG_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
