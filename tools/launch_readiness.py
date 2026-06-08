#!/usr/bin/env python3
"""Audit local readiness for publishing HPC Skill Hub on GitHub."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def run_command(parts: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        parts,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def ok(name: str, detail: str) -> Check:
    return Check(name, "OK", detail)


def warn(name: str, detail: str) -> Check:
    return Check(name, "WARN", detail)


def fail(name: str, detail: str) -> Check:
    return Check(name, "FAIL", detail)


def required_files_check() -> Check:
    required = [
        "README.md",
        "ROADMAP.md",
        "CONTRIBUTING.md",
        "SUPPORT.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "CITATION.cff",
        "CHANGELOG.md",
        "docs/CITATION.md",
        "docs/GITHUB_PUBLISHING.md",
        "docs/GITHUB_REPOSITORY_SETUP.md",
        "docs/COMMUNITY_LAUNCH.md",
        "docs/RELEASE_PROCESS.md",
        "docs/RELEASE_NOTES_v0.1.0.md",
        ".github/repository.json",
        ".github/labels.json",
        ".github/seed_issues.json",
        ".github/rulesets/main.json",
        ".github/workflows/validate.yml",
        ".github/workflows/pages.yml",
        ".github/pull_request_template.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    if missing:
        return fail("required-files", "missing: " + ", ".join(missing))
    return ok("required-files", f"{len(required)} launch files present")


def registry_health_check() -> Check:
    health_path = ROOT / "registry" / "health.json"
    if not health_path.exists():
        return fail("registry-health", "registry/health.json is missing")
    health = json.loads(health_path.read_text(encoding="utf-8"))
    if health.get("uncollected_skill_ids"):
        return fail(
            "registry-health",
            f"{len(health['uncollected_skill_ids'])} uncollected skill(s)",
        )
    return ok(
        "registry-health",
        f"{health['skill_count']} skills, {health['collection_count']} collections",
    )


def generated_artifacts_check() -> List[Check]:
    checks: List[Check] = []
    for name, command in [
        ("registry-index-current", ["python3", "tools/build_index.py", "--check"]),
        ("registry-health-current", ["python3", "tools/build_health.py", "--check"]),
    ]:
        result = run_command(command)
        if result.returncode == 0:
            checks.append(ok(name, result.stdout.strip()))
        else:
            detail = (result.stderr or result.stdout).strip()
            checks.append(fail(name, detail))
    return checks


def github_metadata_check() -> Check:
    repository = json.loads((ROOT / ".github" / "repository.json").read_text())
    labels = json.loads((ROOT / ".github" / "labels.json").read_text())
    seed_issues = json.loads((ROOT / ".github" / "seed_issues.json").read_text())
    if repository.get("visibility") != "public":
        return fail("github-metadata", "repository visibility is not public")
    if repository.get("name") != "hpc-skill-hub":
        return fail("github-metadata", "repository name is not hpc-skill-hub")
    label_names = {label["name"] for label in labels}
    for issue in seed_issues:
        missing = sorted(set(issue["labels"]) - label_names)
        if missing:
            return fail(
                "github-metadata",
                f"seed issue {issue['id']} references missing labels: {', '.join(missing)}",
            )
    return ok(
        "github-metadata",
        f"{len(labels)} labels and {len(seed_issues)} seed issues configured",
    )


def issue_templates_check() -> Check:
    template_dir = ROOT / ".github" / "ISSUE_TEMPLATE"
    templates = sorted(path.name for path in template_dir.glob("*.md"))
    expected = {
        "adoption_report.md",
        "bug_report.md",
        "documentation.md",
        "maturity_review.md",
        "rfc_proposal.md",
        "safety_review.md",
        "site_adapter_request.md",
        "skill_request.md",
    }
    missing = sorted(expected - set(templates))
    if missing:
        return fail("issue-templates", "missing: " + ", ".join(missing))
    return ok("issue-templates", f"{len(templates)} issue templates present")


def git_status_check() -> Check:
    result = run_command(["git", "status", "--short"])
    if result.returncode != 0:
        return fail("git-status", result.stderr.strip())
    if result.stdout.strip():
        return warn("git-status", "working tree has uncommitted changes")
    return ok("git-status", "working tree clean")


def git_remote_check() -> Check:
    result = run_command(["git", "remote", "get-url", "origin"])
    if result.returncode != 0:
        return warn("git-remote", "origin remote is not configured")
    return ok("git-remote", result.stdout.strip())


def gh_cli_check() -> Check:
    if shutil.which("gh"):
        return ok("gh-cli", "GitHub CLI found")
    return warn("gh-cli", "GitHub CLI not found; run generated commands in an authenticated environment")


def make_check(run_check: bool) -> Check:
    if not run_check:
        return warn("make-check", "not run; pass --run-check to execute make check")
    result = run_command(["make", "check"])
    if result.returncode == 0:
        return ok("make-check", "make check passed")
    detail = (result.stderr or result.stdout).strip()
    return fail("make-check", detail)


def launch_checks(run_make_check: bool) -> List[Check]:
    checks = [
        required_files_check(),
        registry_health_check(),
        github_metadata_check(),
        issue_templates_check(),
        git_status_check(),
        git_remote_check(),
        gh_cli_check(),
    ]
    checks.extend(generated_artifacts_check())
    checks.append(make_check(run_make_check))
    return checks


def print_text(checks: Iterable[Check]) -> None:
    for check in checks:
        print(f"{check.status:4} {check.name}: {check.detail}")


def print_json(checks: Iterable[Check]) -> None:
    payload = [
        {"name": check.name, "status": check.status, "detail": check.detail}
        for check in checks
    ]
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit local readiness for publishing HPC Skill Hub on GitHub"
    )
    parser.add_argument(
        "--run-check",
        action="store_true",
        help="Run make check as part of the readiness audit.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    checks = launch_checks(args.run_check)
    if args.json:
        print_json(checks)
    else:
        print_text(checks)
    return 1 if any(check.status == "FAIL" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
