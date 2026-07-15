#!/usr/bin/env python3
"""Create and verify deterministic community intake receipts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.intake_receipt import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
