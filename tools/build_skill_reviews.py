#!/usr/bin/env python3
"""Build deterministic evidence-backed skill review status artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.reviews import build_status, dashboard, markdown_report


OUTPUT_JSON = ROOT / "registry" / "review-status.json"
OUTPUT_MD = ROOT / "docs" / "REVIEW_PACKET_v0.4.0.md"
OUTPUT_HTML = ROOT / "docs" / "SKILL_REVIEW_DASHBOARD.html"


def outputs(payload: Dict[str, object]) -> Dict[Path, str]:
    return {
        OUTPUT_JSON: json.dumps(payload, indent=2, sort_keys=True) + "\n",
        OUTPUT_MD: markdown_report(payload),
        OUTPUT_HTML: dashboard(payload),
    }


def stale_outputs(expected: Dict[Path, str]) -> List[str]:
    errors = []
    for path, content in expected.items():
        if not path.exists():
            errors.append(f"{path.relative_to(ROOT)} is missing")
        elif path.read_text(encoding="utf-8") != content:
            errors.append(
                f"{path.relative_to(ROOT)} is stale; run tools/build_skill_reviews.py"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the evidence-backed skill maturity review queue"
    )
    parser.add_argument("--release", default="v0.4.0", help="Review release")
    parser.add_argument("--check", action="store_true", help="Fail if outputs are stale")
    parser.add_argument("--json", action="store_true", help="Print status JSON")
    args = parser.parse_args()

    payload = build_status(ROOT, args.release)
    expected = outputs(payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1 if any(skill["validation_errors"] for skill in payload["skills"]) else 0
    if args.check:
        errors = stale_outputs(expected)
        errors.extend(
            f"{skill['bundle_path']}: {error}"
            for skill in payload["skills"]
            for error in skill["validation_errors"]
        )
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(
            f"Skill review status is current: {payload['candidate_count']} candidate(s), "
            f"{payload['promotion_ready_count']} promotion ready."
        )
        return 0

    for path, content in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
