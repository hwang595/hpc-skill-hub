#!/usr/bin/env python3
"""Build generated compatibility tables from the registry index."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


ROOT = Path(__file__).resolve().parents[1]
INDEX_JSON = ROOT / "registry" / "index.json"
OUTPUT_MD = ROOT / "docs" / "COMPATIBILITY.md"


WORKFLOW_AREAS = [
    ("Slurm dependencies", ["slurm-job-dependency-chain"]),
    ("Dask", ["dask"]),
    ("Ray", ["ray"]),
    ("Nextflow and nf-core", ["nextflow", "nf-core"]),
    ("Snakemake", ["snakemake"]),
    ("CWL", ["cwl"]),
    ("WDL", ["wdl"]),
]

STACK_AREAS = [
    ("Apptainer and Singularity", ["apptainer", "singularity", "container"]),
    ("Spack", ["spack"]),
    ("EasyBuild", ["easybuild", "eb"]),
    ("Conda and Mamba", ["conda", "mamba", "micromamba"]),
    ("Python", ["python", "python3", "virtualenv", "mpi4py"]),
    ("R, Julia, and MATLAB", ["Rscript", "julia", "matlab"]),
    ("Compiler and MPI stacks", ["compiler", "mpi", "mpicc", "mpicxx", "mpifort"]),
]

DOMAIN_COLLECTION_IDS = [
    "ai-hpc",
    "bioinformatics-workflows",
    "simulation-workflows",
    "data-movement",
    "facility-ops",
    "training-onboarding",
]


def load_index() -> Dict[str, Any]:
    with INDEX_JSON.open(encoding="utf-8") as handle:
        return json.load(handle)


def skill_link(skill: Dict[str, Any]) -> str:
    return f"[`{skill['id']}`](../{skill['readme']})"


def collection_link(collection: Dict[str, Any]) -> str:
    return f"[`{collection['id']}`](../{collection['path']})"


def comma_join(items: Iterable[str]) -> str:
    values = list(items)
    return ", ".join(values) if values else "-"


def manifest_tokens(skill: Dict[str, Any]) -> set[str]:
    raw_values = [
        skill["id"],
        *skill["categories"],
        *skill["tags"],
        *skill["tools"],
    ]
    tokens: set[str] = set()
    for value in raw_values:
        normalized = value.lower()
        tokens.add(normalized)
        tokens.update(part for part in normalized.replace("_", "-").split("-") if part)
    return tokens


def skill_matches(skill: Dict[str, Any], needles: Sequence[str]) -> bool:
    tokens = manifest_tokens(skill)
    return any(needle.lower() in tokens for needle in needles)


def skills_for_collection(
    collection: Dict[str, Any], skills_by_id: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    return [skills_by_id[skill_id] for skill_id in collection["skill_ids"]]


def collection_membership(index: Dict[str, Any]) -> Dict[str, List[str]]:
    membership: Dict[str, List[str]] = defaultdict(list)
    for collection in index["collections"]:
        for skill_id in collection["skill_ids"]:
            membership[skill_id].append(collection["id"])
    return {skill_id: sorted(collections) for skill_id, collections in membership.items()}


def scheduler_table(index: Dict[str, Any]) -> List[str]:
    membership = collection_membership(index)
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for skill in index["skills"]:
        schedulers = skill["schedulers"] or ["scheduler-agnostic"]
        for scheduler in schedulers:
            grouped[scheduler].append(skill)

    lines = [
        "## Scheduler Coverage",
        "",
        "| Scheduler | Skills | Categories | Collections |",
        "| --- | ---: | --- | --- |",
    ]
    for scheduler in sorted(grouped):
        skills = sorted(grouped[scheduler], key=lambda item: item["id"])
        categories = sorted({category for skill in skills for category in skill["categories"]})
        collections = sorted({name for skill in skills for name in membership.get(skill["id"], [])})
        lines.append(
            f"| `{scheduler}` | {len(skills)} | "
            f"{comma_join(f'`{category}`' for category in categories)} | "
            f"{comma_join(f'`{collection}`' for collection in collections)} |"
        )
    return lines


def collection_category_matrix(index: Dict[str, Any]) -> List[str]:
    skills_by_id = {skill["id"]: skill for skill in index["skills"]}
    categories = sorted(index["categories"])

    lines = [
        "## Collection And Category Matrix",
        "",
        "Counts show how many skills in each collection include each category.",
        "",
        "| Collection | Skills | " + " | ".join(f"`{category}`" for category in categories) + " |",
        "| --- | ---: | " + " | ".join("---:" for _ in categories) + " |",
    ]
    for collection in index["collections"]:
        skills = skills_for_collection(collection, skills_by_id)
        counts = [
            sum(1 for skill in skills if category in skill["categories"])
            for category in categories
        ]
        lines.append(
            f"| {collection_link(collection)} | {len(skills)} | "
            + " | ".join(str(count) for count in counts)
            + " |"
        )
    return lines


def area_table(
    title: str,
    areas: Sequence[tuple[str, Sequence[str]]],
    skills: Sequence[Dict[str, Any]],
) -> List[str]:
    lines = [
        f"## {title}",
        "",
        "| Area | Skills |",
        "| --- | --- |",
    ]
    for area, needles in areas:
        matched = sorted(
            [skill for skill in skills if skill_matches(skill, needles)],
            key=lambda item: item["id"],
        )
        lines.append(f"| {area} | {comma_join(skill_link(skill) for skill in matched)} |")
    return lines


def domain_collection_table(index: Dict[str, Any]) -> List[str]:
    skills_by_id = {skill["id"]: skill for skill in index["skills"]}
    collections_by_id = {collection["id"]: collection for collection in index["collections"]}
    lines = [
        "## Domain And Adoption Collections",
        "",
        "| Collection | Skills | Dominant categories | Audience |",
        "| --- | ---: | --- | --- |",
    ]
    for collection_id in DOMAIN_COLLECTION_IDS:
        collection = collections_by_id[collection_id]
        skills = skills_for_collection(collection, skills_by_id)
        category_counts: Dict[str, int] = defaultdict(int)
        for skill in skills:
            for category in skill["categories"]:
                category_counts[category] += 1
        dominant = sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))[:4]
        lines.append(
            f"| {collection_link(collection)} | {len(skills)} | "
            f"{comma_join(f'`{category}` ({count})' for category, count in dominant)} | "
            f"{', '.join(collection['audience'])} |"
        )
    return lines


def tool_table(index: Dict[str, Any]) -> List[str]:
    tools = sorted(index["tools"].items(), key=lambda item: (-item[1], item[0].lower()))
    common = [(tool, count) for tool, count in tools if count >= 2]
    specialized = [tool for tool, count in tools if count == 1]

    lines = [
        "## Tool Signals",
        "",
        "Tools are declared by skill manifests. Counts are not installation checks;",
        "they show where examples and wrappers expect a command or library.",
        "",
        "### Common Tools",
        "",
        "| Tool | Skills |",
        "| --- | ---: |",
    ]
    for tool, count in common:
        lines.append(f"| `{tool}` | {count} |")

    lines.extend(
        [
            "",
            "### Specialized Single-Skill Tools",
            "",
            comma_join(f"`{tool}`" for tool in specialized) + ".",
        ]
    )
    return lines


def build_compatibility(index: Dict[str, Any]) -> str:
    lines = [
        "# Compatibility Tables",
        "",
        "This document is generated from `registry/index.json` by",
        "`tools/build_compatibility.py`. Do not edit it by hand.",
        "",
        "## Summary",
        "",
        "| Signal | Count |",
        "| --- | ---: |",
        f"| Skills | {index['skill_count']} |",
        f"| Collections | {index['collection_count']} |",
        f"| Site adapters | {index['site_adapter_count']} |",
        f"| Schedulers | {len(index['schedulers'])} |",
        f"| Categories | {len(index['categories'])} |",
        f"| Tools | {len(index['tools'])} |",
        "",
    ]

    sections = [
        scheduler_table(index),
        collection_category_matrix(index),
        area_table("Workflow Engine Coverage", WORKFLOW_AREAS, index["skills"]),
        area_table("Software Stack And Container Coverage", STACK_AREAS, index["skills"]),
        domain_collection_table(index),
        tool_table(index),
    ]
    for section in sections:
        lines.extend(section)
        lines.append("")

    return "\n".join(lines)


def check_output(expected: str) -> List[str]:
    if not OUTPUT_MD.exists():
        return [f"{OUTPUT_MD.relative_to(ROOT)} is missing"]
    if OUTPUT_MD.read_text(encoding="utf-8") != expected:
        return [f"{OUTPUT_MD.relative_to(ROOT)} is stale; run tools/build_compatibility.py"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build generated compatibility tables for the HPC Skill Hub registry"
    )
    parser.add_argument("--check", action="store_true", help="Fail if output is stale")
    args = parser.parse_args()

    expected = build_compatibility(load_index())
    if args.check:
        errors = check_output(expected)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Compatibility tables are current in {OUTPUT_MD.relative_to(ROOT)}.")
        return 0

    OUTPUT_MD.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
