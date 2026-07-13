import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_tool():
    spec = importlib.util.spec_from_file_location(
        "build_skill_quality", ROOT / "tools" / "build_skill_quality.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SkillQualityTests(unittest.TestCase):
    def test_adjacent_markdown_headings_are_all_detected(self):
        text = "# Example\n\n## Safety Notes\nRead only.\n\n## Success Criteria\nDone.\n"

        self.assertEqual(
            self.quality.headings(text),
            {"safety notes", "success criteria"},
        )
        self.assertEqual(
            self.quality.section_text(
                text, self.quality.HEADING_ALIASES["validation"]
            ),
            "Done.",
        )

    def setUp(self):
        self.quality = load_tool()
        self.payload = self.quality.quality_payload()
        self.by_id = {item["id"]: item for item in self.payload["skills"]}

    def test_quality_report_covers_registry(self):
        index = json.loads((ROOT / "registry" / "index.json").read_text(encoding="utf-8"))
        index_by_id = {item["id"]: item for item in index["skills"]}
        self.assertEqual(self.payload["skill_count"], index["skill_count"])
        self.assertEqual(set(self.by_id), {item["id"] for item in index["skills"]})
        self.assertEqual(sum(self.payload["band_counts"].values()), index["skill_count"])
        for skill_id, assessment in self.by_id.items():
            self.assertEqual(assessment["version"], index_by_id[skill_id]["version"])
            self.assertEqual(assessment["status"], index_by_id[skill_id]["status"])

    def test_each_assessment_has_stable_dimensions(self):
        expected = {
            "scope",
            "prerequisites",
            "workflow",
            "inputs_outputs",
            "validation",
            "failure_handling",
            "safety",
            "resource_impact",
            "cleanup",
            "site_boundary",
        }
        for item in self.payload["skills"]:
            self.assertEqual({dimension["id"] for dimension in item["dimensions"]}, expected)
            self.assertGreaterEqual(item["score"], 0)
            self.assertLessEqual(item["score"], 100)

    def test_agent_benchmark_skills_are_tier_one(self):
        for skill_id in ["gpu-sanity-check", "job-failure-triage", "slurm-submit-job"]:
            self.assertEqual(
                self.by_id[skill_id]["release_priority"], "tier-1-agent-evidence"
            )

    def test_first_quality_pilot_skills_cover_every_dimension(self):
        for skill_id in ["gpu-sanity-check", "job-failure-triage", "slurm-submit-job"]:
            self.assertEqual(self.by_id[skill_id]["band"], "strong")
            self.assertEqual(self.by_id[skill_id]["gaps"], [])

    def test_second_quality_pilot_skills_cover_every_dimension(self):
        for skill_id in [
            "slurm-pending-reason-triage",
            "mpi-hello-and-benchmark",
            "quota-and-filesystem-triage",
        ]:
            self.assertEqual(self.by_id[skill_id]["band"], "strong")
            self.assertEqual(self.by_id[skill_id]["gaps"], [])

    def test_all_tier_one_agent_evidence_skills_cover_every_dimension(self):
        tier_one = [
            item
            for item in self.payload["skills"]
            if item["release_priority"] == "tier-1-agent-evidence"
        ]
        self.assertEqual(len(tier_one), 9)
        for assessment in tier_one:
            self.assertEqual(assessment["band"], "strong")
            self.assertEqual(assessment["gaps"], [])

    def test_short_skill_exposes_actionable_gaps(self):
        easybuild = self.by_id["easybuild-install-software"]
        self.assertEqual(easybuild["band"], "needs-depth")
        self.assertIn("documentation_depth", easybuild["gaps"])
        self.assertIn("failure_handling", easybuild["gaps"])

    def test_generated_outputs_are_current(self):
        self.assertEqual(self.quality.check_outputs(self.payload), [])


if __name__ == "__main__":
    unittest.main()
