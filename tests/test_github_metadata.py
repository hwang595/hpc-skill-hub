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


if __name__ == "__main__":
    unittest.main()
