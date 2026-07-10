#!/usr/bin/env python3
"""Repository wrapper for the installable skill security scanner."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.security import main


if __name__ == "__main__":
    raise SystemExit(main())
