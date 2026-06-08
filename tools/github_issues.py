#!/usr/bin/env python3
"""Print GitHub CLI commands for seed community issues."""

from __future__ import annotations

import argparse
import json
import re
import shlex
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
SEED_ISSUES_JSON = ROOT / ".github" / "seed_issues.json"

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LABEL_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def shell_join(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def load_seed_issues() -> List[Dict[str, Any]]:
    with SEED_ISSUES_JSON.open(encoding="utf-8") as handle:
        issues = json.load(handle)
    if not isinstance(issues, list):
        raise ValueError(".github/seed_issues.json must contain a list")
    return issues


def validate_issue(issue: Dict[str, Any]) -> None:
    required = {"id", "title", "labels", "body", "pin"}
    missing = sorted(required - set(issue))
    if missing:
        raise ValueError(f"seed issue missing field(s): {', '.join(missing)}")

    if not isinstance(issue["id"], str) or not ID_RE.match(issue["id"]):
        raise ValueError(f"invalid seed issue id: {issue['id']!r}")
    if not isinstance(issue["title"], str) or not issue["title"].strip():
        raise ValueError(f"seed issue {issue['id']} has an empty title")
    if not isinstance(issue["labels"], list) or not issue["labels"]:
        raise ValueError(f"seed issue {issue['id']} must include labels")
    for label in issue["labels"]:
        if not isinstance(label, str) or not LABEL_RE.match(label):
            raise ValueError(f"seed issue {issue['id']} has invalid label {label!r}")
    if not isinstance(issue["body"], str):
        raise ValueError(f"seed issue {issue['id']} body must be a path")
    relative_body_path = Path(issue["body"])
    body_path = ROOT / relative_body_path
    if relative_body_path.is_absolute() or ".." in relative_body_path.parts:
        raise ValueError(f"seed issue {issue['id']} body must stay inside the repo")
    if not body_path.exists():
        raise FileNotFoundError(f"seed issue body not found: {issue['body']}")
    if not isinstance(issue["pin"], bool):
        raise ValueError(f"seed issue {issue['id']} pin must be boolean")


def command_for_issue(issue: Dict[str, Any], repo: str | None) -> List[str]:
    validate_issue(issue)
    command = [
        "gh",
        "issue",
        "create",
        "--title",
        issue["title"],
        "--body-file",
        issue["body"],
    ]
    for label in issue["labels"]:
        command.extend(["--label", label])
    if repo:
        command.extend(["--repo", repo])
    return command


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print GitHub CLI commands for starter community issues"
    )
    parser.add_argument(
        "--repo",
        help="Optional GitHub repository in owner/name form for gh --repo.",
    )
    parser.add_argument(
        "--include-pin-notes",
        action="store_true",
        help="Print comments for seed issues that maintainers should pin.",
    )
    args = parser.parse_args()

    for issue in load_seed_issues():
        print(shell_join(command_for_issue(issue, args.repo)))
        if args.include_pin_notes and issue.get("pin"):
            print(f"# Pin the issue created from {issue['body']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
