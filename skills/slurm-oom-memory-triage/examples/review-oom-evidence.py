#!/usr/bin/env python3
"""Review saved Slurm accounting and log evidence for OOM signals."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


LOG_SIGNALS = {
    "oom-kill": r"oom-kill|out[ _-]?of[ _-]?memory",
    "killed-process": r"worker.*killed|killed by signal|cannot allocate memory",
    "allocator": r"bad_alloc|memoryerror|java heap|allocator",
}


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Review saved Slurm OOM evidence.")
    parser.add_argument("--accounting", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--require-both", action="store_true")
    args = parser.parse_args()

    accounting = read(args.accounting)
    log = read(args.log)
    rows = list(csv.DictReader(accounting.splitlines(), delimiter="|"))
    oom_rows = [row for row in rows if "OUT_OF_MEMORY" in (row.get("State") or "")]
    requested = sorted({row.get("ReqMem") for row in rows if row.get("ReqMem")})
    observed = sorted({row.get("MaxRSS") for row in rows if row.get("MaxRSS")})
    log_signals = [
        label for label, pattern in LOG_SIGNALS.items() if re.search(pattern, log, re.I)
    ]

    print(f"scheduler_oom_rows: {len(oom_rows)}")
    print(f"requested_memory_values: {', '.join(requested) or 'missing'}")
    print(f"maxrss_values: {', '.join(observed) or 'missing'}")
    print(f"application_log_signals: {', '.join(log_signals) or 'none'}")
    print("review: compare request scope, job steps, MaxRSS, and log evidence before changing memory")

    scheduler_evidence = bool(oom_rows)
    application_evidence = bool(log_signals)
    if args.require_both:
        return 0 if scheduler_evidence and application_evidence else 1
    return 0 if scheduler_evidence or application_evidence else 1


if __name__ == "__main__":
    raise SystemExit(main())
