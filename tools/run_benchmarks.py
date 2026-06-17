#!/usr/bin/env python3
"""Run CI-safe benchmark cases for HPC Skill Hub skills."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_DIR = ROOT / "benchmarks"
CASE_DIR = BENCHMARK_DIR / "cases"
INDEX_JSON = ROOT / "registry" / "index.json"
DEFAULT_REPORT = ROOT / "docs" / "BENCHMARK_REPORT.md"

REQUIRED_FIELDS = {
    "id",
    "name",
    "version",
    "status",
    "mode",
    "risk_level",
    "skill_ids",
    "summary",
    "fixtures",
    "commands",
    "checks",
    "expected_outcomes",
}
ALLOWED_MODES = {"fixture", "static", "dry-run", "site"}
ALLOWED_STATUS = {"draft", "reviewed", "deprecated"}
ALLOWED_RISK = {"low", "medium", "high"}
ALLOWED_CHECKS = {"file_exists", "contains_all", "contains_any", "not_contains"}
SAFE_COMMANDS = {"bash", "python3"}
RESOURCE_COMMANDS = {"sbatch", "salloc", "srun", "qsub", "bsub", "condor_submit"}
BLOCKED_COMMANDS = {
    "sbatch",
    "salloc",
    "srun",
    "qsub",
    "bsub",
    "condor_submit",
    "globus",
    "rsync",
    "scp",
    "ssh",
    "apptainer",
    "singularity",
    "docker",
    "podman",
}
SITE_COMMANDS = SAFE_COMMANDS | RESOURCE_COMMANDS
COMMAND_FIELDS = {"label", "argv", "expect_returncode", "requires_env", "timeout_seconds"}
ENV_TOKEN = re.compile(r"^\$\{([A-Z][A-Z0-9_]*)\}$")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def resolve_repo_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        raise ValueError(f"path escapes repository: {value}")
    return path


def load_cases() -> List[Dict[str, Any]]:
    cases = []
    for path in sorted(CASE_DIR.glob("*.json")):
        case = load_json(path)
        case["_path"] = path
        cases.append(case)
    return cases


def validate_case(case: Dict[str, Any], known_skills: set[str]) -> List[str]:
    errors: List[str] = []
    context = rel(case["_path"])

    missing = sorted(REQUIRED_FIELDS - set(case))
    for field in missing:
        errors.append(f"{context}: missing required field {field}")

    unknown = sorted(set(case) - REQUIRED_FIELDS - {"$schema", "_path"})
    for field in unknown:
        errors.append(f"{context}: unknown field {field}")

    if not isinstance(case.get("id"), str) or not case.get("id"):
        errors.append(f"{context}: id must be a non-empty string")
    elif case["id"] != case["_path"].stem:
        errors.append(f"{context}: id must match filename")

    if case.get("status") not in ALLOWED_STATUS:
        errors.append(f"{context}: status must be one of {sorted(ALLOWED_STATUS)}")
    if case.get("mode") not in ALLOWED_MODES:
        errors.append(f"{context}: mode must be one of {sorted(ALLOWED_MODES)}")
    if case.get("risk_level") not in ALLOWED_RISK:
        errors.append(f"{context}: risk_level must be one of {sorted(ALLOWED_RISK)}")

    skill_ids = case.get("skill_ids", [])
    if not isinstance(skill_ids, list) or not skill_ids:
        errors.append(f"{context}: skill_ids must be a non-empty list")
    else:
        for skill_id in skill_ids:
            if skill_id not in known_skills:
                errors.append(f"{context}: unknown skill id {skill_id}")

    for field in ["fixtures", "commands", "checks", "expected_outcomes"]:
        if not isinstance(case.get(field), list):
            errors.append(f"{context}: {field} must be a list")

    for fixture in case.get("fixtures", []):
        path = fixture.get("path") if isinstance(fixture, dict) else None
        if not isinstance(path, str):
            errors.append(f"{context}: fixture path must be a string")
            continue
        try:
            resolved = resolve_repo_path(path)
        except ValueError as exc:
            errors.append(f"{context}: {exc}")
            continue
        if not resolved.exists():
            errors.append(f"{context}: fixture does not exist: {path}")

    for command in case.get("commands", []):
        if not isinstance(command, dict):
            errors.append(f"{context}: command must be an object")
            continue
        unknown_command_fields = sorted(set(command) - COMMAND_FIELDS)
        for field in unknown_command_fields:
            errors.append(f"{context}: command has unknown field {field}")
        argv = command.get("argv") if isinstance(command, dict) else None
        if not isinstance(argv, list) or not argv or not all(isinstance(item, str) for item in argv):
            errors.append(f"{context}: command argv must be a non-empty string list")
            continue
        executable = Path(argv[0]).name
        if case.get("mode") == "site":
            if executable not in SITE_COMMANDS:
                errors.append(f"{context}: site command executable {executable} is not in site allowlist")
        else:
            if executable in BLOCKED_COMMANDS:
                errors.append(f"{context}: command uses blocked executable {executable}")
            if executable not in SAFE_COMMANDS:
                errors.append(f"{context}: command executable {executable} is not in safe allowlist")
        requires_env = command.get("requires_env", [])
        if not isinstance(requires_env, list) or not all(isinstance(item, str) for item in requires_env):
            errors.append(f"{context}: command requires_env must be a string list")
        timeout_seconds = command.get("timeout_seconds")
        if timeout_seconds is not None and (
            not isinstance(timeout_seconds, int) or timeout_seconds <= 0
        ):
            errors.append(f"{context}: command timeout_seconds must be a positive integer")

    for check in case.get("checks", []):
        if not isinstance(check, dict):
            errors.append(f"{context}: check must be an object")
            continue
        check_type = check.get("type")
        if check_type not in ALLOWED_CHECKS:
            errors.append(f"{context}: unsupported check type {check_type}")
        path = check.get("path")
        if not isinstance(path, str):
            errors.append(f"{context}: check path must be a string")
            continue
        try:
            resolved = resolve_repo_path(path)
        except ValueError as exc:
            errors.append(f"{context}: {exc}")
            continue
        if not resolved.exists():
            errors.append(f"{context}: check path does not exist: {path}")
        if check_type != "file_exists":
            patterns = check.get("patterns")
            if not isinstance(patterns, list) or not patterns:
                errors.append(f"{context}: check patterns must be a non-empty list")

    return errors


def expand_argv(argv: List[str]) -> List[str]:
    expanded = []
    for item in argv:
        match = ENV_TOKEN.match(item)
        if match:
            expanded.append(os.environ[match.group(1)])
        else:
            expanded.append(item)
    return expanded


def run_command(command: Dict[str, Any]) -> Dict[str, Any]:
    required_env = set(command.get("requires_env", []))
    for item in command["argv"]:
        match = ENV_TOKEN.match(item)
        if match:
            required_env.add(match.group(1))
    missing_env = sorted(name for name in required_env if not os.environ.get(name))
    if missing_env:
        return {
            "label": command.get("label", " ".join(command["argv"])),
            "argv": command["argv"],
            "expected_returncode": int(command.get("expect_returncode", 0)),
            "returncode": None,
            "status": "skipped",
            "stdout": "",
            "stderr": "",
            "skip_reason": f"missing environment variable(s): {', '.join(missing_env)}",
        }

    argv = expand_argv(command["argv"])
    expected = int(command.get("expect_returncode", 0))
    try:
        result = subprocess.run(
            argv,
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=int(command.get("timeout_seconds", 120)),
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "label": command.get("label", " ".join(command["argv"])),
            "argv": argv,
            "expected_returncode": expected,
            "returncode": None,
            "status": "failed",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"timed out after {command.get('timeout_seconds', 120)} seconds",
        }
    passed = result.returncode == expected
    return {
        "label": command.get("label", " ".join(argv)),
        "argv": argv,
        "expected_returncode": expected,
        "returncode": result.returncode,
        "status": "passed" if passed else "failed",
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_check(check: Dict[str, Any]) -> Dict[str, Any]:
    path = resolve_repo_path(check["path"])
    check_type = check["type"]
    patterns = check.get("patterns", [])
    if check_type == "file_exists":
        passed = path.exists()
        missing: List[str] = []
    else:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if check_type == "contains_all":
            missing = [pattern for pattern in patterns if pattern not in text]
            passed = not missing
        elif check_type == "contains_any":
            missing = [] if any(pattern in text for pattern in patterns) else list(patterns)
            passed = not missing
        elif check_type == "not_contains":
            missing = [pattern for pattern in patterns if pattern in text]
            passed = not missing
        else:
            missing = [f"unsupported check type {check_type}"]
            passed = False
    return {
        "label": check.get("label", f"{check_type} {check['path']}"),
        "type": check_type,
        "path": check["path"],
        "status": "passed" if passed else "failed",
        "missing_or_unexpected": missing,
    }


def run_case(case: Dict[str, Any], include_site: bool) -> Dict[str, Any]:
    skipped = case["mode"] == "site" and not include_site
    command_results: List[Dict[str, Any]] = []
    check_results: List[Dict[str, Any]] = []
    if not skipped:
        command_results = [run_command(command) for command in case.get("commands", [])]
        check_results = [run_check(check) for check in case.get("checks", [])]
    statuses = [result["status"] for result in command_results + check_results]
    if skipped:
        status = "skipped"
    elif any(item == "failed" for item in statuses):
        status = "failed"
    elif any(item == "skipped" for item in statuses):
        status = "skipped"
    else:
        status = "passed"
    return {
        "id": case["id"],
        "name": case["name"],
        "mode": case["mode"],
        "risk_level": case["risk_level"],
        "skill_ids": case["skill_ids"],
        "summary": case["summary"],
        "status": status,
        "commands": command_results,
        "checks": check_results,
        "expected_outcomes": case["expected_outcomes"],
        "case_path": rel(case["_path"]),
    }


def benchmark_payload(include_site: bool) -> Dict[str, Any]:
    index = load_json(INDEX_JSON)
    known_skills = {skill["id"] for skill in index["skills"]}
    cases = load_cases()
    validation_errors = []
    for case in cases:
        validation_errors.extend(validate_case(case, known_skills))
    if validation_errors:
        return {
            "ok": False,
            "validation_errors": validation_errors,
            "case_count": len(cases),
            "results": [],
        }

    results = [run_case(case, include_site) for case in cases]
    counts = Counter(result["status"] for result in results)
    mode_counts = Counter(result["mode"] for result in results)
    ok = counts.get("failed", 0) == 0
    return {
        "ok": ok,
        "validation_errors": [],
        "case_count": len(results),
        "counts": dict(sorted(counts.items())),
        "mode_counts": dict(sorted(mode_counts.items())),
        "include_site": include_site,
        "results": results,
    }


def markdown_report(payload: Dict[str, Any]) -> str:
    lines = [
        "# Benchmark Report",
        "",
        "This report is generated by `tools/run_benchmarks.py`. Do not edit it by hand.",
        "",
        "The benchmark suite is CI-safe by default. It uses fixtures, static checks,",
        "and dry-run commands to test whether skills expose the evidence and examples",
        "needed for realistic HPC workflows. Site-mode benchmarks are skipped unless",
        "explicitly enabled.",
        "",
        "## Summary",
        "",
        "| Signal | Count |",
        "| --- | ---: |",
        f"| Cases | {payload['case_count']} |",
    ]
    for status, count in payload.get("counts", {}).items():
        lines.append(f"| `{status}` | {count} |")
    for mode, count in payload.get("mode_counts", {}).items():
        lines.append(f"| Mode `{mode}` | {count} |")

    lines.extend(
        [
            "",
            "## Cases",
            "",
            "| Case | Mode | Skills | Status | Evidence |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for result in sorted(payload.get("results", []), key=lambda item: item["id"]):
        skills = ", ".join(f"`{skill_id}`" for skill_id in result["skill_ids"])
        evidence_bits = []
        if result["commands"]:
            evidence_bits.append(f"{len(result['commands'])} command(s)")
        if result["checks"]:
            evidence_bits.append(f"{len(result['checks'])} check(s)")
        if not evidence_bits:
            evidence_bits.append("metadata only")
        lines.append(
            f"| [`{result['id']}`](../{result['case_path']}) | "
            f"`{result['mode']}` | {skills} | `{result['status']}` | "
            f"{', '.join(evidence_bits)} |"
        )

    lines.extend(
        [
            "",
            "## Expected Outcomes",
            "",
        ]
    )
    for result in sorted(payload.get("results", []), key=lambda item: item["id"]):
        lines.append(f"### `{result['id']}`")
        lines.append("")
        for outcome in result["expected_outcomes"]:
            lines.append(f"- {outcome}")
        lines.append("")

    return "\n".join(lines)


def check_report(report_path: Path, expected: str) -> List[str]:
    if not report_path.exists():
        return [f"{rel(report_path)} is missing"]
    current = report_path.read_text(encoding="utf-8")
    if current != expected:
        return [f"{rel(report_path)} is stale; run tools/run_benchmarks.py"]
    return []


def emit_failures(payload: Dict[str, Any]) -> None:
    for error in payload.get("validation_errors", []):
        print(f"ERROR: {error}", file=sys.stderr)
    for result in payload.get("results", []):
        if result["status"] != "failed":
            continue
        for command in result["commands"]:
            if command["status"] == "failed":
                print(
                    f"ERROR: {result['id']}: command failed: {command['label']}",
                    file=sys.stderr,
                )
                if command["stderr"]:
                    print(command["stderr"], file=sys.stderr)
        for check in result["checks"]:
            if check["status"] == "failed":
                print(
                    f"ERROR: {result['id']}: check failed: {check['label']}: "
                    f"{check['missing_or_unexpected']}",
                    file=sys.stderr,
                )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run HPC Skill Hub benchmark cases")
    parser.add_argument("--check", action="store_true", help="Fail if report is stale")
    parser.add_argument("--json", action="store_true", help="Emit JSON results")
    parser.add_argument(
        "--include-site",
        action="store_true",
        help="Run site-mode benchmarks that may require real HPC resources",
    )
    parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT),
        help="Benchmark report path",
    )
    args = parser.parse_args()

    payload = benchmark_payload(args.include_site)
    expected_report = markdown_report(payload) + "\n"

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.check:
        errors = check_report(Path(args.report), expected_report)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Benchmark report is current in {rel(Path(args.report))}.")
    else:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(expected_report, encoding="utf-8")
        print(f"Wrote {rel(report_path)}.")

    if not payload["ok"]:
        emit_failures(payload)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
