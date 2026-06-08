#!/usr/bin/env python3
"""Run lightweight safety checks over registry files."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "site",
}
SKIP_SUFFIXES = {
    ".egg-info",
}
TEXT_SUFFIXES = {
    "",
    ".c",
    ".cfg",
    ".css",
    ".html",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".sbatch",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class Rule:
    name: str
    pattern: re.Pattern[str]
    message: str


RULES = [
    Rule(
        "private-key",
        re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
        "private key material must not be committed",
    ),
    Rule(
        "github-token",
        re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"),
        "GitHub token-shaped secret detected",
    ),
    Rule(
        "aws-access-key",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "AWS access key-shaped secret detected",
    ),
    Rule(
        "slack-token",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
        "Slack token-shaped secret detected",
    ),
    Rule(
        "danger-rm-root",
        re.compile(r"(^|[;&|]\s*)rm\s+-[A-Za-z]*r[A-Za-z]*f?\s+/(?:\s|$)"),
        "recursive remove against filesystem root is forbidden",
    ),
    Rule(
        "danger-chmod-777",
        re.compile(r"(^|[;&|]\s*)chmod\s+(?:-R\s+)?777\b"),
        "chmod 777 is not acceptable in shared HPC examples",
    ),
    Rule(
        "danger-sudo",
        re.compile(r"(^|[;&|]\s*)sudo\s+"),
        "sudo must not appear in user-facing skill examples",
    ),
]


def skip_path(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        relative = path
    for part in relative.parts:
        if part in SKIP_DIRS:
            return True
        if any(part.endswith(suffix) for suffix in SKIP_SUFFIXES):
            return True
    return False


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_dir() or skip_path(path):
            continue
        if path.suffix not in TEXT_SUFFIXES:
            continue
        yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def audit_file(path: Path) -> List[str]:
    findings: List[str] = []
    text = read_text(path)
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            if rule.pattern.search(line):
                try:
                    relative = path.relative_to(ROOT)
                except ValueError:
                    relative = path
                findings.append(
                    f"{relative}:{line_number}: {rule.name}: {rule.message}"
                )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit registry files for obvious safety issues")
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional files or directories to audit; defaults to the repository root",
    )
    args = parser.parse_args()

    roots = [Path(path).resolve() for path in args.paths] if args.paths else [ROOT]
    findings: List[str] = []
    files_checked = 0

    for root in roots:
        if root.is_file():
            files = [root]
        else:
            files = list(iter_files(root))
        for path in files:
            if skip_path(path):
                continue
            files_checked += 1
            findings.extend(audit_file(path))

    if findings:
        for finding in findings:
            print(f"ERROR: {finding}", file=sys.stderr)
        print(f"Safety audit failed with {len(findings)} finding(s).", file=sys.stderr)
        return 1

    print(f"Safety audit passed for {files_checked} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
