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

        self.assertIn("labels: [\"adoption\"]", template)
        self.assertIn("adoption", labels)
        for heading in ["## 30 Day Pilot", "## 60 Day Pilot", "## 90 Day Pilot"]:
            self.assertIn(heading, playbook)
        self.assertIn("Public-Safe Evidence", playbook)

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


if __name__ == "__main__":
    unittest.main()
