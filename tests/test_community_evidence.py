import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
FIXTURE = ROOT / "tests" / "fixtures" / "intake" / "benign-skill"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.community_evidence import (  # noqa: E402
    ADOPTION_SCHEMA_URL,
    MAX_EVIDENCE_ARTIFACT_BYTES,
    PACKET_SCHEMA_URL,
    REVIEW_SCHEMA_URL,
    STATUS_SCHEMA_URL,
    CommunityEvidenceError,
    add_artifact_digest,
    build_evidence_status,
    create_review_packet,
    ensure_distinct_artifacts,
    evidence_bindings,
    issue_summary,
    load_evidence_artifact,
    validate_adoption_report,
    validate_evidence_status,
    validate_independent_review,
    validate_review_packet,
    verify_review_packet,
)
from hpc_skill_hub.intake_receipt import (  # noqa: E402
    DECISION_SCHEMA_URL,
    IntakeReceiptError,
    create_receipt,
)
from hpc_skill_hub.security_policy import canonical_digest  # noqa: E402


class CommunityEvidenceTests(unittest.TestCase):
    def decision(self, draft):
        return {
            "$schema": DECISION_SCHEMA_URL,
            "schema_version": "0.1.0",
            "reviewer_id": "maintainer-a",
            "reviewer_role": "maintainer-intake",
            "reviewed_on": "2026-07-14",
            "disposition": "accept",
            "bindings": copy.deepcopy(draft["bindings"]),
            "acknowledged_finding_digests": [],
            "acknowledged_exception_ids": [],
            "rationale": "Reviewed the exact bounded intake evidence.",
        }

    def accepted_receipt(self, source=FIXTURE):
        draft = create_receipt(source)
        return create_receipt(source, decision=self.decision(draft))

    def packet(self, source=FIXTURE, *, risk="medium"):
        receipt = self.accepted_receipt(source)
        packet = create_review_packet(
            receipt,
            source,
            contribution_id="community-demo",
            version="0.1.0",
            risk_level=risk,
            domains=["scheduler"],
            submitter_id="contributor-a",
            artifact_url="https://example.com/community-demo-0.1.0.zip",
        )
        return receipt, packet

    def packet_for_domains(self, domains):
        receipt = self.accepted_receipt()
        packet = create_review_packet(
            receipt,
            FIXTURE,
            contribution_id="community-demo",
            version="0.1.0",
            risk_level="medium",
            domains=domains,
            submitter_id="contributor-a",
            artifact_url="https://example.com/community-demo-0.1.0.zip",
        )
        return receipt, packet

    def review(
        self,
        packet,
        *,
        scope="domain",
        reviewer="domain-reviewer-a",
        decision="approved",
    ):
        review = {
            "$schema": REVIEW_SCHEMA_URL,
            "schema_version": "0.1.0",
            "review_id": f"{scope}-review-1",
            "contribution": {"id": "community-demo", "version": "0.1.0"},
            "scope": scope,
            "reviewer_id": reviewer,
            "reviewed_on": "2026-07-15",
            "domain": "scheduler" if scope == "domain" else "safety",
            "decision": decision,
            "independence_attestation": True,
            "conflict_disclosure": "No conflicts disclosed.",
            "evidence_url": f"https://example.com/reviews/{scope}-review-1",
            "checklist": {
                "source_digest_verified": True,
                "scope_and_assumptions_reviewed": True,
                "examples_and_side_effects_reviewed": True,
                "risk_and_site_boundaries_reviewed": True,
                "references_reviewed": True,
                "public_safe_evidence_attested": True,
            },
            "bindings": evidence_bindings(packet),
            "notes": "Reviewed the exact public-safe contribution evidence.",
        }
        review["review_digest"] = canonical_digest(review)
        return review

    def adoption(self, packet, *, adopter="adopter-a", outcome="successful"):
        report = {
            "$schema": ADOPTION_SCHEMA_URL,
            "schema_version": "0.1.0",
            "report_id": "adoption-1",
            "contribution": {"id": "community-demo", "version": "0.1.0"},
            "adopter_id": adopter,
            "reported_on": "2026-07-15",
            "scope": "smoke-test",
            "outcome": outcome,
            "environment": {
                "type": "training-cluster",
                "scheduler": "slurm",
                "site_adapter_id": None,
                "public_documentation_urls": ["https://example.com/public-cluster-docs"],
                "private_details_omitted": True,
            },
            "observations": {
                "worked": ["The documented dry-run path produced the expected plan."],
                "changes_required": [],
                "blockers": [],
                "follow_up_urls": [],
            },
            "evidence_url": "https://example.com/adoption/adoption-1",
            "bindings": evidence_bindings(packet),
            "independent_adopter_attestation": True,
            "public_safe_attestation": True,
            "no_maturity_claim": True,
        }
        report["report_digest"] = canonical_digest(report)
        return report

    @staticmethod
    def resign(payload, digest_key):
        payload[digest_key] = canonical_digest(
            {key: value for key, value in payload.items() if key != digest_key}
        )

    def test_packet_is_deterministic_and_contains_no_instruction_content(self):
        receipt = self.accepted_receipt()
        first = create_review_packet(
            receipt,
            FIXTURE,
            contribution_id="community-demo",
            version="0.1.0",
            risk_level="medium",
            domains=["scheduler"],
            submitter_id="contributor-a",
            artifact_url="https://example.com/community-demo-0.1.0.zip",
        )
        second = create_review_packet(
            receipt,
            FIXTURE,
            contribution_id="community-demo",
            version="0.1.0",
            risk_level="medium",
            domains=["scheduler"],
            submitter_id="contributor-a",
            artifact_url="https://example.com/community-demo-0.1.0.zip",
        )

        self.assertEqual(first, second)
        self.assertEqual(first["$schema"], PACKET_SCHEMA_URL)
        self.assertTrue(first["requirements"]["safety_review_required"])
        self.assertNotIn("plan only", json.dumps(first, sort_keys=True))
        validate_review_packet(first)

    def test_packet_requires_fresh_accepted_p2_evidence(self):
        draft = create_receipt(FIXTURE)
        with self.assertRaisesRegex(CommunityEvidenceError, "accepted P2 receipt"):
            create_review_packet(
                draft,
                FIXTURE,
                contribution_id="community-demo",
                version="0.1.0",
                risk_level="low",
                domains=["scheduler"],
                submitter_id="contributor-a",
                artifact_url="https://example.com/community-demo.zip",
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package"
            shutil.copytree(FIXTURE, package)
            receipt, packet = self.packet(package)
            (package / "README.md").write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(IntakeReceiptError, "stale inventory"):
                verify_review_packet(packet, receipt, package)

    def test_packet_rejects_tampering_and_malformed_contribution(self):
        _, packet = self.packet()
        packet["summary"]["domain_review_complete"] = True
        with self.assertRaisesRegex(CommunityEvidenceError, "packet digest mismatch"):
            validate_review_packet(packet)

        _, malformed = self.packet()
        malformed["contribution"]["id"] = None
        self.resign(malformed, "packet_digest")
        with self.assertRaisesRegex(CommunityEvidenceError, "contribution id"):
            validate_review_packet(malformed)

        with self.assertRaisesRegex(CommunityEvidenceError, "non-empty strings"):
            create_review_packet(
                self.accepted_receipt(),
                FIXTURE,
                contribution_id="community-demo",
                version="0.1.0",
                risk_level="low",
                domains=[{"nested": "value"}],
                submitter_id="contributor-a",
                artifact_url="https://example.com/community-demo.zip",
            )

    def test_review_requires_independent_exact_bound_owner(self):
        _, packet = self.packet()
        review = self.review(packet, reviewer="contributor-a")
        with self.assertRaisesRegex(CommunityEvidenceError, "cannot be the submitter"):
            validate_independent_review(review, packet)

        review = self.review(packet, reviewer="maintainer-a")
        with self.assertRaisesRegex(CommunityEvidenceError, "intake decision maker"):
            validate_independent_review(review, packet)

        review = self.review(packet)
        review["bindings"]["source_digest"] = "0" * 64
        self.resign(review, "review_digest")
        with self.assertRaisesRegex(CommunityEvidenceError, "stale packet bindings"):
            validate_independent_review(review, packet)

    def test_approved_review_requires_complete_checklist(self):
        _, packet = self.packet()
        review = self.review(packet)
        review["checklist"]["references_reviewed"] = False
        self.resign(review, "review_digest")
        with self.assertRaisesRegex(CommunityEvidenceError, "every checklist"):
            validate_independent_review(review, packet)

    def test_required_domain_and_safety_reviews_need_different_people(self):
        _, packet = self.packet()
        domain = self.review(packet, reviewer="reviewer-a")
        safety = self.review(packet, scope="safety", reviewer="reviewer-a")
        with self.assertRaisesRegex(CommunityEvidenceError, "different owners"):
            build_evidence_status(packet, [domain, safety])

    def test_domain_gate_requires_every_declared_domain(self):
        _, packet = self.packet_for_domains(["scheduler", "storage"])
        scheduler = self.review(packet)
        partial = build_evidence_status(packet, [scheduler])
        storage = self.review(packet, reviewer="storage-reviewer-a")
        storage["review_id"] = "storage-review-1"
        storage["domain"] = "storage"
        self.resign(storage, "review_digest")
        complete = build_evidence_status(packet, [scheduler, storage])

        self.assertEqual(partial["gates"]["domain_review"], "pending")
        self.assertEqual(partial["evidence"]["approved_domains"], ["scheduler"])
        self.assertEqual(complete["gates"]["domain_review"], "passed")
        self.assertEqual(complete["evidence"]["approved_domains"], ["scheduler", "storage"])

    def test_adoption_is_public_safe_independent_and_not_a_maturity_claim(self):
        _, packet = self.packet()
        report = self.adoption(packet, adopter="contributor-a")
        with self.assertRaisesRegex(CommunityEvidenceError, "cannot be the submitter"):
            validate_adoption_report(report, packet)

        report = self.adoption(packet)
        report["environment"]["public_documentation_urls"] = ["https://127.0.0.1/private"]
        self.resign(report, "report_digest")
        with self.assertRaisesRegex(CommunityEvidenceError, "private, loopback"):
            validate_adoption_report(report, packet)

        report = self.adoption(packet)
        report["evidence_url"] = "https://review.internal/adoption"
        self.resign(report, "report_digest")
        with self.assertRaisesRegex(CommunityEvidenceError, "public DNS name"):
            validate_adoption_report(report, packet)

        report = self.adoption(packet)
        report["no_maturity_claim"] = False
        self.resign(report, "report_digest")
        with self.assertRaisesRegex(CommunityEvidenceError, "cannot claim maturity"):
            validate_adoption_report(report, packet)

    def test_adoption_and_review_records_need_different_owners(self):
        _, packet = self.packet()
        review = self.review(packet, reviewer="shared-owner")
        adoption = self.adoption(packet, adopter="shared-owner")
        with self.assertRaisesRegex(CommunityEvidenceError, "different owners"):
            build_evidence_status(packet, [review], [adoption])

    def test_generated_artifacts_cannot_overwrite_inputs(self):
        path = Path("review.json")
        with self.assertRaisesRegex(CommunityEvidenceError, "must not reuse"):
            ensure_distinct_artifacts(
                [(path, "intake receipt"), (path, "review packet output")]
            )

    def test_external_evidence_loader_rejects_links_and_oversized_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(CommunityEvidenceError, "regular file"):
                load_evidence_artifact(link, "review")

            oversized = root / "oversized.json"
            with oversized.open("wb") as handle:
                handle.truncate(MAX_EVIDENCE_ARTIFACT_BYTES + 1)
            with self.assertRaisesRegex(CommunityEvidenceError, "exceeds"):
                load_evidence_artifact(oversized, "review")

    def test_digest_helper_completes_review_and_adoption_records(self):
        _, packet = self.packet()
        review = self.review(packet)
        review.pop("review_digest")
        report = self.adoption(packet)
        report.pop("report_digest")

        completed_review = add_artifact_digest(review)
        completed_report = add_artifact_digest(report)
        validate_independent_review(completed_review, packet)
        validate_adoption_report(completed_report, packet)

    def test_status_keeps_all_gates_separate_and_never_promotes_maturity(self):
        _, packet = self.packet()
        domain = self.review(packet)
        safety = self.review(packet, scope="safety", reviewer="safety-reviewer-a")
        adoption = self.adoption(packet)
        status = build_evidence_status(packet, [domain, safety], [adoption])

        self.assertEqual(status["$schema"], STATUS_SCHEMA_URL)
        self.assertEqual(status["summary"]["status"], "review-complete")
        self.assertEqual(status["gates"]["domain_review"], "passed")
        self.assertEqual(status["gates"]["safety_review"], "passed")
        self.assertEqual(status["gates"]["adoption_evidence"], "recorded")
        self.assertEqual(status["gates"]["maturity_promotion"], "not-authorized")
        self.assertFalse(status["summary"]["maturity_promotion_authorized"])
        self.assertIsNone(status["owners"]["maturity_decider"])
        validate_evidence_status(status, packet)

        status["summary"]["maturity_promotion_authorized"] = True
        self.resign(status, "status_digest")
        with self.assertRaisesRegex(CommunityEvidenceError, "status summary mismatch"):
            validate_evidence_status(status, packet)

    def test_low_risk_packet_marks_absent_safety_review_not_required(self):
        _, packet = self.packet(risk="low")
        domain = self.review(packet)
        status = build_evidence_status(packet, [domain])

        self.assertEqual(status["gates"]["safety_review"], "not-required")
        self.assertEqual(status["summary"]["status"], "review-complete")
        self.assertFalse(status["summary"]["maturity_promotion_authorized"])

    def test_issue_summary_binds_public_digests_and_validates_status(self):
        _, packet = self.packet()
        status = build_evidence_status(packet)
        summary = issue_summary(packet, status)

        self.assertIn(packet["bindings"]["source_digest"], summary)
        self.assertIn(packet["bindings"]["receipt_digest"], summary)
        self.assertIn("Registry maturity decision: separate pull request", summary)
        self.assertNotIn("plan only", summary)

        status["bindings"]["packet_digest"] = "0" * 64
        self.resign(status, "status_digest")
        with self.assertRaisesRegex(CommunityEvidenceError, "stale packet bindings"):
            issue_summary(packet, status)

    def test_public_schemas_validate_all_p3_artifacts(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schemas = {}
        for name in (
            "community-skill-review-packet.schema.json",
            "community-skill-independent-review.schema.json",
            "community-skill-adoption-report.schema.json",
            "community-skill-evidence-status.schema.json",
        ):
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            schemas[schema["$id"]] = schema
        _, packet = self.packet()
        review = self.review(packet)
        report = self.adoption(packet)
        status = build_evidence_status(packet, [review], [report])

        for artifact in (packet, review, report, status):
            Draft202012Validator(schemas[artifact["$schema"]]).validate(artifact)

    def test_installable_packet_and_standalone_check_cli(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            package = root / "package"
            shutil.copytree(FIXTURE, package)
            receipt = self.accepted_receipt(package)
            receipt_path = root / "receipt.json"
            packet_path = root / "packet.json"
            summary_path = root / "summary.md"
            review_draft_path = root / "review-draft.json"
            review_path = root / "review.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            created = subprocess.run(
                [
                    "python3",
                    "tools/hpc_skill.py",
                    "evidence",
                    "packet",
                    str(receipt_path),
                    "--source",
                    str(package),
                    "--id",
                    "community-demo",
                    "--version",
                    "0.1.0",
                    "--risk",
                    "medium",
                    "--domain",
                    "scheduler",
                    "--submitter",
                    "contributor-a",
                    "--artifact-url",
                    "https://example.com/community-demo.zip",
                    "--output",
                    str(packet_path),
                    "--summary-output",
                    str(summary_path),
                    "--json",
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            review_draft = self.review(packet)
            review_draft.pop("review_digest")
            review_draft_path.write_text(json.dumps(review_draft), encoding="utf-8")
            digested = subprocess.run(
                [
                    "python3",
                    "tools/hpc_skill.py",
                    "evidence",
                    "digest",
                    str(review_draft_path),
                    "--output",
                    str(review_path),
                    "--json",
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            checked = subprocess.run(
                [
                    "python3",
                    "tools/community_review_evidence.py",
                    "check",
                    str(packet_path),
                    "--receipt",
                    str(receipt_path),
                    "--source",
                    str(package),
                    "--review",
                    str(review_path),
                    "--json",
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(json.loads(created.stdout)["$schema"], PACKET_SCHEMA_URL)
            self.assertTrue(packet_path.is_file())
            self.assertIn("Immutable Evidence", summary_path.read_text(encoding="utf-8"))
            self.assertEqual(digested.returncode, 0, digested.stderr)
            self.assertIn("review_digest", json.loads(digested.stdout))
            self.assertEqual(checked.returncode, 0, checked.stderr)
            status = json.loads(checked.stdout)
            self.assertEqual(status["summary"]["status"], "awaiting-independent-review")
            self.assertEqual(status["evidence"]["approved_domains"], ["scheduler"])


if __name__ == "__main__":
    unittest.main()
