#!/usr/bin/env python3
"""Summarize TensorBoard log directory shape without importing TensorBoard."""

from __future__ import annotations

import argparse
from pathlib import Path


EVENT_PATTERNS = ("events.out.tfevents", "tfevents")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize TensorBoard logdir contents")
    parser.add_argument("logdir", help="TensorBoard log directory")
    args = parser.parse_args()

    logdir = Path(args.logdir).expanduser()
    print(f"logdir={logdir}")

    if not logdir.exists():
        print("status=missing")
        return 1
    if not logdir.is_dir():
        print("status=not-a-directory")
        return 1

    files = [path for path in logdir.rglob("*") if path.is_file()]
    event_files = [
        path for path in files if any(pattern in path.name for pattern in EVENT_PATTERNS)
    ]

    print(f"file_count={len(files)}")
    print(f"event_file_count={len(event_files)}")
    for path in event_files[:10]:
        print(f"event_file={path}")

    if not event_files:
        print("warning=no-event-files-found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
