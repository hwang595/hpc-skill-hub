#!/usr/bin/env python3
"""Print GitHub CLI commands for linking Pages as the repository homepage."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from github_repo import shell_join


def pages_url_command(repo: str) -> List[str]:
    return ["gh", "api", f"repos/{repo}/pages", "--jq", ".html_url"]


def set_homepage_command(repo: str, pages_url: str) -> List[str]:
    return ["gh", "repo", "edit", repo, "--homepage", pages_url]


def command_records(repo: str, pages_url: str | None) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    if not pages_url:
        records.append(
            {
                "purpose": "inspect_pages_url",
                "command": pages_url_command(repo),
            }
        )
    records.append(
        {
            "purpose": "set_repository_homepage",
            "command": set_homepage_command(repo, pages_url or "<pages-url>"),
        }
    )
    for record in records:
        record["shell"] = shell_join(record["command"])
    return records


def print_commands(repo: str, pages_url: str | None) -> None:
    print("# HPC Skill Hub Repository Homepage Commands")
    if pages_url:
        print("# Set the repository homepage to the deployed GitHub Pages URL.")
    else:
        print("# Inspect the deployed GitHub Pages URL, then set it as the repository homepage.")
    for record in command_records(repo, pages_url):
        if record["purpose"] == "set_repository_homepage" and not pages_url:
            print("# Replace <pages-url> with the URL printed above.")
        print(record["shell"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print GitHub CLI commands for linking Pages as the repository homepage"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository in owner/name form.",
    )
    parser.add_argument(
        "--pages-url",
        help="Known GitHub Pages URL. When omitted, print the command to inspect it.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output.",
    )
    args = parser.parse_args()

    records = command_records(args.repo, args.pages_url)
    if args.json:
        print(
            json.dumps(
                {
                    "repo": args.repo,
                    "pages_url": args.pages_url,
                    "commands": records,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print_commands(args.repo, args.pages_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
