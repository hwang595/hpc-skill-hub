import json
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub import reviews


def run_cmd(*args, cwd=ROOT, env=None):
    command_env = os.environ.copy()
    if env:
        command_env.update(env)
    return subprocess.run(
        args,
        cwd=str(cwd),
        env=command_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class SkillReviewTests(unittest.TestCase):
    def setUp(self):
        self.index = reviews.load_json(ROOT / "registry" / "index.json")
        self.quality = reviews.load_json(ROOT / "registry" / "skill-quality.json")
        self.payload = reviews.build_status(ROOT, "v0.4.0")
        self.by_id = {item["id"]: item for item in self.payload["skills"]}

    def assess_temporary_bundle(self, source_id, mutate):
        source = ROOT / "reviews" / "v0.4.0" / f"{source_id}.json"
        bundle = reviews.load_json(source)
        mutate(bundle)
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            dir=ROOT / "reviews" / "v0.4.0",
            encoding="utf-8",
            delete=False,
        ) as handle:
            json.dump(bundle, handle, indent=2)
            handle.write("\n")
            path = Path(handle.name)
        try:
            return reviews.assess_bundle(ROOT, path, self.index, self.quality)
        finally:
            path.unlink()

    def test_pilot_queue_is_static_ready_but_not_promoted(self):
        self.assertEqual(self.payload["candidate_count"], 5)
        self.assertEqual(self.payload["static_ready_count"], 5)
        self.assertEqual(self.payload["promotion_ready_count"], 0)
        self.assertEqual(
            self.payload["status_counts"],
            {
                "blocked": 0,
                "awaiting-review": 5,
                "promotion-ready": 0,
                "promoted": 0,
            },
        )
        for assessment in self.payload["skills"]:
            self.assertEqual(assessment["validation_errors"], [])
            self.assertTrue(assessment["static_ready"])
            self.assertEqual(assessment["status"], "awaiting-review")
            self.assertIn(
                "domain-review",
                {item["id"] for item in assessment["blockers"]},
            )

    def test_admin_scope_requires_safety_review(self):
        shared = self.by_id["shared-project-permissions-triage"]
        self.assertTrue(shared["safety_review_required"])
        self.assertIn("safety-review", {item["id"] for item in shared["blockers"]})
        self.assertFalse(self.by_id["job-failure-triage"]["safety_review_required"])

    def test_stale_quality_snapshot_blocks_bundle(self):
        assessment = self.assess_temporary_bundle(
            "job-failure-triage",
            lambda bundle: bundle["quality_snapshot"].update({"score": 1}),
        )
        self.assertEqual(assessment["status"], "blocked")
        self.assertIn("quality_snapshot.score is stale", assessment["validation_errors"])

    def test_commit_pinned_domain_approval_opens_gate(self):
        commit = "a" * 40

        def approve(bundle):
            bundle["review_issue"] = (
                "https://github.com/hwang595/hpc-skill-hub/issues/100"
            )
            bundle["review_commit"] = commit
            bundle["domain_reviews"] = [
                {
                    "reviewer": "independent-reviewer",
                    "domain": "scheduler operations",
                    "decision": "approved",
                    "independence_attestation": True,
                    "reviewed_at": "2026-07-13T00:00:00Z",
                    "review_commit": commit,
                    "evidence_url": "https://github.com/hwang595/hpc-skill-hub/issues/100#issuecomment-1",
                    "notes": "Public-safe domain review completed.",
                }
            ]
            bundle["decision"] = {
                "status": "approved",
                "decided_by": "registry-maintainer",
                "decided_at": "2026-07-13T01:00:00Z",
                "notes": "Approved for a maturity promotion pull request.",
            }

        assessment = self.assess_temporary_bundle("job-failure-triage", approve)
        self.assertEqual(assessment["validation_errors"], [])
        self.assertTrue(assessment["promotion_ready"])
        self.assertEqual(assessment["status"], "promotion-ready")
        self.assertEqual(assessment["blockers"], [])

    def test_generated_review_outputs_are_current(self):
        result = run_cmd("python3", "tools/build_skill_reviews.py", "--check")
        self.assertIn("Skill review status is current", result.stdout)

    def test_review_cli_exposes_queue_status_and_bundle_check(self):
        candidates = run_cmd(
            "python3", "tools/hpc_skill.py", "review", "candidates", "--json"
        )
        candidate_payload = json.loads(candidates.stdout)
        self.assertEqual(candidate_payload["candidate_count"], 5)
        self.assertEqual(candidate_payload["promotion_ready_count"], 0)

        status = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "review",
            "status",
            "shared-project-permissions-triage",
            "--json",
        )
        self.assertTrue(json.loads(status.stdout)["safety_review_required"])

        check = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "review",
            "check",
            "reviews/v0.4.0/job-failure-triage.json",
            "--json",
        )
        check_payload = json.loads(check.stdout)
        self.assertTrue(check_payload["ok"])
        self.assertFalse(check_payload["promotion_ready"])

    def test_installed_snapshot_supports_review_discovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            package_copy = Path(tmpdir) / "hpc_skill_hub"
            shutil.copytree(ROOT / "src" / "hpc_skill_hub", package_copy)
            result = run_cmd(
                "python3",
                "-m",
                "hpc_skill_hub",
                "review",
                "candidates",
                "--json",
                cwd=tmpdir,
                env={"PYTHONPATH": tmpdir},
            )
        self.assertEqual(json.loads(result.stdout)["candidate_count"], 5)

    def test_pages_build_copies_dashboard_and_source_bundles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "site" / "index.html"
            run_cmd("python3", "tools/build_site.py", "--output", str(output))
            self.assertTrue(
                (output.parent / "docs" / "SKILL_REVIEW_DASHBOARD.html").is_file()
            )
            self.assertTrue(
                (
                    output.parent
                    / "reviews"
                    / "v0.4.0"
                    / "job-failure-triage.json"
                ).is_file()
            )

    def test_release_manifest_includes_review_evidence(self):
        spec = importlib.util.spec_from_file_location(
            "build_release_manifest", ROOT / "tools" / "build_release_manifest.py"
        )
        module = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(module)
        output = ROOT / "registry" / "releases" / "v0.4.0.json"
        paths = {
            str(path.relative_to(ROOT))
            for path in module.iter_release_files(output)
        }
        self.assertIn(
            "reviews/v0.4.0/job-failure-triage.json",
            paths,
        )


if __name__ == "__main__":
    unittest.main()
