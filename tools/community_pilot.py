#!/usr/bin/env python3
"""Build or check the deterministic v0.6 community intake pilot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.community_pilot import (  # noqa: E402
    CommunityPilotError,
    build_pilot_report,
    render_pilot_report,
    serialized_report,
)


FIXTURES = ROOT / "tests" / "fixtures" / "community-pilot"
JSON_OUTPUT = ROOT / "registry" / "community-pilot-v0.6.0.json"
DOC_OUTPUT = ROOT / "docs" / "COMMUNITY_PILOT_v0.6.0.md"


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the deterministic v0.6 community intake pilot report"
    )
    parser.add_argument("--check", action="store_true", help="Fail when generated outputs are stale")
    parser.add_argument("--json", action="store_true", help="Print the generated JSON without writing")
    args = parser.parse_args()

    try:
        report = build_pilot_report(FIXTURES)
        expected_json = serialized_report(report)
        expected_doc = render_pilot_report(report)
    except (CommunityPilotError, KeyError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(expected_json, end="")
        return 0
    if args.check:
        stale = []
        for path, expected in ((JSON_OUTPUT, expected_json), (DOC_OUTPUT, expected_doc)):
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                stale.append(_relative(path))
        if stale:
            print("ERROR: stale community pilot output: " + ", ".join(stale), file=sys.stderr)
            return 1
        print(
            f"Community pilot is current: {report['matrix']['passed_count']}/"
            f"{report['matrix']['case_count']} cases passed."
        )
        return 0

    JSON_OUTPUT.write_text(expected_json, encoding="utf-8")
    DOC_OUTPUT.write_text(expected_doc, encoding="utf-8")
    print(f"Wrote {_relative(JSON_OUTPUT)}")
    print(f"Wrote {_relative(DOC_OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
