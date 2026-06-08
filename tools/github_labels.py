#!/usr/bin/env python3
"""Print GitHub CLI commands for labels defined in .github/labels.json."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
LABELS_JSON = ROOT / ".github" / "labels.json"


def load_labels() -> List[Dict[str, Any]]:
    with LABELS_JSON.open(encoding="utf-8") as handle:
        labels = json.load(handle)
    return labels


def command_for_label(label: Dict[str, Any], repo: str | None) -> List[str]:
    command = [
        "gh",
        "label",
        "create",
        label["name"],
        "--color",
        label["color"],
        "--description",
        label["description"],
        "--force",
    ]
    if repo:
        command.extend(["--repo", repo])
    return command


def shell_join(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print GitHub CLI commands for the repository label set"
    )
    parser.add_argument(
        "--repo",
        help="Optional GitHub repository in owner/name form for gh --repo.",
    )
    args = parser.parse_args()

    for label in load_labels():
        print(shell_join(command_for_label(label, args.repo)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
