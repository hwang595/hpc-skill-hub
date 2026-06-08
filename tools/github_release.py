#!/usr/bin/env python3
"""Print GitHub CLI commands for publishing a release."""

from __future__ import annotations

import argparse
import shlex
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]


def shell_join(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def notes_path_for_version(version: str) -> Path:
    normalized = version.removeprefix("v")
    return ROOT / "docs" / f"RELEASE_NOTES_v{normalized}.md"


def manifest_path_for_version(version: str) -> Path:
    tag = version if version.startswith("v") else f"v{version}"
    return ROOT / "registry" / "releases" / f"{tag}.json"


def release_commands(version: str, repo: str | None) -> List[List[str]]:
    tag = version if version.startswith("v") else f"v{version}"
    notes_path = notes_path_for_version(tag)
    manifest_path = manifest_path_for_version(tag)
    if not notes_path.exists():
        raise FileNotFoundError(f"release notes not found: {notes_path.relative_to(ROOT)}")
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"release manifest not found: {manifest_path.relative_to(ROOT)}"
        )

    commands = [
        ["git", "tag", "-a", tag, "-m", f"{tag} seed release"],
        ["git", "push", "origin", tag],
        [
            "gh",
            "release",
            "create",
            tag,
            str(manifest_path.relative_to(ROOT)),
            "--title",
            tag,
            "--notes-file",
            str(notes_path.relative_to(ROOT)),
        ],
    ]
    if repo:
        commands[-1].extend(["--repo", repo])
    return commands


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print GitHub CLI commands for creating a release"
    )
    parser.add_argument("version", help="Release version, for example v0.1.0 or 0.1.0.")
    parser.add_argument(
        "--repo",
        help="Optional GitHub repository in owner/name form for gh --repo.",
    )
    args = parser.parse_args()

    for command in release_commands(args.version, args.repo):
        print(shell_join(command))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
