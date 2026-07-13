import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_launch_readiness_module():
    spec = importlib.util.spec_from_file_location(
        "launch_readiness", ROOT / "tools" / "launch_readiness.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class GitHubMetadataTests(unittest.TestCase):
    def load_labels(self):
        with (ROOT / ".github" / "labels.json").open(encoding="utf-8") as handle:
            return json.load(handle)

    def load_repository(self):
        with (ROOT / ".github" / "repository.json").open(encoding="utf-8") as handle:
            return json.load(handle)

    def load_seed_issues(self):
        with (ROOT / ".github" / "seed_issues.json").open(encoding="utf-8") as handle:
            return json.load(handle)

    def load_milestones(self):
        with (ROOT / ".github" / "milestones.json").open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_labels_are_unique_and_complete(self):
        labels = self.load_labels()
        names = [label["name"] for label in labels]
        self.assertEqual(len(names), len(set(names)))

        for label in labels:
            self.assertRegex(label["name"], r"^[a-z0-9][a-z0-9-]*$")
            self.assertRegex(label["color"], r"^[0-9A-Fa-f]{6}$")
            self.assertGreaterEqual(len(label["description"]), 12)

    def test_issue_template_labels_exist(self):
        label_names = {label["name"] for label in self.load_labels()}
        template_dir = ROOT / ".github" / "ISSUE_TEMPLATE"
        frontmatter_label_pattern = re.compile(r"^labels:\s*\[(.*?)\]\s*$", re.MULTILINE)

        referenced_labels = set()
        for template_path in template_dir.glob("*.md"):
            text = template_path.read_text(encoding="utf-8")
            match = frontmatter_label_pattern.search(text)
            if not match:
                continue
            labels = [item.strip().strip("\"'") for item in match.group(1).split(",")]
            referenced_labels.update(label for label in labels if label)

        self.assertTrue(referenced_labels)
        self.assertTrue(referenced_labels.issubset(label_names))

    def test_discussion_templates_are_publishable(self):
        label_names = {label["name"] for label in self.load_labels()}
        template_dir = ROOT / ".github" / "DISCUSSION_TEMPLATE"
        expected = {
            "adoption.yml",
            "integrations.yml",
            "review-process.yml",
            "site-adapters.yml",
            "skill-coverage.yml",
        }
        paths = {path.name for path in template_dir.glob("*.yml")}
        self.assertEqual(paths, expected)

        label_pattern = re.compile(r'^labels:\s*\[(.*?)\]\s*$', re.MULTILINE)
        referenced_labels = set()
        for template_path in template_dir.glob("*.yml"):
            text = template_path.read_text(encoding="utf-8")
            self.assertIn("title:", text, template_path.name)
            self.assertIn("body:", text, template_path.name)
            self.assertIn("validations:", text, template_path.name)
            match = label_pattern.search(text)
            self.assertIsNotNone(match, template_path.name)
            labels = [item.strip().strip("\"'") for item in match.group(1).split(",")]
            referenced_labels.update(label for label in labels if label)

        self.assertTrue(referenced_labels)
        self.assertTrue(referenced_labels.issubset(label_names))

    def test_seed_issues_are_publishable(self):
        label_names = {label["name"] for label in self.load_labels()}
        issues = self.load_seed_issues()
        ids = [issue["id"] for issue in issues]
        self.assertEqual(len(ids), len(set(ids)))

        pinned = [issue for issue in issues if issue["pin"]]
        self.assertEqual(len(pinned), 1)

        for issue in issues:
            self.assertRegex(issue["id"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertGreaterEqual(len(issue["title"]), 12)
            self.assertTrue(set(issue["labels"]).issubset(label_names))
            body_path = ROOT / issue["body"]
            self.assertTrue(body_path.exists(), issue["body"])
            self.assertGreaterEqual(len(body_path.read_text(encoding="utf-8")), 200)

    def test_milestones_are_publishable(self):
        milestones = self.load_milestones()
        titles = [milestone["title"] for milestone in milestones]
        self.assertEqual(len(titles), len(set(titles)))
        self.assertIn("v0.1.0 seed launch", titles)
        self.assertIn("v0.4.0 evidence and reviewed registry", titles)
        self.assertIn("ecosystem backlog", titles)

        for milestone in milestones:
            self.assertIn(milestone["state"], {"open", "closed"})
            self.assertGreaterEqual(len(milestone["description"]), 40)

    def test_repository_metadata_is_publishable(self):
        repository = self.load_repository()
        self.assertEqual(repository["name"], "hpc-skill-hub")
        self.assertEqual(repository["visibility"], "public")
        self.assertEqual(repository["default_branch"], "main")
        self.assertIn("HPC workflows", repository["description"])
        self.assertIn("hpc", repository["topics"])
        self.assertIn("slurm", repository["topics"])
        self.assertTrue(repository["features"]["issues"])
        self.assertTrue(repository["features"]["discussions"])
        self.assertFalse(repository["features"]["wiki"])

    def test_citation_metadata_exists(self):
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        self.assertIn("cff-version: 1.2.0", citation)
        self.assertIn('title: "HPC Skill Hub"', citation)
        self.assertIn('license: "MIT"', citation)
        self.assertIn("HPC Skill Hub Maintainers", citation)

    def test_label_command_generator(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_labels.py",
                "--repo",
                "example/hpc-skill-hub",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("gh label create safety-review", result.stdout)
        self.assertIn("--repo example/hpc-skill-hub", result.stdout)
        self.assertIn("--force", result.stdout)

    def test_milestone_command_generator(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_milestones.py",
                "--repo",
                "example/hpc-skill-hub",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn(
            "gh api -X POST repos/example/hpc-skill-hub/milestones",
            result.stdout,
        )
        self.assertIn("title=v0.1.0 seed launch", result.stdout)
        self.assertIn("title=ecosystem backlog", result.stdout)

    def test_repository_command_generator(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_repo.py",
                "--owner",
                "example",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("git branch -M main", result.stdout)
        self.assertIn("gh repo create example/hpc-skill-hub", result.stdout)
        self.assertIn("--public", result.stdout)
        self.assertIn("--remote=origin", result.stdout)
        self.assertIn("--push", result.stdout)
        self.assertIn("has_discussions=true", result.stdout)

    def test_homepage_command_generator(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_homepage.py",
                "--repo",
                "example/hpc-skill-hub",
                "--pages-url",
                "https://example.github.io/hpc-skill-hub/",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("# HPC Skill Hub Repository Homepage Commands", result.stdout)
        self.assertIn(
            "gh repo edit example/hpc-skill-hub --homepage https://example.github.io/hpc-skill-hub/",
            result.stdout,
        )

        inspect_result = subprocess.run(
            [
                "python3",
                "tools/github_homepage.py",
                "--repo",
                "example/hpc-skill-hub",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn(
            "gh api repos/example/hpc-skill-hub/pages --jq .html_url",
            inspect_result.stdout,
        )
        self.assertIn(
            "gh repo edit example/hpc-skill-hub --homepage '<pages-url>'",
            inspect_result.stdout,
        )

    def test_homepage_command_generator_json(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_homepage.py",
                "--repo",
                "example/hpc-skill-hub",
                "--json",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["repo"], "example/hpc-skill-hub")
        purposes = [command["purpose"] for command in payload["commands"]]
        self.assertEqual(
            purposes,
            ["inspect_pages_url", "set_repository_homepage"],
        )

    def test_main_ruleset_is_review_oriented(self):
        with (ROOT / ".github" / "rulesets" / "main.json").open(encoding="utf-8") as handle:
            ruleset = json.load(handle)

        self.assertEqual(ruleset["target"], "branch")
        self.assertEqual(ruleset["enforcement"], "active")
        self.assertIn("refs/heads/main", ruleset["conditions"]["ref_name"]["include"])

        rules_by_type = {rule["type"]: rule for rule in ruleset["rules"]}
        self.assertIn("deletion", rules_by_type)
        self.assertIn("non_fast_forward", rules_by_type)
        self.assertEqual(
            rules_by_type["pull_request"]["parameters"]["required_approving_review_count"],
            1,
        )
        required_checks = rules_by_type["required_status_checks"]["parameters"]
        self.assertTrue(required_checks["strict_required_status_checks_policy"])
        self.assertIn(
            {"context": "skills"},
            required_checks["required_status_checks"],
        )
        self.assertIn(
            {"context": "wheel"},
            required_checks["required_status_checks"],
        )

    def test_validate_workflow_covers_release_artifacts(self):
        workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )

        for command in [
            "python3 tools/build_index.py --check",
            "python3 tools/build_health.py --check",
            "python3 tools/build_skill_quality.py --check",
            "python3 tools/build_compatibility.py --check",
            "python3 tools/build_package_data.py --check",
            "hpc-skill resolve slurm-submit-job --adapter example-campus-cluster --json",
            "python3 tools/agent_benchmark_harness.py --plan agent-bench/plans/smoke-v0.3.json --report docs/AGENT_BENCHMARK_SMOKE_PLAN.md --check",
            "python3 tools/agent_benchmark_harness.py --plan agent-bench/plans/evidence-v0.4.json --report docs/AGENT_BENCHMARK_V0_4_PLAN.md --check",
            "python3 tools/agent_benchmark_review.py --help",
            "python3 tools/validate_registry_artifacts.py --release-only",
            "python3 tools/review_packet.py --check",
            "python3 tools/validate_registry_artifacts.py",
            "python3 tools/audit_safety.py",
            "python3 -m unittest discover -s tests",
        ]:
            self.assertIn(command, workflow)
        self.assertIn("Smoke test installed package outside checkout", workflow)
        self.assertIn("cd /tmp", workflow)
        self.assertIn("hpc-skill health --json", workflow)
        self.assertIn("python3 -m hpc_skill_hub show slurm-submit-job --json", workflow)

    def test_package_workflow_builds_and_smoke_tests_wheel(self):
        workflow = (ROOT / ".github" / "workflows" / "package.yml").read_text(
            encoding="utf-8"
        )

        for text in [
            "name: Package",
            "wheel:",
            "python3 -m pip install --upgrade pip build twine",
            "python3 tools/build_package_data.py --check",
            "python3 tools/validate_registry_artifacts.py",
            "python3 -m build --sdist --wheel",
            "python3 -m twine check dist/*",
            "actions/attest@v4",
            "actions/upload-artifact@v4",
            "actions/download-artifact@v4",
            "registry/releases/${{ github.ref_name }}.json",
            "attestations: write",
            "id-token: write",
            "python3 -m venv /tmp/hpc-skill-hub-wheel",
            "--no-index --find-links",
            "hpc-skill health --json",
            "hpc-skill resolve slurm-submit-job --adapter example-campus-cluster --json",
            "python -m hpc_skill_hub show slurm-submit-job --json",
        ]:
            self.assertIn(text, workflow)

    def test_ruleset_command_generator(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_rulesets.py",
                "--repo",
                "example/hpc-skill-hub",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("gh api -X POST repos/example/hpc-skill-hub/rulesets", result.stdout)
        self.assertIn("--input .github/rulesets/main.json", result.stdout)

    def test_release_command_generator(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_release.py",
                "v0.1.0",
                "--repo",
                "example/hpc-skill-hub",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("git tag -a v0.1.0", result.stdout)
        self.assertIn("git push origin v0.1.0", result.stdout)
        self.assertIn("gh release create v0.1.0", result.stdout)
        self.assertIn("registry/releases/v0.1.0.json", result.stdout)
        self.assertIn("--notes-file docs/RELEASE_NOTES_v0.1.0.md", result.stdout)
        self.assertIn("--repo example/hpc-skill-hub", result.stdout)

    def test_seed_issue_command_generator(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_issues.py",
                "--repo",
                "example/hpc-skill-hub",
                "--include-pin-notes",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("gh issue create", result.stdout)
        self.assertIn("--body-file .github/seed-issues/community-call.md", result.stdout)
        self.assertIn(
            "--body-file .github/seed-issues/reviewed-skill-pilot.md",
            result.stdout,
        )
        self.assertIn("--label maturity-review", result.stdout)
        self.assertIn("--label help-wanted", result.stdout)
        self.assertIn("--repo example/hpc-skill-hub", result.stdout)
        self.assertIn(
            "# Pin the issue created from .github/seed-issues/community-call.md.",
            result.stdout,
        )

    def test_publish_plan_generator(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_publish_plan.py",
                "--owner",
                "example",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("# HPC Skill Hub GitHub Publish Plan", result.stdout)
        self.assertIn("# Repository: example/hpc-skill-hub", result.stdout)
        self.assertIn("python3 tools/launch_readiness.py", result.stdout)
        self.assertIn("python3 tools/launch_evidence.py", result.stdout)
        self.assertIn("python3 tools/review_candidates.py --limit 12", result.stdout)
        self.assertIn("python3 tools/review_packet.py --check", result.stdout)
        self.assertIn("python3 tools/proposal_evidence.py --owner example", result.stdout)
        self.assertIn("Review public launch packet and owner checklist", result.stdout)
        self.assertIn("docs/PUBLIC_LAUNCH_PACKET.md", result.stdout)
        self.assertIn("docs/GITHUB_OWNER_CHECKLIST.md", result.stdout)
        self.assertIn("gh repo create example/hpc-skill-hub", result.stdout)
        self.assertIn("gh label create safety-review", result.stdout)
        self.assertIn("Configure milestones", result.stdout)
        self.assertIn("repos/example/hpc-skill-hub/milestones", result.stdout)
        self.assertIn("Configure discussion categories", result.stdout)
        self.assertIn(".github/DISCUSSION_TEMPLATE/adoption.yml", result.stdout)
        self.assertIn("skill-coverage", result.stdout)
        self.assertIn("gh issue create", result.stdout)
        self.assertIn(
            "Apply branch rulesets after first green Validate and Package workflows",
            result.stdout,
        )
        self.assertIn("repos/example/hpc-skill-hub/rulesets", result.stdout)
        self.assertIn("gh release create v0.3.0", result.stdout)
        self.assertIn("Link Pages URL from repository homepage", result.stdout)
        self.assertIn("python3 tools/github_homepage.py", result.stdout)
        self.assertIn("Verify published repository state", result.stdout)
        self.assertIn("python3 tools/github_post_launch_check.py", result.stdout)

    def test_post_launch_check_dry_run(self):
        result = subprocess.run(
            [
                "python3",
                "tools/github_post_launch_check.py",
                "--repo",
                "example/hpc-skill-hub",
                "--dry-run",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("# HPC Skill Hub Post-Launch Check Commands", result.stdout)
        self.assertIn("gh api repos/example/hpc-skill-hub", result.stdout)
        self.assertIn("gh api repos/example/hpc-skill-hub --jq .homepage", result.stdout)
        self.assertIn("gh label list --repo example/hpc-skill-hub", result.stdout)
        self.assertIn(
            "gh api -X GET repos/example/hpc-skill-hub/milestones -f state=all",
            result.stdout,
        )
        self.assertIn("gh api repos/example/hpc-skill-hub/actions/workflows", result.stdout)
        self.assertIn(
            "gh api repos/example/hpc-skill-hub/pages --jq .html_url",
            result.stdout,
        )
        self.assertIn("python3 tools/github_homepage.py --repo example/hpc-skill-hub", result.stdout)
        self.assertIn("gh release view v0.3.0", result.stdout)

    def test_proposal_evidence_generator(self):
        markdown = subprocess.run(
            [
                "python3",
                "tools/proposal_evidence.py",
                "--owner",
                "example",
                "--review-limit",
                "3",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("# HPC Skill Hub Proposal Evidence", markdown.stdout)
        self.assertIn("## Community Assets", markdown.stdout)
        self.assertIn("Starter issues: 5", markdown.stdout)
        self.assertIn("## Reviewed Skill Pilot", markdown.stdout)

        json_result = subprocess.run(
            [
                "python3",
                "tools/proposal_evidence.py",
                "--owner",
                "example",
                "--json",
                "--review-limit",
                "3",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(json_result.stdout)
        with (ROOT / "registry" / "index.json").open(encoding="utf-8") as handle:
            index = json.load(handle)
        self.assertEqual(payload["registry"]["skill_count"], index["skill_count"])
        self.assertEqual(payload["community"]["seed_issue_count"], 5)
        self.assertLessEqual(len(payload["reviewed_skill_pilot"]["candidates"]), 3)
        self.assertIn("readiness", payload)

    def test_launch_evidence_generator(self):
        markdown = subprocess.run(
            [
                "python3",
                "tools/launch_evidence.py",
                "--owner",
                "example",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("# HPC Skill Hub Launch Evidence", markdown.stdout)
        self.assertIn("- Repository: `hpc-skill-hub`", markdown.stdout)
        self.assertIn("| Status | Check | Detail |", markdown.stdout)
        self.assertIn("registry-health", markdown.stdout)

        json_result = subprocess.run(
            [
                "python3",
                "tools/launch_evidence.py",
                "--owner",
                "example",
                "--json",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        evidence = json.loads(json_result.stdout)
        index = json.loads((ROOT / "registry" / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(evidence["repository"], "hpc-skill-hub")
        self.assertEqual(evidence["registry"]["skill_count"], index["skill_count"])
        self.assertIn("release_manifest", evidence)
        self.assertTrue(evidence["readiness"])

    def test_launch_readiness_audit(self):
        launch_readiness = load_launch_readiness_module()
        self.assertIn(
            "docs/PUBLIC_LAUNCH_PACKET.md",
            launch_readiness.REQUIRED_LAUNCH_FILES,
        )
        self.assertIn(
            "docs/GITHUB_OWNER_CHECKLIST.md",
            launch_readiness.REQUIRED_LAUNCH_FILES,
        )
        self.assertIn(
            "docs/POST_LAUNCH_VERIFICATION.md",
            launch_readiness.REQUIRED_LAUNCH_FILES,
        )
        self.assertIn(
            "tools/github_post_launch_check.py",
            launch_readiness.REQUIRED_LAUNCH_FILES,
        )
        self.assertIn(
            "tools/github_homepage.py",
            launch_readiness.REQUIRED_LAUNCH_FILES,
        )
        self.assertIn(
            "registry/skill-quality.json",
            launch_readiness.REQUIRED_LAUNCH_FILES,
        )
        self.assertIn(
            "docs/V0_4_COMPLETION.md",
            launch_readiness.REQUIRED_LAUNCH_FILES,
        )
        self.assertIn(
            "docs/AGENT_BENCHMARK_DASHBOARD.html",
            launch_readiness.REQUIRED_LAUNCH_FILES,
        )

        result = subprocess.run(
            [
                "python3",
                "tools/launch_readiness.py",
                "--owner",
                "example",
                "--json",
            ],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        by_name = {check["name"]: check for check in payload}
        self.assertEqual(by_name["required-files"]["status"], "OK")
        self.assertEqual(by_name["github-metadata"]["status"], "OK")
        self.assertEqual(by_name["discussion-templates"]["status"], "OK")
        self.assertEqual(by_name["github-milestones"]["status"], "OK")
        self.assertEqual(by_name["registry-index-current"]["status"], "OK")
        self.assertEqual(by_name["registry-health-current"]["status"], "OK")
        self.assertEqual(by_name["registry-artifact-contracts"]["status"], "OK")
        self.assertIn(by_name["git-remote"]["status"], {"OK", "WARN"})
        self.assertIn(by_name["gh-cli"]["status"], {"OK", "WARN"})
        if by_name["git-remote"]["status"] == "WARN":
            self.assertIn("example/hpc-skill-hub", by_name["git-remote"]["detail"])
        if by_name["gh-cli"]["status"] == "WARN":
            self.assertIn("--owner example", by_name["gh-cli"]["detail"])


if __name__ == "__main__":
    unittest.main()
