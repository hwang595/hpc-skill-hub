#!/usr/bin/env python3
"""Review saved Slurm job-record and output-path evidence."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Review saved Slurm output-log evidence.")
    parser.add_argument("--job-record", required=True, type=Path)
    parser.add_argument("--filesystem", required=True, type=Path)
    args = parser.parse_args()

    job_record = read(args.job_record)
    filesystem = read(args.filesystem)
    fields = {
        name: bool(re.search(rf"\b{name}=\S+", job_record))
        for name in ("WorkDir", "StdOut", "StdErr", "Command")
    }
    rows = list(csv.DictReader(filesystem.splitlines(), delimiter="|"))
    missing = [row for row in rows if row.get("exists") == "no"]
    empty = [
        row for row in rows if row.get("exists") == "yes" and row.get("size") == "0"
    ]

    for name, present in fields.items():
        print(f"job_record_{name.lower()}: {'present' if present else 'missing'}")
    print(f"missing_path_records: {len(missing)}")
    print(f"empty_file_records: {len(empty)}")
    print("review: resolve paths against WorkDir, then separate missing files from empty output")

    return 0 if all(fields.values()) and (missing or empty) else 1


if __name__ == "__main__":
    raise SystemExit(main())
