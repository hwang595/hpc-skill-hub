#!/usr/bin/env python3
"""Sync generated registry data into the installable Python package."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "src" / "hpc_skill_hub" / "data"
FILES: List[Tuple[Path, Path]] = [
    (
        ROOT / "registry" / filename,
        PACKAGE_ROOT / "registry" / filename,
    )
    for filename in (
        "index.json",
        "health.json",
        "community-pilot-v0.6.0.json",
        "release-status.json",
        "review-status.json",
        "skill-context.json",
    )
] + [
    (
        ROOT / "registry" / "provenance" / "v0.6.0.json",
        PACKAGE_ROOT / "registry" / "release-provenance.json",
    ),
    (
        ROOT / "integrations" / "mcp-client.json",
        PACKAGE_ROOT / "integrations" / "mcp-client.json",
    ),
    (
        ROOT / "security" / "policies" / "community-default.json",
        PACKAGE_ROOT / "security" / "community-default.json",
    ),
]


def stale_files(files: Iterable[Tuple[Path, Path]]) -> List[str]:
    stale: List[str] = []
    for source, output in files:
        if not source.exists():
            stale.append(f"{source.relative_to(ROOT)} is missing")
            continue
        if not output.exists():
            stale.append(f"{output.relative_to(ROOT)} is missing")
            continue
        if not filecmp.cmp(source, output, shallow=False):
            stale.append(
                f"{output.relative_to(ROOT)} is stale; run tools/build_package_data.py"
            )
    return stale


def sync_files(files: Iterable[Tuple[Path, Path]]) -> None:
    for source, output in files:
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, output)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync registry JSON files into the installable package"
    )
    parser.add_argument("--check", action="store_true", help="Fail if package data is stale")
    args = parser.parse_args()

    if args.check:
        errors = stale_files(FILES)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("Package registry data is current.")
        return 0

    sync_files(FILES)
    print(f"Wrote {len(FILES)} package data artifact(s) in {PACKAGE_ROOT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
