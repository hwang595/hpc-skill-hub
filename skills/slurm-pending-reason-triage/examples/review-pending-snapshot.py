#!/usr/bin/env python3
"""Classify reasons in saved Slurm queue or job snapshots."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DETAIL_REASON_RE = re.compile(r"\bReason=([A-Za-z][A-Za-z0-9_]*)")
TABLE_REASON_RE = re.compile(r"\sPD\s.*\s\(?([A-Za-z][A-Za-z0-9_]*)\)?\s*$")


def reason_category(reason: str) -> str:
    if reason.startswith("Dependency"):
        return "dependency"
    if reason == "Priority":
        return "priority"
    if reason == "Resources":
        return "resources"
    if reason.startswith(("Assoc", "QOS", "Max")):
        return "policy-limit"
    if any(term in reason for term in ("Node", "Partition", "Reservation")):
        return "availability-or-policy"
    return "unclassified"


def extract_reasons(text: str) -> list[str]:
    reasons = DETAIL_REASON_RE.findall(text)
    for line in text.splitlines():
        match = TABLE_REASON_RE.search(line)
        if match:
            reasons.append(match.group(1))
    return list(dict.fromkeys(reasons))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify reason fields in saved public-safe Slurm snapshots."
    )
    parser.add_argument("snapshots", nargs="+", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing_reason = False
    for path in args.snapshots:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"error: cannot read {path}: {exc}")
            return 2

        reasons = extract_reasons(text)
        if not reasons:
            print(f"{path}: no pending reason found")
            missing_reason = True
            continue
        for reason in reasons:
            print(f"{path}: {reason} -> {reason_category(reason)}")

    print("review: reason classes are point-in-time evidence, not start-time promises")
    return 1 if missing_reason else 0


if __name__ == "__main__":
    raise SystemExit(main())
