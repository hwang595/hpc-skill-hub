import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GovernanceDocsTests(unittest.TestCase):
    def test_rfc_template_has_required_sections(self):
        template = (ROOT / "docs" / "rfcs" / "0000-template.md").read_text(
            encoding="utf-8"
        )
        for heading in [
            "## Summary",
            "## Motivation",
            "## Proposal",
            "## Compatibility",
            "## Validation",
            "## Rollout",
            "## Safety And Privacy",
            "## Open Questions",
        ]:
            self.assertIn(heading, template)

    def test_seed_decision_record_exists(self):
        decision = (
            ROOT / "docs" / "decisions" / "0001-record-seed-governance.md"
        ).read_text(encoding="utf-8")
        self.assertIn("# Decision 0001", decision)
        self.assertIn("Accepted", decision)
        self.assertIn("Use lightweight repository maintainer ownership", decision)

    def test_rfc_issue_template_has_label(self):
        labels_path = ROOT / ".github" / "labels.json"
        labels = {label["name"] for label in json.loads(labels_path.read_text())}
        template = (
            ROOT / ".github" / "ISSUE_TEMPLATE" / "rfc_proposal.md"
        ).read_text(encoding="utf-8")
        self.assertIn("labels: [\"rfc\"]", template)
        self.assertIn("rfc", labels)
        self.assertIn("decision-record", labels)

    def test_maturity_review_template_and_docs(self):
        labels_path = ROOT / ".github" / "labels.json"
        labels = {label["name"] for label in json.loads(labels_path.read_text())}
        template = (
            ROOT / ".github" / "ISSUE_TEMPLATE" / "maturity_review.md"
        ).read_text(encoding="utf-8")
        guide = (ROOT / "docs" / "MATURITY_REVIEW.md").read_text(encoding="utf-8")

        self.assertIn("labels: [\"maturity-review\"]", template)
        self.assertIn("maturity-review", labels)
        for maturity in ["seed", "reviewed", "field-tested", "maintained"]:
            self.assertIn(maturity, guide)
        self.assertIn("make check", guide)

    def test_adoption_report_template_and_playbook(self):
        labels_path = ROOT / ".github" / "labels.json"
        labels = {label["name"] for label in json.loads(labels_path.read_text())}
        template = (
            ROOT / ".github" / "ISSUE_TEMPLATE" / "adoption_report.md"
        ).read_text(encoding="utf-8")
        playbook = (ROOT / "docs" / "ADOPTER_PLAYBOOK.md").read_text(
            encoding="utf-8"
        )
        worksheet = (ROOT / "docs" / "ADOPTION_WORKSHEET.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("labels: [\"adoption\"]", template)
        self.assertIn("adoption", labels)
        for heading in ["## 30 Day Pilot", "## 60 Day Pilot", "## 90 Day Pilot"]:
            self.assertIn(heading, playbook)
        self.assertIn("Public-Safe Evidence", playbook)
        for heading in [
            "## Pilot Metadata",
            "## Public-Safe Checklist",
            "## 30 Day Checkpoint",
            "## 60 Day Checkpoint",
            "## 90 Day Checkpoint",
        ]:
            self.assertIn(heading, worksheet)

    def test_review_routing_doc_and_codeowners_placeholder(self):
        routing = (ROOT / "docs" / "REVIEW_ROUTING.md").read_text(
            encoding="utf-8"
        )
        codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(
            encoding="utf-8"
        )

        for heading in [
            "## Path Routing",
            "## Domain Routing",
            "## Risk Routing",
            "## Label Routing",
            "## CODEOWNERS Update Checklist",
        ]:
            self.assertIn(heading, routing)
        self.assertIn("safety-review", routing)
        self.assertIn("maturity-review", routing)
        self.assertIn("docs/REVIEW_ROUTING.md", codeowners)

    def test_triage_runbook_and_labels(self):
        labels_path = ROOT / ".github" / "labels.json"
        labels = {label["name"] for label in json.loads(labels_path.read_text())}
        runbook = (ROOT / "docs" / "TRIAGE_RUNBOOK.md").read_text(
            encoding="utf-8"
        )

        for heading in [
            "## Intake Loop",
            "## Issue Triage",
            "## Pull Request Triage",
            "## Escalation Rules",
            "## Response Targets",
        ]:
            self.assertIn(heading, runbook)
        for label in ["needs-triage", "needs-domain-review", "safety-review"]:
            self.assertIn(label, labels)
            self.assertIn(label, runbook)

    def test_integration_guide_and_template(self):
        labels_path = ROOT / ".github" / "labels.json"
        labels = {label["name"] for label in json.loads(labels_path.read_text())}
        template = (
            ROOT / ".github" / "ISSUE_TEMPLATE" / "integration_request.md"
        ).read_text(encoding="utf-8")
        guide = (ROOT / "docs" / "INTEGRATION_GUIDE.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("labels: [\"integration\"]", template)
        self.assertIn("integration", labels)
        for heading in [
            "## Integration Surfaces",
            "## Consumption Contract",
            "## Assistant And Agent Integrations",
            "## Compatibility And Change Management",
            "## Validation Checklist",
        ]:
            self.assertIn(heading, guide)
        self.assertIn("registry/index.json", guide)
        self.assertIn("risk_level", guide)
        self.assertIn("site adapter", guide)


if __name__ == "__main__":
    unittest.main()
