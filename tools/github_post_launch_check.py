#!/usr/bin/env python3
"""Verify the published GitHub repository after launch."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List

from github_repo import shell_join


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_JSON = ROOT / ".github" / "repository.json"
LABELS_JSON = ROOT / ".github" / "labels.json"
MILESTONES_JSON = ROOT / ".github" / "milestones.json"
SEED_ISSUES_JSON = ROOT / ".github" / "seed_issues.json"
RULESET_JSON = ROOT / ".github" / "rulesets" / "main.json"
WORKFLOW_DIR = ROOT / ".github" / "workflows"

GITHUB_REMOTE_RE = re.compile(
    r"(?:git@github\.com:|https://github\.com/)(?P<repo>[^/]+/[^/.]+)(?:\.git)?$"
)


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def ok(name: str, detail: str) -> Check:
    return Check(name, "OK", detail)


def warn(name: str, detail: str) -> Check:
    return Check(name, "WARN", detail)


def fail(name: str, detail: str) -> Check:
    return Check(name, "FAIL", detail)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def run_command(parts: List[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        parts,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_json(parts: List[str]) -> tuple[Any | None, str | None]:
    result = run_command(parts)
    if result.returncode != 0:
        return None, (result.stderr or result.stdout).strip()
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON from {' '.join(parts)}: {exc}"


def origin_remote() -> str:
    result = run_command(["git", "remote", "get-url", "origin"])
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def infer_repo_from_origin() -> str:
    remote = origin_remote()
    match = GITHUB_REMOTE_RE.match(remote)
    if not match:
        return ""
    return match.group("repo")


def expected_workflow_paths() -> List[str]:
    return sorted(
        str(path.relative_to(ROOT))
        for path in WORKFLOW_DIR.glob("*.yml")
    )


def command_plan(repo: str, version: str) -> List[List[str]]:
    return [
        ["git", "remote", "get-url", "origin"],
        ["gh", "api", f"repos/{repo}"],
        ["gh", "api", f"repos/{repo}", "--jq", ".homepage"],
        ["gh", "label", "list", "--repo", repo, "--limit", "200", "--json", "name"],
        ["gh", "api", "-X", "GET", f"repos/{repo}/milestones", "-f", "state=all"],
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            "100",
            "--json",
            "title,state,labels,url",
        ],
        ["gh", "api", f"repos/{repo}/actions/workflows"],
        ["gh", "api", f"repos/{repo}/pages"],
        ["gh", "api", f"repos/{repo}/pages", "--jq", ".html_url"],
        ["python3", "tools/github_homepage.py", "--repo", repo],
        ["gh", "api", f"repos/{repo}/rulesets"],
        ["gh", "release", "view", version, "--repo", repo, "--json", "tagName,isDraft,isPrerelease,url"],
    ]


def local_checks(repo: str | None) -> List[Check]:
    checks: List[Check] = []
    metadata = load_json(REPOSITORY_JSON)
    remote = origin_remote()
    expected_name = metadata["name"]

    if not repo:
        checks.append(
            warn(
                "repo-target",
                "repo was not provided and origin does not point to a GitHub repo",
            )
        )
    elif not repo.endswith(f"/{expected_name}"):
        checks.append(
            fail(
                "repo-target",
                f"expected repo name {expected_name!r}, got {repo!r}",
            )
        )
    else:
        checks.append(ok("repo-target", repo))

    if not remote:
        checks.append(warn("origin-remote", "origin remote is not configured"))
    elif repo and repo in remote:
        checks.append(ok("origin-remote", remote))
    elif repo:
        checks.append(warn("origin-remote", f"origin {remote!r} does not include {repo!r}"))
    else:
        checks.append(ok("origin-remote", remote))

    if shutil.which("gh"):
        checks.append(ok("gh-cli", "GitHub CLI found"))
    else:
        checks.append(warn("gh-cli", "GitHub CLI not found; remote checks skipped"))

    return checks


def repo_metadata_check(repo: str) -> Check:
    metadata = load_json(REPOSITORY_JSON)
    payload, error = run_json(["gh", "api", f"repos/{repo}"])
    if error:
        return fail("github-repository", error)

    expected_private = metadata["visibility"] != "public"
    mismatches = []
    if payload.get("name") != metadata["name"]:
        mismatches.append(f"name={payload.get('name')!r}")
    if payload.get("private") != expected_private:
        mismatches.append(f"private={payload.get('private')!r}")
    if payload.get("default_branch") != metadata["default_branch"]:
        mismatches.append(f"default_branch={payload.get('default_branch')!r}")
    if payload.get("description") != metadata["description"]:
        mismatches.append("description mismatch")

    features = metadata["features"]
    feature_fields = {
        "issues": "has_issues",
        "projects": "has_projects",
        "wiki": "has_wiki",
        "discussions": "has_discussions",
    }
    for feature, field in feature_fields.items():
        if field in payload and payload.get(field) != features[feature]:
            mismatches.append(f"{field}={payload.get(field)!r}")

    if mismatches:
        return fail("github-repository", "; ".join(mismatches))
    return ok("github-repository", f"{repo} metadata matches .github/repository.json")


def labels_check(repo: str) -> Check:
    expected = {label["name"] for label in load_json(LABELS_JSON)}
    payload, error = run_json(
        ["gh", "label", "list", "--repo", repo, "--limit", "200", "--json", "name"]
    )
    if error:
        return fail("github-labels", error)
    actual = {label["name"] for label in payload}
    missing = sorted(expected - actual)
    if missing:
        return fail("github-labels", "missing labels: " + ", ".join(missing))
    return ok("github-labels", f"{len(expected)} labels present")


def milestones_check(repo: str) -> Check:
    expected = {milestone["title"] for milestone in load_json(MILESTONES_JSON)}
    payload, error = run_json(
        ["gh", "api", "-X", "GET", f"repos/{repo}/milestones", "-f", "state=all"]
    )
    if error:
        return fail("github-milestones", error)
    actual = {milestone["title"] for milestone in payload}
    missing = sorted(expected - actual)
    if missing:
        return fail("github-milestones", "missing milestones: " + ", ".join(missing))
    return ok("github-milestones", f"{len(expected)} milestones present")


def starter_issues_check(repo: str) -> Check:
    expected = {issue["title"] for issue in load_json(SEED_ISSUES_JSON)}
    payload, error = run_json(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--limit",
            "100",
            "--json",
            "title,state,labels,url",
        ]
    )
    if error:
        return fail("github-starter-issues", error)
    actual = {issue["title"] for issue in payload}
    missing = sorted(expected - actual)
    if missing:
        return fail("github-starter-issues", "missing starter issues: " + ", ".join(missing))
    return ok("github-starter-issues", f"{len(expected)} starter issues present")


def workflows_check(repo: str) -> Check:
    expected = set(expected_workflow_paths())
    payload, error = run_json(["gh", "api", f"repos/{repo}/actions/workflows"])
    if error:
        return fail("github-workflows", error)
    actual = {workflow.get("path") for workflow in payload.get("workflows", [])}
    missing = sorted(expected - actual)
    if missing:
        return fail("github-workflows", "missing workflows: " + ", ".join(missing))
    return ok("github-workflows", f"{len(expected)} workflows present")


def pages_check(repo: str) -> Check:
    payload, error = run_json(["gh", "api", f"repos/{repo}/pages"])
    if error:
        return fail("github-pages", error)
    status = payload.get("status")
    html_url = payload.get("html_url") or payload.get("url") or "unknown URL"
    if status and status not in {"built", "deployed"}:
        return warn("github-pages", f"Pages status is {status!r} at {html_url}")
    return ok("github-pages", f"Pages configured at {html_url}")


def normalize_url(url: str) -> str:
    return url.rstrip("/")


def homepage_check(repo: str) -> Check:
    repo_payload, repo_error = run_json(["gh", "api", f"repos/{repo}"])
    if repo_error:
        return fail("github-homepage", repo_error)

    pages_payload, pages_error = run_json(["gh", "api", f"repos/{repo}/pages"])
    if pages_error:
        return warn("github-homepage", f"Pages URL unavailable: {pages_error}")

    homepage = (repo_payload.get("homepage") or "").strip()
    pages_url = (pages_payload.get("html_url") or pages_payload.get("url") or "").strip()
    if not pages_url:
        return warn("github-homepage", "Pages URL is unavailable")
    if not homepage:
        return fail(
            "github-homepage",
            "repository homepage is not set; run tools/github_homepage.py",
        )
    if normalize_url(homepage) != normalize_url(pages_url):
        return fail(
            "github-homepage",
            f"homepage {homepage!r} does not match Pages URL {pages_url!r}",
        )
    return ok("github-homepage", f"repository homepage points at {pages_url}")


def ruleset_check(repo: str) -> Check:
    expected = load_json(RULESET_JSON)
    payload, error = run_json(["gh", "api", f"repos/{repo}/rulesets"])
    if error:
        return fail("github-rulesets", error)
    for ruleset in payload:
        if ruleset.get("name") == expected["name"]:
            if ruleset.get("enforcement") != expected["enforcement"]:
                return fail(
                    "github-rulesets",
                    f"{expected['name']} enforcement is {ruleset.get('enforcement')!r}",
                )
            return ok("github-rulesets", f"{expected['name']} ruleset is active")
    return fail("github-rulesets", f"missing ruleset {expected['name']!r}")


def release_check(repo: str, version: str) -> Check:
    payload, error = run_json(
        [
            "gh",
            "release",
            "view",
            version,
            "--repo",
            repo,
            "--json",
            "tagName,isDraft,isPrerelease,url",
        ]
    )
    if error:
        return fail("github-release", error)
    if payload.get("tagName") != version:
        return fail("github-release", f"expected tag {version}, got {payload.get('tagName')!r}")
    if payload.get("isDraft"):
        return warn("github-release", f"{version} exists but is still draft")
    return ok("github-release", f"{version} release is published")


def run_checks(repo: str | None, version: str) -> List[Check]:
    checks = local_checks(repo)
    if not repo or not shutil.which("gh"):
        return checks
    checks.extend(
        [
            repo_metadata_check(repo),
            labels_check(repo),
            milestones_check(repo),
            starter_issues_check(repo),
            workflows_check(repo),
            pages_check(repo),
            homepage_check(repo),
            ruleset_check(repo),
            release_check(repo, version),
        ]
    )
    return checks


def status_counts(checks: Iterable[Check]) -> Dict[str, int]:
    counts = {"OK": 0, "WARN": 0, "FAIL": 0}
    for check in checks:
        counts[check.status] = counts.get(check.status, 0) + 1
    return counts


def markdown(repo: str | None, version: str, checks: List[Check]) -> str:
    counts = status_counts(checks)
    lines = [
        "# HPC Skill Hub Post-Launch Verification",
        "",
        "This report verifies the published GitHub repository with read-only",
        "commands. It does not create repositories, edit settings, open issues,",
        "apply rulesets, or publish releases.",
        "",
        "## Summary",
        "",
        f"- Repository: `{repo or 'unknown'}`",
        f"- Release target: `{version}`",
        f"- Checks: {counts['OK']} OK, {counts['WARN']} WARN, {counts['FAIL']} FAIL",
        "",
        "## Checks",
        "",
        "| Status | Check | Detail |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        detail = check.detail.replace("\n", " ")
        lines.append(f"| `{check.status}` | `{check.name}` | {detail} |")
    lines.append("")
    return "\n".join(lines)


def print_dry_run(repo: str, version: str) -> None:
    print("# HPC Skill Hub Post-Launch Check Commands")
    print("# Review these checks and helper command generators in an authenticated GitHub environment.")
    for command in command_plan(repo, version):
        print(shell_join(command))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the published GitHub repository after launch"
    )
    parser.add_argument(
        "--repo",
        help="GitHub repository in owner/name form. Defaults to origin when possible.",
    )
    parser.add_argument(
        "--version",
        default="v0.6.0",
        help="Release tag to verify. Default: v0.6.0.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print read-only commands without executing them.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON output.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any WARN or FAIL is present.",
    )
    args = parser.parse_args()

    repo = args.repo or infer_repo_from_origin()
    if args.dry_run:
        if not repo:
            parser.error("--repo is required for --dry-run when origin is unavailable")
        print_dry_run(repo, args.version)
        return 0

    checks = run_checks(repo, args.version)
    if args.json:
        print(
            json.dumps(
                {
                    "repo": repo,
                    "version": args.version,
                    "counts": status_counts(checks),
                    "checks": [check.__dict__ for check in checks],
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(markdown(repo, args.version, checks))

    counts = status_counts(checks)
    if counts["FAIL"] or (args.strict and counts["WARN"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
