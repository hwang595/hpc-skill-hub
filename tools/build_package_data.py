#!/usr/bin/env python3
"""Sync generated registry data into the installable Python package."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "registry"
PACKAGE_DATA_DIR = ROOT / "src" / "hpc_skill_hub" / "data" / "registry"
FILES = ["index.json", "health.json"]


def source_path(filename: str) -> Path:
    return SOURCE_DIR / filename


def output_path(filename: str) -> Path:
    return PACKAGE_DATA_DIR / filename


def stale_files(files: Iterable[str]) -> List[str]:
    stale: List[str] = []
    for filename in files:
        source = source_path(filename)
        output = output_path(filename)
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


def sync_files(files: Iterable[str]) -> None:
    PACKAGE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for filename in files:
        shutil.copyfile(source_path(filename), output_path(filename))


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
    print(f"Wrote package registry data in {PACKAGE_DATA_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
