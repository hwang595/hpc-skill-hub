#!/usr/bin/env python3
"""Summarize files produced by the IOR/MDTest storage smoke example."""

from __future__ import annotations

import argparse
from pathlib import Path


SIGNAL_WORDS = (
    "error",
    "fail",
    "summary",
    "read",
    "write",
    "create",
    "stat",
    "remove",
    "Max",
    "Mean",
    "MiB/s",
    "IOPS",
)


def interesting_lines(path: Path) -> list[str]:
    lines: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [f"could_not_read={path}: {exc}"]

    for line in text.splitlines():
        if any(word in line for word in SIGNAL_WORDS):
            lines.append(line)
    return lines[-20:]


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize an IOR/MDTest smoke run")
    parser.add_argument("run_dir", help="Run directory created by ior-mdtest-smoke.sbatch")
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser()
    print(f"run_dir={run_dir}")

    marker = run_dir / ".hpc-skill-ior-mdtest-smoke"
    if not run_dir.exists():
        print("status=missing")
        return 1
    if not run_dir.is_dir():
        print("status=not-a-directory")
        return 1
    if not marker.exists():
        print("status=marker-missing")
        return 1

    files = sorted(path for path in run_dir.rglob("*") if path.is_file())
    print(f"file_count={len(files)}")
    required = ("run-metadata.txt", "commands.txt", "ior.out", "mdtest.out")
    missing = []
    for name in required:
        path = run_dir / name
        status = "present" if path.exists() else "missing"
        print(f"{name}={status}")
        if status == "missing":
            missing.append(name)

    if missing:
        print(f"status=incomplete; missing={','.join(missing)}")
        return 1

    for output_name in ("ior.out", "mdtest.out"):
        path = run_dir / output_name
        if path.exists():
            print(f"== {output_name} signals ==")
            for line in interesting_lines(path):
                print(line)

    print("status=complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
