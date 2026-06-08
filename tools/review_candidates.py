#!/usr/bin/env python3
"""Rank seed skills that are ready for first domain review routing."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
INDEX_JSON = ROOT / "registry" / "index.json"

RISK_SCORE = {"low": 3, "medium": 1, "high": 0}
RISK_ORDER = {"low": 0, "medium": 1, "high": 2}

REVIEW_FOCUS_RULES = [
    (
        "Facility operations and training",
        {
            "admin",
            "education",
            "facility-ops",
            "training-onboarding",
            "cluster-usage",
            "node-health",
            "workshop",
        },
    ),
    (
        "Bioinformatics workflows",
        {
            "bioinformatics-workflows",
            "bioinformatics",
            "nf-core",
            "gatk",
            "blast",
            "genomics",
        },
    ),
    (
        "Simulation workflows",
        {
            "simulation-workflows",
            "simulation",
            "gromacs",
            "lammps",
            "namd",
            "quantum-espresso",
            "cp2k",
            "openfoam",
            "wrf",
        },
    ),
    (
        "MPI and performance",
        {
            "gpu-mpi-performance",
            "mpi",
            "performance",
            "profiling",
            "benchmark",
            "openmp",
            "ior",
            "mdtest",
        },
    ),
    (
        "AI, GPU, and accelerator workflows",
        {
            "ai-hpc",
            "gpu",
            "accelerator",
            "ray",
            "dask",
            "jax",
            "accelerate",
            "tensorflow",
            "pytorch",
            "deepspeed",
            "nccl",
            "tensorboard",
        },
    ),
    (
        "Workflow engines",
        {
            "workflow",
            "workflow-engines",
            "nextflow",
            "snakemake",
            "cwl",
            "wdl",
            "checkpoint",
        },
    ),
    (
        "Containers",
        {
            "containers",
            "container",
            "apptainer",
            "singularity",
        },
    ),
    (
        "Software environments",
        {
            "software",
            "module",
            "modules",
            "conda",
            "mamba",
            "python",
            "spack",
            "easybuild",
            "r",
            "julia",
            "matlab",
        },
    ),
    (
        "Storage and data movement",
        {
            "data",
            "data-movement",
            "storage",
            "scratch",
            "quota",
            "globus",
            "rsync",
            "object-storage",
            "checksum",
            "archive",
        },
    ),
    (
        "Scheduler and allocation",
        {
            "scheduler",
            "scheduler-basics",
            "core-hpc",
            "slurm",
            "pbs",
            "lsf",
            "htcondor",
            "grid-engine",
            "array",
            "dependency",
        },
    ),
]

CATEGORY_FOCUS_RULES = [
    ("Facility operations and training", {"admin", "education"}),
    ("Bioinformatics workflows", {"bioinformatics"}),
    ("Simulation workflows", {"simulation"}),
    ("AI, GPU, and accelerator workflows", {"gpu"}),
    ("Scheduler and allocation", {"scheduler"}),
    ("MPI and performance", {"mpi", "performance"}),
    ("Workflow engines", {"workflow"}),
    ("Containers", {"containers"}),
    ("Software environments", {"software"}),
    ("Storage and data movement", {"data"}),
]


@dataclass(frozen=True)
class Candidate:
    id: str
    name: str
    summary: str
    maturity: str
    risk_level: str
    categories: List[str]
    collections: List[str]
    score: int
    review_focus: str
    evidence: List[str]


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def manifest_for(skill: Dict[str, Any]) -> Dict[str, Any]:
    manifest_path = ROOT / skill["path"] / "skill.json"
    if not manifest_path.exists():
        return {}
    return load_json(manifest_path)


def collection_membership(index: Dict[str, Any]) -> Dict[str, List[str]]:
    membership: Dict[str, List[str]] = {}
    for collection in index["collections"]:
        collection_id = collection["id"]
        for skill_id in collection["skill_ids"]:
            membership.setdefault(skill_id, []).append(collection_id)
    return {skill_id: sorted(collections) for skill_id, collections in membership.items()}


def has_static_or_dry_run_test(manifest: Dict[str, Any]) -> bool:
    for test in manifest.get("tests", []):
        test_type = str(test.get("type", "")).lower()
        command = str(test.get("command", "")).lower()
        description = str(test.get("description", "")).lower()
        if test_type == "static":
            return True
        if "dry-run" in command or "dry run" in description or "dry-run" in description:
            return True
    return False


def focus_from_signals(
    signals: Iterable[str],
    rules: Iterable[tuple[str, set[str]]] = REVIEW_FOCUS_RULES,
) -> str:
    normalized = {value.lower() for value in signals}
    for focus, keys in rules:
        if normalized & keys:
            return focus
    return "Registry maintainer"


def review_focus(skill: Dict[str, Any], collections: Iterable[str]) -> str:
    focus = focus_from_signals(skill.get("categories", []), CATEGORY_FOCUS_RULES)
    if focus != "Registry maintainer":
        return focus
    metadata_signals = [
        *skill.get("tags", []),
        *skill.get("schedulers", []),
        *skill.get("tools", []),
    ]
    focus = focus_from_signals(metadata_signals)
    if focus != "Registry maintainer":
        return focus
    return focus_from_signals(collections)


def score_skill(
    skill: Dict[str, Any], manifest: Dict[str, Any], collections: List[str]
) -> tuple[int, List[str]]:
    score = RISK_SCORE.get(skill.get("risk_level", "high"), 0)
    evidence = [f"{skill.get('risk_level', 'unknown')} risk"]

    if skill.get("examples"):
        score += 1
        evidence.append("examples")
    if skill.get("references"):
        score += 1
        evidence.append("references")
    if has_static_or_dry_run_test(manifest):
        score += 1
        evidence.append("static or dry-run test")
    if collections:
        score += 1
        evidence.append("collection coverage")
    readme = skill.get("readme")
    if readme and (ROOT / readme).exists():
        score += 1
        evidence.append("README")

    return score, evidence


def build_candidates(index: Dict[str, Any]) -> List[Candidate]:
    membership = collection_membership(index)
    candidates: List[Candidate] = []

    for skill in index["skills"]:
        if skill.get("maturity") != "seed":
            continue
        collections = membership.get(skill["id"], [])
        manifest = manifest_for(skill)
        score, evidence = score_skill(skill, manifest, collections)
        candidates.append(
            Candidate(
                id=skill["id"],
                name=skill["name"],
                summary=skill["summary"],
                maturity=skill["maturity"],
                risk_level=skill["risk_level"],
                categories=list(skill.get("categories", [])),
                collections=collections,
                score=score,
                review_focus=review_focus(skill, collections),
                evidence=evidence,
            )
        )

    return sorted(
        candidates,
        key=lambda candidate: (
            RISK_ORDER.get(candidate.risk_level, 99),
            -candidate.score,
            candidate.review_focus,
            candidate.id,
        ),
    )


def risk_counts(candidates: Iterable[Candidate]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for candidate in candidates:
        counts[candidate.risk_level] = counts.get(candidate.risk_level, 0) + 1
    return dict(sorted(counts.items()))


def filtered_candidates(
    candidates: List[Candidate], collection: str | None
) -> List[Candidate]:
    if collection is None:
        return candidates
    return [
        candidate
        for candidate in candidates
        if collection in candidate.collections
    ]


def escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def markdown(payload: Dict[str, Any]) -> str:
    lines = [
        "# HPC Skill Hub Review Candidates",
        "",
        "This report ranks seed skills that look ready for first domain review",
        "routing. It is based on local metadata and static evidence only; it is",
        "not a maturity promotion decision.",
        "",
        "## Summary",
        "",
        f"- Skills: {payload['skill_count']}",
        f"- Seed skills: {payload['seed_skill_count']}",
        f"- Candidate pool: {payload['candidate_count']}",
        f"- Risk counts: {json.dumps(payload['risk_counts'], sort_keys=True)}",
        f"- Collection filter: `{payload['collection'] or 'all'}`",
        f"- Display limit: {payload['limit']}",
        "",
        "## Candidates",
        "",
        "| Skill | Risk | Categories | Collections | Score | Review Focus |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]

    if not payload["candidates"]:
        lines.append("| _None_ |  |  |  |  |  |")
    else:
        for candidate in payload["candidates"]:
            categories = ", ".join(candidate["categories"])
            collections = ", ".join(candidate["collections"])
            lines.append(
                "| "
                f"`{candidate['id']}` | "
                f"`{candidate['risk_level']}` | "
                f"{escape_table(categories)} | "
                f"{escape_table(collections)} | "
                f"{candidate['score']} | "
                f"{escape_table(candidate['review_focus'])} |"
            )

    lines.extend(
        [
            "",
            "## Review Notes",
            "",
            "- Use this report to seed `maturity-review` issues and domain reviewer",
            "  assignments.",
            "- Confirm examples, references, portability, site assumptions, and risk",
            "  labels before promoting any skill to `reviewed`.",
            "- Keep public review evidence free of private hostnames, allocation names,",
            "  usernames, internal paths, ticket numbers, and unpublished policy.",
            "",
        ]
    )
    return "\n".join(lines)


def build_payload(limit: int, collection: str | None) -> Dict[str, Any]:
    index = load_json(INDEX_JSON)
    candidates = build_candidates(index)
    filtered = filtered_candidates(candidates, collection)
    limited = filtered[:limit]

    return {
        "generated_from": str(INDEX_JSON.relative_to(ROOT)),
        "skill_count": index["skill_count"],
        "seed_skill_count": len(candidates),
        "candidate_count": len(filtered),
        "risk_counts": risk_counts(filtered),
        "collection": collection,
        "limit": limit,
        "candidates": [asdict(candidate) for candidate in limited],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rank seed skills that are ready for first domain review routing"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=12,
        help="Maximum number of candidates to print.",
    )
    parser.add_argument(
        "--collection",
        help="Only show candidates that belong to this collection id.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")

    index = load_json(INDEX_JSON)
    collection_ids = {collection["id"] for collection in index["collections"]}
    if args.collection and args.collection not in collection_ids:
        parser.error(f"unknown collection: {args.collection}")

    payload = build_payload(args.limit, args.collection)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
