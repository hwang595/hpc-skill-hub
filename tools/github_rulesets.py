#!/usr/bin/env python3
"""Print GitHub CLI commands for repository rulesets."""

from __future__ import annotations

import argparse
import json
import shlex
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
RULESETS_DIR = ROOT / ".github" / "rulesets"


def load_ruleset(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def iter_ruleset_paths() -> List[Path]:
    return sorted(RULESETS_DIR.glob("*.json"))


def shell_join(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def command_for_ruleset(path: Path, repo: str) -> List[str]:
    return [
        "gh",
        "api",
        "-X",
        "POST",
        f"repos/{repo}/rulesets",
        "--input",
        str(path.relative_to(ROOT)),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print GitHub CLI commands for repository rulesets"
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository in owner/name form.",
    )
    args = parser.parse_args()

    for path in iter_ruleset_paths():
        load_ruleset(path)
        print(shell_join(command_for_ruleset(path, args.repo)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
