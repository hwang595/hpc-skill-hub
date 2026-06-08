#!/usr/bin/env python3
"""Build a deterministic release manifest with file checksums."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_INDEX = ROOT / "registry" / "index.json"
REGISTRY_HEALTH = ROOT / "registry" / "health.json"
RELEASE_DIR = ROOT / "registry" / "releases"

ROOT_FILES = [
    ".gitignore",
    "CHANGELOG.md",
    "CITATION.cff",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "Makefile",
    "README.md",
    "ROADMAP.md",
    "SECURITY.md",
    "SUPPORT.md",
    "pyproject.toml",
    "setup.py",
]

INCLUDED_DIRS = [
    ".github",
    "collections",
    "docs",
    "registry",
    "schemas",
    "site-adapters",
    "skills",
    "src",
    "tests",
    "tools",
]

EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "site",
}


def normalize_version(version: str) -> str:
    return version if version.startswith("v") else f"v{version}"


def release_manifest_path(version: str) -> Path:
    return RELEASE_DIR / f"{normalize_version(version)}.json"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def should_include(path: Path, output_path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if path == output_path:
        return False
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return False
    if relative.parts[:2] == ("registry", "releases"):
        return False
    if path.name == ".DS_Store" or path.suffix == ".pyc":
        return False
    return path.is_file()


def iter_release_files(output_path: Path) -> Iterable[Path]:
    for root_file in ROOT_FILES:
        path = ROOT / root_file
        if should_include(path, output_path):
            yield path

    for directory in INCLUDED_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if should_include(path, output_path):
                yield path


def file_entry(path: Path) -> Dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def build_manifest(version: str) -> Dict[str, Any]:
    normalized = normalize_version(version)
    output_path = release_manifest_path(normalized)
    index = load_json(REGISTRY_INDEX)
    health = load_json(REGISTRY_HEALTH)
    files = [file_entry(path) for path in sorted(iter_release_files(output_path))]

    return {
        "$schema": "../../schemas/release-manifest.schema.json",
        "schema_version": "0.1.0",
        "generated_by": "tools/build_release_manifest.py",
        "version": normalized,
        "registry": {
            "schema_version": index["schema_version"],
            "skill_count": index["skill_count"],
            "collection_count": index["collection_count"],
            "site_adapter_count": index["site_adapter_count"],
            "category_count": len(index["categories"]),
            "scheduler_count": len(index["schedulers"]),
            "tool_count": len(index["tools"]),
            "risk_counts": health["risk_counts"],
            "maturity_counts": health["maturity_counts"],
            "status_counts": health["status_counts"],
            "uncollected_skill_count": len(health["uncollected_skill_ids"]),
        },
        "files": files,
        "file_count": len(files),
        "total_bytes": sum(entry["bytes"] for entry in files),
    }


def serialized_manifest(manifest: Dict[str, Any]) -> str:
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def check_output(output_path: Path, expected: str) -> List[str]:
    if not output_path.exists():
        return [f"{output_path.relative_to(ROOT)} is missing"]
    if output_path.read_text(encoding="utf-8") != expected:
        return [
            f"{output_path.relative_to(ROOT)} is stale; run tools/build_release_manifest.py"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a deterministic release manifest with file checksums"
    )
    parser.add_argument(
        "version",
        nargs="?",
        default="v0.1.0",
        help="Release version, for example v0.1.0 or 0.1.0.",
    )
    parser.add_argument("--check", action="store_true", help="Fail if output is stale")
    args = parser.parse_args()

    output_path = release_manifest_path(args.version)
    expected = serialized_manifest(build_manifest(args.version))
    if args.check:
        errors = check_output(output_path, expected)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Release manifest is current in {output_path.relative_to(ROOT)}.")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(expected, encoding="utf-8")
    print(f"Wrote {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
