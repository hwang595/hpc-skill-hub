#!/usr/bin/env python3
"""Print GitHub CLI commands for repository milestones."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
MILESTONES_JSON = ROOT / ".github" / "milestones.json"


def shell_join(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def load_milestones() -> List[Dict[str, Any]]:
    with MILESTONES_JSON.open(encoding="utf-8") as handle:
        milestones = json.load(handle)
    if not isinstance(milestones, list):
        raise ValueError(".github/milestones.json must contain a list")
    return milestones


def validate_milestone(milestone: Dict[str, Any]) -> None:
    required = {"title", "description", "state"}
    missing = sorted(required - set(milestone))
    if missing:
        raise ValueError(f"milestone missing field(s): {', '.join(missing)}")
    if not isinstance(milestone["title"], str) or not milestone["title"].strip():
        raise ValueError("milestone title must be a non-empty string")
    if (
        not isinstance(milestone["description"], str)
        or len(milestone["description"].strip()) < 20
    ):
        raise ValueError(f"milestone {milestone['title']!r} has a short description")
    if milestone["state"] not in {"open", "closed"}:
        raise ValueError(f"milestone {milestone['title']!r} has invalid state")


def command_for_milestone(milestone: Dict[str, Any], repo: str) -> List[str]:
    validate_milestone(milestone)
    return [
        "gh",
        "api",
        "-X",
        "POST",
        f"repos/{repo}/milestones",
        "-f",
        f"title={milestone['title']}",
        "-f",
        f"description={milestone['description']}",
        "-f",
        f"state={milestone['state']}",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print GitHub CLI commands for repository milestones"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository in owner/name form.",
    )
    args = parser.parse_args()

    for milestone in load_milestones():
        print(shell_join(command_for_milestone(milestone, args.repo)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
