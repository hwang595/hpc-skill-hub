import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
            "python3 tools/build_compatibility.py --check",
            "python3 tools/build_package_data.py --check",
            "python3 tools/build_release_manifest.py v0.1.0 --check",
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
            "python3 -m venv /tmp/hpc-skill-hub-wheel",
            "--no-index --find-links",
            "hpc-skill health --json",
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
        self.assertIn("gh repo create example/hpc-skill-hub", result.stdout)
        self.assertIn("gh label create safety-review", result.stdout)
        self.assertIn("gh issue create", result.stdout)
        self.assertIn("repos/example/hpc-skill-hub/rulesets", result.stdout)
        self.assertIn("gh release create v0.1.0", result.stdout)

    def test_launch_readiness_audit(self):
        result = subprocess.run(
            [
                "python3",
                "tools/launch_readiness.py",
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
        self.assertEqual(by_name["registry-index-current"]["status"], "OK")
        self.assertEqual(by_name["registry-health-current"]["status"], "OK")
        self.assertEqual(by_name["registry-artifact-contracts"]["status"], "OK")
        self.assertIn(by_name["git-remote"]["status"], {"OK", "WARN"})
        self.assertIn(by_name["gh-cli"]["status"], {"OK", "WARN"})


if __name__ == "__main__":
    unittest.main()
