#!/usr/bin/env python3
"""Validate rank, size, and host lines in a saved MPI hello log."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


RANK_RE = re.compile(r"^rank (\d+) of (\d+) on (\S+)\s*$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review a saved MPI hello output log.")
    parser.add_argument("--expected-ranks", type=int)
    parser.add_argument("--expected-hosts", type=int)
    parser.add_argument("log_file", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.log_file.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"error: cannot read {args.log_file}: {exc}")
        return 2

    records = [(int(rank), int(size), host) for rank, size, host in RANK_RE.findall(text)]
    if not records:
        print("error: no rank lines found")
        return 1

    sizes = {size for _, size, _ in records}
    rank_counts = Counter(rank for rank, _, _ in records)
    hosts = sorted({host for _, _, host in records})
    issues = []

    if len(sizes) != 1:
        issues.append(f"inconsistent communicator sizes: {sorted(sizes)}")
    else:
        size = next(iter(sizes))
        if args.expected_ranks is not None and size != args.expected_ranks:
            issues.append(
                f"communicator size {size} does not match expected {args.expected_ranks}"
            )
        expected = set(range(size))
        observed = set(rank_counts)
        missing = sorted(expected - observed)
        unexpected = sorted(observed - expected)
        duplicates = sorted(rank for rank, count in rank_counts.items() if count > 1)
        if missing:
            issues.append(f"missing ranks: {missing}")
        if unexpected:
            issues.append(f"unexpected ranks: {unexpected}")
        if duplicates:
            issues.append(f"duplicate ranks: {duplicates}")

    if args.expected_hosts is not None and len(hosts) != args.expected_hosts:
        issues.append(
            f"host count {len(hosts)} does not match expected {args.expected_hosts}"
        )

    print(f"rank_lines: {len(records)}")
    print(f"communicator_sizes: {sorted(sizes)}")
    print(f"hosts: {len(hosts)} ({', '.join(hosts)})")
    for issue in issues:
        print(f"error: {issue}")
    if issues:
        return 1

    print("validation: complete and internally consistent rank output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
