#!/usr/bin/env python3
"""Audit local readiness for publishing HPC Skill Hub on GitHub."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_LAUNCH_FILES = [
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
    "docs/GITHUB_OWNER_CHECKLIST.md",
    "docs/GITHUB_REPOSITORY_SETUP.md",
    "docs/GITHUB_DISCUSSIONS.md",
    "docs/GITHUB_MILESTONES.md",
    "docs/POST_LAUNCH_VERIFICATION.md",
    "docs/INTEGRATION_GUIDE.md",
    "docs/SKILL_QUALITY.md",
    "docs/BLINDED_REVIEW.md",
    "docs/V0_3_COMPLETION.md",
    "docs/V0_4_COMPLETION.md",
    "docs/V0_5_PLAN.md",
    "docs/V0_5_COMPLETION.md",
    "docs/V0_6_PLAN.md",
    "docs/V0_6_COMPLETION.md",
    "docs/MCP_SERVER.md",
    "docs/MCP_CLIENT_SETUP.md",
    "docs/AGENT_BENCHMARK_SMOKE_PLAN.md",
    "docs/AGENT_BENCHMARK_V0_4_PLAN.md",
    "docs/AGENT_BENCHMARK_V0_5_PLAN.md",
    "docs/AGENT_BENCHMARK_CAMPAIGN.md",
    "docs/AGENT_BENCHMARK_DASHBOARD.html",
    "docs/SKILL_REVIEW_DASHBOARD.html",
    "docs/REVIEW_PACKET_v0.4.0.md",
    "docs/COMMUNITY_INTAKE.md",
    "docs/INTAKE_RECEIPTS.md",
    "docs/COMMUNITY_EVIDENCE.md",
    "docs/COMMUNITY_CONTEXT.md",
    "docs/COMMUNITY_PILOT_v0.6.0.md",
    "docs/SKILL_SECURITY.md",
    "docs/TRUST_POLICY_PACKS.md",
    "docs/COMMUNITY_LAUNCH.md",
    "docs/PUBLIC_LAUNCH_PACKET.md",
    "docs/ADOPTION_WORKSHEET.md",
    "docs/SKILL_LIFECYCLE.md",
    "docs/COMPATIBILITY.md",
    "docs/RELEASE_PROCESS.md",
    "docs/RELEASE_PROVENANCE.md",
    "docs/RELEASE_NOTES_v0.1.0.md",
    "docs/RELEASE_NOTES_v0.2.0.md",
    "docs/RELEASE_NOTES_v0.3.0.md",
    "docs/RELEASE_NOTES_v0.4.0.md",
    "docs/RELEASE_NOTES_v0.5.0.md",
    "docs/RELEASE_NOTES_v0.6.0.md",
    "docs/REVIEW_PACKET_v0.2.0.md",
    "schemas/registry-index.schema.json",
    "schemas/registry-health.schema.json",
    "schemas/skill-quality-report.schema.json",
    "schemas/skill-review.schema.json",
    "schemas/skill-review-status.schema.json",
    "schemas/release-manifest.schema.json",
    "schemas/release-provenance-record.schema.json",
    "schemas/release-status.schema.json",
    "schemas/community-skill-intake-report.schema.json",
    "schemas/community-skill-intake-decision.schema.json",
    "schemas/community-skill-intake-receipt.schema.json",
    "schemas/community-skill-review-packet.schema.json",
    "schemas/community-skill-independent-review.schema.json",
    "schemas/community-skill-adoption-report.schema.json",
    "schemas/community-skill-evidence-status.schema.json",
    "schemas/community-skill-context-bundle.schema.json",
    "schemas/community-pilot-report.schema.json",
    "schemas/skill-security-report.schema.json",
    "schemas/skill-security-policy.schema.json",
    "schemas/skill-context-bundle.schema.json",
    "schemas/mcp-client-contract.schema.json",
    "schemas/site-adapter-resolution.schema.json",
    "schemas/agent-benchmark-review-packet.schema.json",
    "schemas/agent-benchmark-review.schema.json",
    "schemas/agent-benchmark-reconciliation.schema.json",
    "schemas/agent-benchmark-campaign.schema.json",
    "agent-bench/plans/smoke-v0.3.json",
    "agent-bench/plans/evidence-v0.4.json",
    "agent-bench/plans/evidence-v0.5.json",
    "registry/releases/v0.1.0.json",
    "registry/releases/v0.2.0.json",
    "registry/releases/v0.3.0.json",
    "registry/releases/v0.4.0.json",
    "registry/releases/v0.5.0.json",
    "registry/releases/v0.6.0.json",
    "registry/provenance/v0.5.0.json",
    "registry/release-status.json",
    "registry/community-pilot-v0.6.0.json",
    "registry/skill-quality.json",
    "registry/review-status.json",
    "registry/skill-context.json",
    "integrations/mcp-client.json",
    "security/policies/community-default.json",
    "integrations/codex.config.toml",
    "integrations/claude-code.mcp.json",
    "tools/community_review_evidence.py",
    "tools/community_context_bundle.py",
    "tools/community_pilot.py",
    "tools/installed_release_smoke.py",
    "docs/REVIEW_ROUTING.md",
    "docs/DOMAIN_REVIEWERS.md",
    "docs/CONTRIBUTOR_LADDER.md",
    "docs/TRIAGE_RUNBOOK.md",
    ".github/CODEOWNERS",
    ".github/repository.json",
    ".github/labels.json",
    ".github/milestones.json",
    ".github/seed_issues.json",
    ".github/DISCUSSION_TEMPLATE/adoption.yml",
    ".github/DISCUSSION_TEMPLATE/skill-coverage.yml",
    ".github/DISCUSSION_TEMPLATE/site-adapters.yml",
    ".github/DISCUSSION_TEMPLATE/review-process.yml",
    ".github/DISCUSSION_TEMPLATE/integrations.yml",
    ".github/rulesets/main.json",
    ".github/workflows/validate.yml",
    ".github/workflows/package.yml",
    ".github/workflows/pages.yml",
    ".github/pull_request_template.md",
    "tools/github_publish_plan.py",
    "tools/github_homepage.py",
    "tools/github_post_launch_check.py",
    "tools/launch_evidence.py",
    "tools/proposal_evidence.py",
    "tools/review_candidates.py",
    "tools/review_packet.py",
    "tools/github_milestones.py",
    "tools/build_compatibility.py",
    "tools/build_package_data.py",
    "tools/build_mcp_client_configs.py",
    "tools/build_release_manifest.py",
    "tools/build_release_status.py",
    "tools/build_skill_quality.py",
    "tools/build_skill_reviews.py",
    "tools/build_skill_context.py",
    "tools/quarantine_skill_intake.py",
    "tools/community_intake_receipt.py",
    "tools/scan_skill_security.py",
    "tools/agent_benchmark_review.py",
    "tools/agent_benchmark_campaign.py",
    "tools/validate_registry_artifacts.py",
]


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def run_command(
    parts: List[str], env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    command_env = None
    if env:
        command_env = os.environ.copy()
        command_env.update(env)
    return subprocess.run(
        parts,
        cwd=str(ROOT),
        env=command_env,
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
    missing = [path for path in REQUIRED_LAUNCH_FILES if not (ROOT / path).exists()]
    if missing:
        return fail("required-files", "missing: " + ", ".join(missing))
    return ok("required-files", f"{len(REQUIRED_LAUNCH_FILES)} launch files present")


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
        (
            "skill-context-current",
            ["python3", "tools/build_skill_context.py", "--check"],
        ),
        ("compatibility-current", ["python3", "tools/build_compatibility.py", "--check"]),
        (
            "mcp-client-configs-current",
            ["python3", "tools/build_mcp_client_configs.py", "--check"],
        ),
        (
            "release-status-current",
            ["python3", "tools/build_release_status.py", "--check"],
        ),
        ("package-data-current", ["python3", "tools/build_package_data.py", "--check"]),
        ("runtime-doctor", ["python3", "tools/hpc_skill.py", "doctor"]),
        (
            "release-snapshots-valid",
            ["python3", "tools/validate_registry_artifacts.py", "--release-only"],
        ),
        (
            "review-packet-current",
            ["python3", "tools/review_packet.py", "--check"],
        ),
        (
            "registry-artifact-contracts",
            ["python3", "tools/validate_registry_artifacts.py"],
        ),
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


def milestones_check() -> Check:
    milestone_path = ROOT / ".github" / "milestones.json"
    milestones = json.loads(milestone_path.read_text(encoding="utf-8"))
    if not isinstance(milestones, list) or not milestones:
        return fail(
            "github-milestones",
            ".github/milestones.json must contain milestones",
        )

    titles = [milestone.get("title") for milestone in milestones]
    if len(titles) != len(set(titles)):
        return fail("github-milestones", "milestone titles must be unique")
    for milestone in milestones:
        title = milestone.get("title")
        description = milestone.get("description", "")
        state = milestone.get("state")
        if not isinstance(title, str) or not title.strip():
            return fail("github-milestones", "milestone title must be non-empty")
        if not isinstance(description, str) or len(description.strip()) < 20:
            return fail(
                "github-milestones",
                f"milestone {title!r} has a short description",
            )
        if state not in {"open", "closed"}:
            return fail("github-milestones", f"milestone {title!r} has invalid state")
    return ok("github-milestones", f"{len(milestones)} milestones configured")


def issue_templates_check() -> Check:
    template_dir = ROOT / ".github" / "ISSUE_TEMPLATE"
    templates = sorted(path.name for path in template_dir.glob("*.md"))
    expected = {
        "adoption_report.md",
        "bug_report.md",
        "documentation.md",
        "integration_request.md",
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


def discussion_templates_check() -> Check:
    labels = json.loads((ROOT / ".github" / "labels.json").read_text(encoding="utf-8"))
    label_names = {label["name"] for label in labels}
    template_dir = ROOT / ".github" / "DISCUSSION_TEMPLATE"
    templates = sorted(path.name for path in template_dir.glob("*.yml"))
    expected = {
        "adoption.yml",
        "integrations.yml",
        "review-process.yml",
        "site-adapters.yml",
        "skill-coverage.yml",
    }
    missing = sorted(expected - set(templates))
    if missing:
        return fail("discussion-templates", "missing: " + ", ".join(missing))

    label_pattern = re.compile(r'^labels:\s*\[(.*?)\]\s*$', re.MULTILINE)
    for template_path in template_dir.glob("*.yml"):
        text = template_path.read_text(encoding="utf-8")
        if "body:" not in text or "validations:" not in text:
            return fail(
                "discussion-templates",
                f"{template_path.name} is missing form body or validations",
            )
        match = label_pattern.search(text)
        if not match:
            return fail("discussion-templates", f"{template_path.name} is missing labels")
        labels_in_template = [
            item.strip().strip("\"'") for item in match.group(1).split(",")
        ]
        missing_labels = sorted(set(labels_in_template) - label_names)
        if missing_labels:
            return fail(
                "discussion-templates",
                f"{template_path.name} references missing labels: {', '.join(missing_labels)}",
            )
    return ok("discussion-templates", f"{len(templates)} discussion templates present")


def git_status_check() -> Check:
    result = run_command(["git", "status", "--short"])
    if result.returncode != 0:
        return fail("git-status", result.stderr.strip())
    if result.stdout.strip():
        return warn("git-status", "working tree has uncommitted changes")
    return ok("git-status", "working tree clean")


def git_remote_check(owner: str | None = None) -> Check:
    result = run_command(["git", "remote", "get-url", "origin"])
    if result.returncode != 0:
        if owner:
            return warn(
                "git-remote",
                "origin remote is not configured; expected "
                f"git@github.com:{owner}/hpc-skill-hub.git after repository creation",
            )
        return warn("git-remote", "origin remote is not configured")
    return ok("git-remote", result.stdout.strip())


def gh_cli_check(owner: str | None = None, run_make_check: bool = False) -> Check:
    if shutil.which("gh"):
        return ok("gh-cli", "GitHub CLI found")
    command = "python3 tools/github_publish_plan.py"
    if owner:
        command += f" --owner {owner}"
    else:
        command += " --owner <owner>"
    if run_make_check:
        command += " --run-check"
    return warn(
        "gh-cli",
        "GitHub CLI not found; install and authenticate gh, then review "
        f"`{command}` in that environment",
    )


def make_check(run_check: bool) -> Check:
    if not run_check:
        return warn("make-check", "not run; pass --run-check to execute make check")
    with tempfile.TemporaryDirectory(prefix="hpc-skill-hub-check-") as tmpdir:
        site_output = str(Path(tmpdir) / "site" / "index.html")
        result = run_command(["make", "check"], env={"SITE_OUTPUT": site_output})
    if result.returncode == 0:
        return ok("make-check", "make check passed")
    detail = (result.stderr or result.stdout).strip()
    return fail("make-check", detail)


def launch_checks(run_make_check: bool, owner: str | None = None) -> List[Check]:
    checks = [
        required_files_check(),
        registry_health_check(),
        github_metadata_check(),
        issue_templates_check(),
        discussion_templates_check(),
        milestones_check(),
        git_status_check(),
        git_remote_check(owner),
        gh_cli_check(owner, run_make_check),
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
    parser.add_argument(
        "--owner",
        help="Optional GitHub owner or organization used to print concrete follow-up hints.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    checks = launch_checks(args.run_check, args.owner)
    if args.json:
        print_json(checks)
    else:
        print_text(checks)
    return 1 if any(check.status == "FAIL" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
