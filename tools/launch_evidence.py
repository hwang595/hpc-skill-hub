#!/usr/bin/env python3
"""Print a local launch evidence report for maintainers and GitHub owners."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List

from launch_readiness import launch_checks


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


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def git_summary() -> Dict[str, str]:
    status = run_git(["status", "--short"])
    return {
        "branch": run_git(["rev-parse", "--abbrev-ref", "HEAD"]),
        "commit": run_git(["rev-parse", "--short", "HEAD"]),
        "status": "clean" if not status else "dirty",
    }


def build_evidence(owner: str | None, run_check: bool) -> Dict[str, Any]:
    index = load_json(INDEX_JSON)
    health = load_json(HEALTH_JSON)
    release = load_json(RELEASE_MANIFEST)
    checks = launch_checks(run_check, owner)

    return {
        "repository": "hpc-skill-hub",
        "release": release["version"],
        "git": git_summary(),
        "registry": {
            "skill_count": index["skill_count"],
            "collection_count": index["collection_count"],
            "site_adapter_count": index["site_adapter_count"],
            "uncollected_skill_count": len(health.get("uncollected_skill_ids", [])),
            "risk_counts": health["risk_counts"],
            "maturity_counts": health["maturity_counts"],
        },
        "release_manifest": {
            "path": str(RELEASE_MANIFEST.relative_to(ROOT)),
            "file_count": release["file_count"],
            "total_bytes": release["total_bytes"],
        },
        "readiness": [
            {"name": check.name, "status": check.status, "detail": check.detail}
            for check in checks
        ],
    }


def status_counts(checks: Iterable[Dict[str, str]]) -> Dict[str, int]:
    counts = {"OK": 0, "WARN": 0, "FAIL": 0}
    for check in checks:
        counts[check["status"]] = counts.get(check["status"], 0) + 1
    return counts


def markdown(evidence: Dict[str, Any]) -> str:
    readiness = evidence["readiness"]
    counts = status_counts(readiness)
    git = evidence["git"]
    registry = evidence["registry"]
    release_manifest = evidence["release_manifest"]

    lines = [
        "# HPC Skill Hub Launch Evidence",
        "",
        "This report is generated from the local checkout. It does not create a",
        "GitHub repository, push commits, edit settings, open issues, or publish a",
        "release.",
        "",
        "## Summary",
        "",
        f"- Repository: `{evidence['repository']}`",
        f"- Release target: `{evidence['release']}`",
        f"- Git branch: `{git['branch'] or 'unknown'}`",
        f"- Git commit: `{git['commit'] or 'unknown'}`",
        f"- Git status: `{git['status']}`",
        f"- Skills: {registry['skill_count']}",
        f"- Collections: {registry['collection_count']}",
        f"- Site adapters: {registry['site_adapter_count']}",
        f"- Uncollected skills: {registry['uncollected_skill_count']}",
        f"- Readiness checks: {counts.get('OK', 0)} OK, {counts.get('WARN', 0)} WARN, {counts.get('FAIL', 0)} FAIL",
        "",
        "## Registry",
        "",
        f"- Risk counts: {json.dumps(registry['risk_counts'], sort_keys=True)}",
        f"- Maturity counts: {json.dumps(registry['maturity_counts'], sort_keys=True)}",
        f"- Release manifest: `{release_manifest['path']}`",
        f"- Release manifest files: {release_manifest['file_count']}",
        f"- Release manifest bytes: {release_manifest['total_bytes']}",
        "",
        "## Readiness Checks",
        "",
        "| Status | Check | Detail |",
        "| --- | --- | --- |",
    ]

    for check in readiness:
        detail = check["detail"].replace("\n", " ")
        lines.append(f"| `{check['status']}` | `{check['name']}` | {detail} |")

    lines.extend(
        [
            "",
            "## Launch Notes",
            "",
            "- `WARN` entries are expected before first publication when no `origin`",
            "  remote exists or `gh` is unavailable in the local environment.",
            "- Treat any `FAIL` entry as a launch blocker until the underlying local",
            "  artifact or validation gate is fixed.",
            "- Attach this report to the launch issue or owner handoff after running it",
            "  from the final pre-launch commit.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print a local launch evidence report for HPC Skill Hub"
    )
    parser.add_argument(
        "--owner",
        help="Optional GitHub owner or organization used in readiness hints.",
    )
    parser.add_argument(
        "--run-check",
        action="store_true",
        help="Run make check as part of readiness evidence.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    evidence = build_evidence(args.owner, args.run_check)
    if args.json:
        print(json.dumps(evidence, indent=2, sort_keys=True))
    else:
        print(markdown(evidence))

    return 1 if any(check["status"] == "FAIL" for check in evidence["readiness"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
