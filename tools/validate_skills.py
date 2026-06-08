#!/usr/bin/env python3
"""Validate HPC Skill Hub manifests without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

REQUIRED_FIELDS = {
    "id",
    "name",
    "version",
    "status",
    "summary",
    "description",
    "categories",
    "tags",
    "maintainers",
    "license",
    "maturity",
    "risk_level",
    "tools",
    "inputs",
    "outputs",
    "artifacts",
    "examples",
    "tests",
    "references",
}

OPTIONAL_FIELDS = {"$schema", "schedulers"}
ALLOWED_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS
ALLOWED_STATUS = {"draft", "reviewed", "deprecated"}
ALLOWED_MATURITY = {"seed", "reviewed", "field-tested", "maintained"}
ALLOWED_RISK = {"low", "medium", "high"}
ALLOWED_CATEGORIES = {
    "scheduler",
    "containers",
    "software",
    "workflow",
    "data",
    "debugging",
    "performance",
    "gpu",
    "mpi",
    "interactive",
    "admin",
    "education",
}
ALLOWED_TEST_TYPES = {"static", "dry-run", "manual", "integration"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9.+_-]*$")


def load_json(path: Path, errors: List[str]) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return {}
    except OSError as exc:
        errors.append(f"{path}: cannot read file: {exc}")
        return {}

    if not isinstance(data, dict):
        errors.append(f"{path}: manifest must be a JSON object")
        return {}
    return data


def require_non_empty_string(
    manifest: Dict[str, Any], field: str, errors: List[str], context: str
) -> None:
    value = manifest.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}: field '{field}' must be a non-empty string")


def require_list(
    manifest: Dict[str, Any], field: str, errors: List[str], context: str
) -> List[Any]:
    value = manifest.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{context}: field '{field}' must be a non-empty list")
        return []
    return value


def validate_manifest(skill_dir: Path) -> List[str]:
    errors: List[str] = []
    manifest_path = skill_dir / "skill.json"
    context = str(manifest_path.relative_to(ROOT))

    if not manifest_path.exists():
        return [f"{skill_dir.relative_to(ROOT)}: missing skill.json"]

    manifest = load_json(manifest_path, errors)
    if not manifest:
        return errors

    missing = sorted(REQUIRED_FIELDS - set(manifest))
    for field in missing:
        errors.append(f"{context}: missing required field '{field}'")

    unknown = sorted(set(manifest) - ALLOWED_FIELDS)
    for field in unknown:
        errors.append(f"{context}: unknown field '{field}'")

    for field in ["id", "name", "version", "status", "summary", "description", "license", "maturity", "risk_level"]:
        require_non_empty_string(manifest, field, errors, context)

    skill_id = manifest.get("id")
    if isinstance(skill_id, str):
        if not ID_RE.match(skill_id):
            errors.append(f"{context}: id must be lowercase kebab-case")
        if skill_id != skill_dir.name:
            errors.append(f"{context}: id '{skill_id}' must match directory '{skill_dir.name}'")

    version = manifest.get("version")
    if isinstance(version, str) and not SEMVER_RE.match(version):
        errors.append(f"{context}: version must use MAJOR.MINOR.PATCH")

    status = manifest.get("status")
    if isinstance(status, str) and status not in ALLOWED_STATUS:
        errors.append(f"{context}: status must be one of {sorted(ALLOWED_STATUS)}")

    maturity = manifest.get("maturity")
    if isinstance(maturity, str) and maturity not in ALLOWED_MATURITY:
        errors.append(f"{context}: maturity must be one of {sorted(ALLOWED_MATURITY)}")

    risk = manifest.get("risk_level")
    if isinstance(risk, str) and risk not in ALLOWED_RISK:
        errors.append(f"{context}: risk_level must be one of {sorted(ALLOWED_RISK)}")

    categories = require_list(manifest, "categories", errors, context)
    for category in categories:
        if category not in ALLOWED_CATEGORIES:
            errors.append(f"{context}: unsupported category '{category}'")

    tags = require_list(manifest, "tags", errors, context)
    for tag in tags:
        if not isinstance(tag, str) or not TAG_RE.match(tag):
            errors.append(f"{context}: invalid tag '{tag}'")

    maintainers = require_list(manifest, "maintainers", errors, context)
    for index, maintainer in enumerate(maintainers):
        if not isinstance(maintainer, dict) or not maintainer.get("name"):
            errors.append(f"{context}: maintainers[{index}] must include a name")

    tools = require_list(manifest, "tools", errors, context)
    for index, tool in enumerate(tools):
        if not isinstance(tool, dict) or not tool.get("name"):
            errors.append(f"{context}: tools[{index}] must include a name")
            continue
        if not isinstance(tool.get("required"), bool):
            errors.append(f"{context}: tools[{index}].required must be boolean")

    for field in ["inputs", "outputs"]:
        value = manifest.get(field, [])
        if not isinstance(value, list):
            errors.append(f"{context}: field '{field}' must be a list")
            continue
        for index, item in enumerate(value):
            if not isinstance(item, dict) or not item.get("name") or not item.get("description"):
                errors.append(f"{context}: {field}[{index}] must include name and description")

    readme = skill_dir / "README.md"
    if not readme.exists():
        errors.append(f"{skill_dir.relative_to(ROOT)}: missing README.md")

    artifacts = require_list(manifest, "artifacts", errors, context)
    for artifact in artifacts:
        if not isinstance(artifact, str):
            errors.append(f"{context}: artifact path must be a string")
            continue
        if artifact.startswith("/") or ".." in Path(artifact).parts:
            errors.append(f"{context}: artifact path '{artifact}' must stay inside the skill directory")
            continue
        if not (skill_dir / artifact).exists():
            errors.append(f"{context}: artifact '{artifact}' does not exist")

    examples = require_list(manifest, "examples", errors, context)
    for index, example in enumerate(examples):
        if not isinstance(example, dict) or not example.get("title") or not example.get("path"):
            errors.append(f"{context}: examples[{index}] must include title and path")
            continue
        path = example["path"]
        if not isinstance(path, str) or path.startswith("/") or ".." in Path(path).parts:
            errors.append(f"{context}: examples[{index}].path must stay inside the skill directory")
            continue
        if not (skill_dir / path).exists():
            errors.append(f"{context}: example '{path}' does not exist")

    tests = require_list(manifest, "tests", errors, context)
    for index, test in enumerate(tests):
        if not isinstance(test, dict) or not test.get("description"):
            errors.append(f"{context}: tests[{index}] must include a description")
            continue
        test_type = test.get("type")
        if test_type not in ALLOWED_TEST_TYPES:
            errors.append(f"{context}: tests[{index}].type must be one of {sorted(ALLOWED_TEST_TYPES)}")

    references = manifest.get("references", [])
    if not isinstance(references, list):
        errors.append(f"{context}: field 'references' must be a list")
    for index, reference in enumerate(references):
        if not isinstance(reference, dict) or not reference.get("title") or not reference.get("url"):
            errors.append(f"{context}: references[{index}] must include title and url")
            continue
        url = reference["url"]
        if not isinstance(url, str) or not (url.startswith("https://") or url.startswith("http://")):
            errors.append(f"{context}: references[{index}].url must be http(s)")

    return errors


def discover_skill_dirs(selected: str | None) -> Iterable[Path]:
    if selected:
        yield SKILLS_DIR / selected
        return
    if not SKILLS_DIR.exists():
        return
    for path in sorted(SKILLS_DIR.iterdir()):
        if path.is_dir() and not path.name.startswith("."):
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate HPC Skill Hub manifests")
    parser.add_argument("--skill", help="Validate one skill id")
    args = parser.parse_args()

    errors: List[str] = []
    skill_dirs = list(discover_skill_dirs(args.skill))
    if not skill_dirs:
        errors.append("No skills found")

    for skill_dir in skill_dirs:
        if not skill_dir.exists():
            errors.append(f"skills/{skill_dir.name}: skill directory does not exist")
            continue
        errors.extend(validate_manifest(skill_dir))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(f"Validated {len(skill_dirs)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
