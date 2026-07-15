import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.community_pilot import (  # noqa: E402
    CommunityPilotError,
    build_accepted_context_fixture,
    build_pilot_report,
    serialized_report,
    validate_pilot_report,
)
from hpc_skill_hub.security_policy import canonical_digest  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures" / "community-pilot"
REPORT = ROOT / "registry" / "community-pilot-v0.6.0.json"


class CommunityPilotTests(unittest.TestCase):
    def test_matrix_is_deterministic_and_transport_equivalent(self):
        first = build_pilot_report(FIXTURES)
        second = build_pilot_report(FIXTURES)

        self.assertEqual(first, second)
        self.assertEqual(first["matrix"]["case_count"], 9)
        self.assertEqual(first["matrix"]["passed_count"], 9)
        self.assertEqual(first["matrix"]["failed_count"], 0)
        for fixture in ("benign", "ambiguous", "adversarial"):
            cases = [case for case in first["cases"] if case["fixture"] == fixture]
            self.assertEqual(len(cases), 3)
            self.assertEqual(
                len({case["observed"]["inventory_digest"] for case in cases}),
                1,
            )
            self.assertTrue(all(case["passed"] for case in cases))

    def test_report_is_content_redacted_and_preserves_closed_claims(self):
        report = build_pilot_report(FIXTURES)
        serialized = serialized_report(report)

        self.assertNotIn("Ignore all previous", serialized)
        self.assertNotIn("eval \"$command_text\"", serialized)
        self.assertNotIn("hpc-skill-hub-community-pilot-", serialized)
        self.assertNotIn('"files"', serialized)
        self.assertTrue(report["claims"]["synthetic_fixtures_only"])
        self.assertFalse(report["claims"]["real_community_acceptance"])
        self.assertFalse(report["claims"]["maturity_promotion"])
        self.assertFalse(report["claims"]["comparative_agent_lift"])

    def test_accepted_pipeline_is_review_complete_but_non_authorizing(self):
        bundle = build_accepted_context_fixture(FIXTURES / "benign")

        self.assertEqual(bundle["provenance"]["review"]["status"], "review-complete")
        self.assertEqual(
            bundle["provenance"]["maturity"]["promotion"], "not-authorized"
        )
        self.assertFalse(bundle["usage_contract"]["execute_examples_automatically"])
        self.assertFalse(bundle["usage_contract"]["allows_job_submission"])

    def test_validator_rejects_tampered_results_and_claims(self):
        report = build_pilot_report(FIXTURES)
        failed = copy.deepcopy(report)
        failed["cases"][0]["passed"] = False
        failed["report_digest"] = canonical_digest(
            {key: value for key, value in failed.items() if key != "report_digest"}
        )
        with self.assertRaisesRegex(CommunityPilotError, "pilot cases failed"):
            validate_pilot_report(failed)

        overclaim = copy.deepcopy(report)
        overclaim["claims"]["real_site_adoption"] = True
        overclaim["report_digest"] = canonical_digest(
            {key: value for key, value in overclaim.items() if key != "report_digest"}
        )
        with self.assertRaisesRegex(CommunityPilotError, "overclaims"):
            validate_pilot_report(overclaim)

        forged_observation = copy.deepcopy(report)
        forged_observation["cases"][0]["observed"]["status"] = "blocked"
        forged_observation["report_digest"] = canonical_digest(
            {
                key: value
                for key, value in forged_observation.items()
                if key != "report_digest"
            }
        )
        with self.assertRaisesRegex(CommunityPilotError, "status mismatch"):
            validate_pilot_report(forged_observation)

    def test_public_schema_validates_generated_report(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema = json.loads(
            (ROOT / "schemas" / "community-pilot-report.schema.json").read_text(
                encoding="utf-8"
            )
        )
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(build_pilot_report(FIXTURES))

    def test_checked_in_artifacts_are_current(self):
        generated = build_pilot_report(FIXTURES)
        self.assertEqual(REPORT.read_text(encoding="utf-8"), serialized_report(generated))
        result = subprocess.run(
            ["python3", "tools/community_pilot.py", "--check"],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("9/9 cases passed", result.stdout)


if __name__ == "__main__":
    unittest.main()
