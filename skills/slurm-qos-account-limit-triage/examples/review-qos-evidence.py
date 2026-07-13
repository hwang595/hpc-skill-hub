#!/usr/bin/env python3
"""Review saved Slurm queue and visible QOS/account policy evidence."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}") from exc


def classify(reason: str) -> str:
    if reason.startswith("AssocGrp"):
        return "association-aggregate-limit"
    if reason.startswith("AssocMax"):
        return "association-per-job-limit"
    if reason.startswith("QOSGrp"):
        return "qos-aggregate-limit"
    if reason.startswith("QOSMax"):
        return "qos-per-job-limit"
    if reason in {"InvalidAccount", "InvalidQOS"}:
        return "invalid-association-or-qos"
    if reason == "Priority":
        return "priority"
    return "unclassified"


def main() -> int:
    parser = argparse.ArgumentParser(description="Review saved Slurm QOS evidence.")
    parser.add_argument("--queue", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    args = parser.parse_args()

    queue = read(args.queue)
    policy = read(args.policy)
    reasons = re.findall(r"\sPD\s.*\s([A-Za-z][A-Za-z0-9_]*)\s*$", queue, re.M)
    reason = reasons[0] if reasons else ""
    policy_fields = {
        name: name in policy for name in ("Account", "QOS", "GrpTRES", "Fairshare")
    }

    print(f"pending_reason: {reason or 'missing'}")
    print(f"reason_category: {classify(reason) if reason else 'missing'}")
    for name, present in policy_fields.items():
        print(f"policy_{name.lower()}: {'present' if present else 'missing'}")
    print("review: visible policy fields are evidence, not a complete policy or start-time promise")

    return 0 if reason and all(policy_fields.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
