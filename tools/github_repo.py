#!/usr/bin/env python3
"""Print GitHub CLI commands from .github/repository.json."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_JSON = ROOT / ".github" / "repository.json"


def load_repository() -> Dict[str, Any]:
    with REPOSITORY_JSON.open(encoding="utf-8") as handle:
        return json.load(handle)


def shell_join(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def create_command(metadata: Dict[str, Any], owner: str | None, push: bool) -> List[str]:
    repo_name = metadata["name"]
    repo = f"{owner}/{repo_name}" if owner else repo_name
    command = [
        "gh",
        "repo",
        "create",
        repo,
        f"--{metadata['visibility']}",
        "--source=.",
        "--remote=origin",
        "--description",
        metadata["description"],
    ]
    if push:
        command.append("--push")
    return command


def edit_commands(metadata: Dict[str, Any], owner: str | None) -> List[List[str]]:
    repo_name = metadata["name"]
    repo = f"{owner}/{repo_name}" if owner else repo_name
    features = metadata["features"]
    commands = [
        [
            "gh",
            "repo",
            "edit",
            repo,
            "--description",
            metadata["description"],
            "--enable-issues" if features["issues"] else "--disable-issues",
            "--enable-projects" if features["projects"] else "--disable-projects",
            "--enable-wiki" if features["wiki"] else "--disable-wiki",
        ],
        [
            "gh",
            "repo",
            "edit",
            repo,
            "--add-topic",
            ",".join(metadata["topics"]),
        ],
    ]
    if features["discussions"]:
        commands.append(
            [
                "gh",
                "api",
                "-X",
                "PATCH",
                f"repos/{repo}",
                "-f",
                "has_discussions=true",
            ]
        )
    return commands


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print GitHub CLI commands for repository creation and metadata"
    )
    parser.add_argument(
        "--owner",
        help="Optional GitHub owner or organization. When omitted, gh uses the authenticated account.",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Omit --push from the gh repo create command.",
    )
    args = parser.parse_args()

    metadata = load_repository()
    print(shell_join(["git", "branch", "-M", metadata["default_branch"]]))
    print(shell_join(create_command(metadata, args.owner, not args.no_push)))
    for command in edit_commands(metadata, args.owner):
        print(shell_join(command))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
