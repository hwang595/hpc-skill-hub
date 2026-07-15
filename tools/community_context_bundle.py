#!/usr/bin/env python3
"""Build and inspect review-gated community context bundles."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.cli import build_parser  # noqa: E402


def main() -> int:
    args = build_parser().parse_args(["community-context", *sys.argv[1:]])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
