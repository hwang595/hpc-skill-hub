#!/usr/bin/env python3
"""Print proposal evidence for adopting HPC Skill Hub as an open ecosystem."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List

from launch_readiness import launch_checks
from review_candidates import build_payload as build_review_candidate_payload


ROOT = Path(__file__).resolve().parents[1]
INDEX_JSON = ROOT / "registry" / "index.json"
HEALTH_JSON = ROOT / "registry" / "health.json"
RELEASE_MANIFEST = ROOT / "registry" / "releases" / "v0.5.0.json"


def run_git(parts: List[str]) -> str:
    result = subprocess.run(
        ["git", *parts],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def git_summary() -> Dict[str, str]:
    status = run_git(["status", "--short"])
    return {
        "branch": run_git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "commit": run_git(["rev-parse", "--short", "HEAD"]),
        "status": "clean" if not status else "dirty",
    }


def status_counts(checks: Iterable[Dict[str, str]]) -> Dict[str, int]:
    counts = {"OK": 0, "WARN": 0, "FAIL": 0}
    for check in checks:
        counts[check["status"]] = counts.get(check["status"], 0) + 1
    return counts


def top_counts(counts: Dict[str, int], limit: int) -> List[Dict[str, Any]]:
    return [
        {"name": name, "count": count}
        for name, count in sorted(
            counts.items(), key=lambda item: (-item[1], item[0])
        )[:limit]
    ]


def workflow_count() -> int:
    return len(list((ROOT / ".github" / "workflows").glob("*.yml")))


def discussion_template_count() -> int:
    return len(list((ROOT / ".github" / "DISCUSSION_TEMPLATE").glob("*.yml")))


def build_evidence(
    owner: str | None, run_check: bool, review_limit: int
) -> Dict[str, Any]:
    index = load_json(INDEX_JSON)
    health = load_json(HEALTH_JSON)
    release = load_json(RELEASE_MANIFEST)
    labels = load_json(ROOT / ".github" / "labels.json")
    seed_issues = load_json(ROOT / ".github" / "seed_issues.json")
    milestones = load_json(ROOT / ".github" / "milestones.json")
    checks = [
        {"name": check.name, "status": check.status, "detail": check.detail}
        for check in launch_checks(run_check, owner)
    ]
    review = build_review_candidate_payload(review_limit, None)

    return {
        "repository": "hpc-skill-hub",
        "release": release["version"],
        "git": git_summary(),
        "registry": {
            "skill_count": index["skill_count"],
            "collection_count": index["collection_count"],
            "site_adapter_count": index["site_adapter_count"],
            "category_count": len(index["categories"]),
            "scheduler_count": len(index["schedulers"]),
            "tool_count": len(index["tools"]),
            "risk_counts": health["risk_counts"],
            "maturity_counts": health["maturity_counts"],
            "uncollected_skill_count": len(health.get("uncollected_skill_ids", [])),
            "top_categories": top_counts(index["categories"], 8),
        },
        "community": {
            "label_count": len(labels),
            "seed_issue_count": len(seed_issues),
            "discussion_template_count": discussion_template_count(),
            "milestone_count": len(milestones),
            "workflow_count": workflow_count(),
        },
        "reviewed_skill_pilot": {
            "candidate_count": review["candidate_count"],
            "risk_counts": review["risk_counts"],
            "candidates": review["candidates"],
        },
        "release_manifest": {
            "path": str(RELEASE_MANIFEST.relative_to(ROOT)),
            "file_count": release["file_count"],
            "total_bytes": release["total_bytes"],
        },
        "readiness": {
            "counts": status_counts(checks),
            "checks": checks,
        },
        "next_actions": [
            "Create the public GitHub repository and push main.",
            "Confirm Validate, Package, and Pages workflows are green.",
            "Link the generated Pages URL from the repository homepage.",
            "Open starter issues, including the reviewed-skill pilot issue.",
            "Recruit domain reviewers and site-adapter reviewers.",
            "Use public evidence to promote the first seed skills to reviewed.",
        ],
    }


def escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def markdown(evidence: Dict[str, Any]) -> str:
    git = evidence["git"]
    registry = evidence["registry"]
    community = evidence["community"]
    readiness = evidence["readiness"]
    review = evidence["reviewed_skill_pilot"]
    release_manifest = evidence["release_manifest"]

    lines = [
        "# HPC Skill Hub Proposal Evidence",
        "",
        "This report is generated from the local checkout. It is designed for",
        "open-source proposal packets, owner handoffs, and ecosystem sponsor",
        "reviews. It does not create a repository, push commits, open issues,",
        "edit settings, or publish a release.",
        "",
        "## Executive Summary",
        "",
        f"- Repository: `{evidence['repository']}`",
        f"- Release target: `{evidence['release']}`",
        f"- Git branch: `{git['branch'] or 'unknown'}`",
        f"- Git commit: `{git['commit'] or 'unknown'}`",
        f"- Git status: `{git['status']}`",
        f"- Skills: {registry['skill_count']}",
        f"- Collections: {registry['collection_count']}",
        f"- Site adapters: {registry['site_adapter_count']}",
        f"- Readiness checks: {readiness['counts']['OK']} OK, {readiness['counts']['WARN']} WARN, {readiness['counts']['FAIL']} FAIL",
        "",
        "## Registry Coverage",
        "",
        f"- Risk counts: {json.dumps(registry['risk_counts'], sort_keys=True)}",
        f"- Maturity counts: {json.dumps(registry['maturity_counts'], sort_keys=True)}",
        f"- Uncollected skills: {registry['uncollected_skill_count']}",
        f"- Category count: {registry['category_count']}",
        f"- Scheduler count: {registry['scheduler_count']}",
        f"- Tool count: {registry['tool_count']}",
        f"- Release manifest: `{release_manifest['path']}`",
        f"- Release manifest files: {release_manifest['file_count']}",
        "",
        "| Top Category | Skills |",
        "| --- | ---: |",
    ]

    for category in registry["top_categories"]:
        lines.append(f"| `{category['name']}` | {category['count']} |")

    lines.extend(
        [
            "",
            "## Community Assets",
            "",
            f"- Labels: {community['label_count']}",
            f"- Starter issues: {community['seed_issue_count']}",
            f"- Discussion templates: {community['discussion_template_count']}",
            f"- Milestones: {community['milestone_count']}",
            f"- GitHub workflows: {community['workflow_count']}",
            "",
            "## Reviewed Skill Pilot",
            "",
            f"- Candidate pool: {review['candidate_count']}",
            f"- Candidate risk counts: {json.dumps(review['risk_counts'], sort_keys=True)}",
            "",
            "| Skill | Risk | Review Focus | Collections |",
            "| --- | --- | --- | --- |",
        ]
    )

    for candidate in review["candidates"]:
        collections = ", ".join(candidate["collections"])
        lines.append(
            "| "
            f"`{candidate['id']}` | "
            f"`{candidate['risk_level']}` | "
            f"{escape_table(candidate['review_focus'])} | "
            f"{escape_table(collections)} |"
        )

    lines.extend(
        [
            "",
            "## Launch Readiness",
            "",
            "| Status | Check | Detail |",
            "| --- | --- | --- |",
        ]
    )

    for check in readiness["checks"]:
        detail = check["detail"].replace("\n", " ")
        lines.append(f"| `{check['status']}` | `{check['name']}` | {escape_table(detail)} |")

    lines.extend(
        [
            "",
            "## Proposal Use",
            "",
            "- Attach this report to an open-source proposal, launch decision record,",
            "  or sponsoring-organization handoff.",
            "- Treat `FAIL` readiness checks as local blockers before publication.",
            "- Treat `WARN` readiness checks as external setup or human follow-up",
            "  unless the detail says otherwise.",
            "- Use the reviewed-skill pilot table to recruit the first domain",
            "  reviewers without hard-coding a stale candidate list in the proposal.",
            "",
            "## Next Actions",
            "",
        ]
    )

    for action in evidence["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print proposal evidence for HPC Skill Hub open ecosystem adoption"
    )
    parser.add_argument(
        "--owner",
        help="Optional GitHub owner or organization used in readiness hints.",
    )
    parser.add_argument(
        "--run-check",
        action="store_true",
        help="Run make check while building readiness evidence.",
    )
    parser.add_argument(
        "--review-limit",
        type=int,
        default=8,
        help="Number of reviewed-skill pilot candidates to include.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    if args.review_limit < 1:
        parser.error("--review-limit must be at least 1")

    evidence = build_evidence(args.owner, args.run_check, args.review_limit)
    if args.json:
        print(json.dumps(evidence, indent=2, sort_keys=True))
    else:
        print(markdown(evidence))
    return 1 if evidence["readiness"]["counts"].get("FAIL", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
