#!/usr/bin/env python3
"""Review saved path traversal, ACL, and permission-log evidence."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def read_optional(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Review saved permission evidence.")
    parser.add_argument("--namei", type=Path)
    parser.add_argument("--acl", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--require-all", action="store_true")
    args = parser.parse_args()
    if not any((args.namei, args.acl, args.log)):
        parser.error("provide at least one of --namei, --acl, or --log")

    namei = read_optional(args.namei)
    acl = read_optional(args.acl)
    log = read_optional(args.log)
    signals = {
        "blocked_traversal": bool(re.search(r"^\s*d---------\s", namei, re.M)),
        "restrictive_acl_mask": "mask::r--" in acl and "effective:r--" in acl,
        "application_denied": bool(
            re.search(r"permission denied|operation not permitted|access denied", log, re.I)
        ),
    }

    for name, present in signals.items():
        print(f"{name}: {'present' if present else 'not observed'}")
    print("review: traversal, identity/group membership, ACL mask, and application evidence are distinct")

    if args.require_all:
        return 0 if all(signals.values()) else 1
    return 0 if any(signals.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
