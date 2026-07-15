#!/usr/bin/env python3
"""Build and verify community review and adoption evidence."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.community_evidence import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
