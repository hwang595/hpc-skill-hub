#!/usr/bin/env python3
"""Print an ordered GitHub publication plan for HPC Skill Hub."""

from __future__ import annotations

import argparse
from typing import Iterable, List

from github_issues import command_for_issue, load_seed_issues
from github_labels import command_for_label, load_labels
from github_milestones import command_for_milestone, load_milestones
from github_release import release_commands
from github_repo import create_command, edit_commands, load_repository, shell_join
from github_rulesets import command_for_ruleset, iter_ruleset_paths, load_ruleset
from launch_readiness import launch_checks


DISCUSSION_FORMS = [
    ("Adoption", "adoption", ".github/DISCUSSION_TEMPLATE/adoption.yml"),
    (
        "Skill coverage",
        "skill-coverage",
        ".github/DISCUSSION_TEMPLATE/skill-coverage.yml",
    ),
    ("Site adapters", "site-adapters", ".github/DISCUSSION_TEMPLATE/site-adapters.yml"),
    (
        "Review process",
        "review-process",
        ".github/DISCUSSION_TEMPLATE/review-process.yml",
    ),
    ("Integrations", "integrations", ".github/DISCUSSION_TEMPLATE/integrations.yml"),
]


def print_section(title: str) -> None:
    print()
    print(f"## {title}")


def print_commands(commands: Iterable[List[str]]) -> None:
    for command in commands:
        print(shell_join(command))


def repo_slug(owner: str, repo_name: str) -> str:
    return f"{owner}/{repo_name}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print an ordered, reviewable plan for publishing the repository on GitHub"
    )
    parser.add_argument(
        "--owner",
        required=True,
        help="GitHub user or organization that will own the public repository.",
    )
    parser.add_argument(
        "--version",
        default="v0.1.0",
        help="Release version to include in the plan. Default: v0.1.0.",
    )
    parser.add_argument(
        "--run-check",
        action="store_true",
        help="Run make check while summarizing current local readiness.",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Omit --push from the repository creation command.",
    )
    args = parser.parse_args()

    metadata = load_repository()
    repo = repo_slug(args.owner, metadata["name"])

    print("# HPC Skill Hub GitHub Publish Plan")
    print(f"# Repository: {repo}")
    print(f"# Release: {args.version}")
    print("# Review commands before running them in an authenticated GitHub environment.")

    print_section("1. Local readiness")
    readiness_command = ["python3", "tools/launch_readiness.py", "--owner", args.owner]
    if args.run_check:
        readiness_command.append("--run-check")
    print(shell_join(readiness_command))
    print()
    for check in launch_checks(args.run_check, args.owner):
        print(f"# {check.status:4} {check.name}: {check.detail}")

    print_section("2. Review public launch packet and owner checklist")
    print("# Share docs/PUBLIC_LAUNCH_PACKET.md with the GitHub owner,")
    print("# and complete docs/GITHUB_OWNER_CHECKLIST.md before running networked commands.")

    print_section("3. Create repository and push seed branch")
    print(shell_join(["git", "branch", "-M", metadata["default_branch"]]))
    print(shell_join(create_command(metadata, args.owner, not args.no_push)))
    print_commands(edit_commands(metadata, args.owner))

    print_section("4. Configure labels")
    print_commands(command_for_label(label, repo) for label in load_labels())

    print_section("5. Configure milestones")
    print_commands(
        command_for_milestone(milestone, repo) for milestone in load_milestones()
    )

    print_section("6. Configure discussion categories")
    print("# Create GitHub Discussions categories matching these template slugs:")
    for name, slug, path in DISCUSSION_FORMS:
        print(f"# - {name}: slug `{slug}`, form {path}")

    print_section("7. Open starter issues")
    for issue in load_seed_issues():
        print(shell_join(command_for_issue(issue, repo)))
        if issue.get("pin"):
            print(f"# Pin the issue created from {issue['body']}.")

    print_section(
        "8. Apply branch rulesets after first green Validate and Package workflows"
    )
    for path in iter_ruleset_paths():
        load_ruleset(path)
        print(shell_join(command_for_ruleset(path, repo)))

    print_section("9. Publish first release after CI and Pages are green")
    print_commands(release_commands(args.version, repo))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
