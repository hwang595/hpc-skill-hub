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
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.community_context import (  # noqa: E402
    CommunityContextError,
    SCHEMA_URL,
    build_community_context,
    community_context_metadata,
    load_community_context,
    render_community_context,
    validate_community_context,
)
from hpc_skill_hub.community_evidence import (  # noqa: E402
    REVIEW_SCHEMA_URL,
    create_review_packet,
    evidence_bindings,
)
from hpc_skill_hub.intake_receipt import DECISION_SCHEMA_URL, create_receipt  # noqa: E402
from hpc_skill_hub.mcp_server import (  # noqa: E402
    community_context_catalog,
    community_context_resource,
)
from hpc_skill_hub.security_policy import canonical_digest  # noqa: E402


try:
    from mcp.shared.memory import create_connected_server_and_client_session
    from pydantic import AnyUrl
except ImportError:
    create_connected_server_and_client_session = None
    AnyUrl = None


FIXTURE = ROOT / "tests" / "fixtures" / "intake" / "benign-skill"


class CommunityContextTests(unittest.TestCase):
    def accepted_receipt(self, source=FIXTURE):
        draft = create_receipt(source)
        decision = {
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
        return create_receipt(source, decision=decision)

    def packet(self, source=FIXTURE):
        receipt = self.accepted_receipt(source)
        packet = create_review_packet(
            receipt,
            source,
            contribution_id="community-demo",
            version="0.1.0",
            risk_level="medium",
            domains=["scheduler"],
            submitter_id="contributor-a",
            artifact_url="https://example.com/community-demo-0.1.0.zip",
        )
        return receipt, packet

    def review(self, packet, scope="domain"):
        reviewer = "domain-reviewer-a" if scope == "domain" else "safety-reviewer-a"
        review = {
            "$schema": REVIEW_SCHEMA_URL,
            "schema_version": "0.1.0",
            "review_id": f"{scope}-review-1",
            "contribution": {"id": "community-demo", "version": "0.1.0"},
            "scope": scope,
            "reviewer_id": reviewer,
            "reviewed_on": "2026-07-15",
            "domain": "scheduler" if scope == "domain" else "safety",
            "decision": "approved",
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

    def bundle(self, source=FIXTURE):
        receipt, packet = self.packet(source)
        reviews = [self.review(packet), self.review(packet, "safety")]
        return build_community_context(source, receipt, packet, reviews)

    def test_build_reconstructs_exact_reviewed_content_and_provenance(self):
        bundle = self.bundle()

        self.assertEqual(bundle["$schema"], SCHEMA_URL)
        self.assertEqual(bundle["provenance"]["review"]["status"], "review-complete")
        self.assertEqual(bundle["provenance"]["maturity"]["promotion"], "not-authorized")
        self.assertTrue(bundle["files"])
        self.assertTrue(any("plan only" in item["content"] for item in bundle["files"]))
        self.assertEqual(
            bundle["content_manifest"]["digest"],
            bundle["evidence"]["receipt"]["accepted_context"]["accepted_digest"],
        )
        validate_community_context(bundle)

    def test_incomplete_review_cannot_expose_content(self):
        receipt, packet = self.packet()
        with self.assertRaisesRegex(CommunityContextError, "completed domain"):
            build_community_context(FIXTURE, receipt, packet, [self.review(packet)])

    def test_stale_source_and_tampered_content_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            package = Path(tmpdir) / "package"
            shutil.copytree(FIXTURE, package)
            receipt, packet = self.packet(package)
            reviews = [self.review(packet), self.review(packet, "safety")]
            (package / "README.md").write_text("changed\n", encoding="utf-8")
            with self.assertRaisesRegex(Exception, "stale inventory"):
                build_community_context(package, receipt, packet, reviews)

        bundle = self.bundle()
        bundle["files"][0]["content"] += "tampered"
        bundle["bundle_digest"] = canonical_digest(
            {key: value for key, value in bundle.items() if key != "bundle_digest"}
        )
        with self.assertRaisesRegex(CommunityContextError, "byte count mismatch"):
            validate_community_context(bundle)

    def test_loader_rejects_forged_limits_types_and_identifiers(self):
        limits = self.bundle()
        limits["limits"]["max_total_bytes"] -= 1
        limits["bundle_digest"] = canonical_digest(
            {key: value for key, value in limits.items() if key != "bundle_digest"}
        )
        with self.assertRaisesRegex(CommunityContextError, "do not match"):
            validate_community_context(limits)

        content = self.bundle()
        content["files"][0]["content"] = None
        content["bundle_digest"] = canonical_digest(
            {key: value for key, value in content.items() if key != "bundle_digest"}
        )
        with self.assertRaisesRegex(CommunityContextError, "UTF-8 text"):
            validate_community_context(content)

        identifier = self.bundle()
        identifier["contribution"]["id"] = None
        identifier["bundle_digest"] = canonical_digest(
            {key: value for key, value in identifier.items() if key != "bundle_digest"}
        )
        with self.assertRaisesRegex(CommunityContextError, "contribution id"):
            validate_community_context(identifier)

    def test_metadata_excludes_instruction_content_and_render_orders_provenance(self):
        bundle = self.bundle()
        metadata = community_context_metadata(bundle)
        rendered = render_community_context(bundle)

        self.assertNotIn("files", metadata)
        self.assertNotIn("plan only", json.dumps(metadata))
        self.assertLess(rendered.index("Source digest:"), rendered.index("--- README.md ---"))
        self.assertIn("not-authorized", rendered)

    def test_mcp_catalog_returns_provenance_before_resource_content(self):
        bundle = self.bundle()
        contexts = {("community-demo", "0.1.0"): bundle}
        catalog = community_context_catalog(contexts)
        resource = community_context_resource(contexts, "community-demo", "0.1.0")

        self.assertEqual(catalog["count"], 1)
        self.assertNotIn("plan only", json.dumps(catalog))
        self.assertEqual(
            catalog["contexts"][0]["resource_uri"],
            "hpc-skill://community/community-demo/0.1.0",
        )
        self.assertLess(resource.index('"provenance"'), resource.index('"files"'))
        self.assertIn("plan only", resource)

    def test_public_schema_validates_bundle_and_embedded_evidence(self):
        try:
            from jsonschema import Draft202012Validator
            from referencing import Registry, Resource
        except ImportError:
            self.skipTest("jsonschema is not installed")
        schema_names = (
            "skill-security-report.schema.json",
            "community-skill-intake-report.schema.json",
            "community-skill-intake-decision.schema.json",
            "community-skill-intake-receipt.schema.json",
            "community-skill-review-packet.schema.json",
            "community-skill-independent-review.schema.json",
            "community-skill-adoption-report.schema.json",
            "community-skill-evidence-status.schema.json",
            "community-skill-context-bundle.schema.json",
        )
        schemas = {}
        registry = Registry()
        for name in schema_names:
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            schemas[schema["$id"]] = schema
            registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
        Draft202012Validator(schemas[SCHEMA_URL], registry=registry).validate(self.bundle())

    def test_installable_cli_build_check_and_show(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            package = root / "package"
            shutil.copytree(FIXTURE, package)
            receipt, packet = self.packet(package)
            reviews = [self.review(packet), self.review(packet, "safety")]
            paths = {
                "receipt": root / "receipt.json",
                "packet": root / "packet.json",
                "domain": root / "domain.json",
                "safety": root / "safety.json",
                "bundle": root / "context.json",
            }
            for name, payload in (
                ("receipt", receipt),
                ("packet", packet),
                ("domain", reviews[0]),
                ("safety", reviews[1]),
            ):
                paths[name].write_text(json.dumps(payload), encoding="utf-8")
            built = subprocess.run(
                [
                    "python3", "tools/community_context_bundle.py", "build",
                    "--source", str(package), "--receipt", str(paths["receipt"]),
                    "--packet", str(paths["packet"]), "--review", str(paths["domain"]),
                    "--review", str(paths["safety"]), "--output", str(paths["bundle"]),
                ],
                cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            checked = subprocess.run(
                [
                    "python3",
                    "tools/hpc_skill.py",
                    "community-context",
                    "check",
                    str(paths["bundle"]),
                    "--json",
                ],
                cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            shown = subprocess.run(
                [
                    "python3",
                    "tools/hpc_skill.py",
                    "community-context",
                    "show",
                    str(paths["bundle"]),
                ],
                cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )

            self.assertEqual(built.returncode, 0, built.stderr)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertNotIn("plan only", checked.stdout)
            self.assertEqual(shown.returncode, 0, shown.stderr)
            self.assertIn("plan only", shown.stdout)
            loaded = load_community_context(paths["bundle"])
            self.assertEqual(loaded["provenance"]["review"]["status"], "review-complete")
            self.assertLess(list(loaded).index("provenance"), list(loaded).index("files"))


@unittest.skipIf(
    create_connected_server_and_client_session is None,
    "optional MCP SDK is not installed",
)
class CommunityContextMcpProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_configured_bundle_is_discovered_before_resource_content(self):
        bundle = CommunityContextTests().bundle()
        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_path = Path(tmpdir) / "context.json"
            bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
            from hpc_skill_hub.mcp_server import create_server

            server = create_server([bundle_path])
            async with create_connected_server_and_client_session(
                server, raise_exceptions=True
            ) as session:
                result = await session.call_tool("list_community_contexts", {})
                catalog = result.structuredContent["result"]
                self.assertEqual(catalog["count"], 1)
                self.assertNotIn("files", catalog["contexts"][0])

                resource = await session.read_resource(
                    AnyUrl("hpc-skill://community/community-demo/0.1.0")
                )
                raw = resource.contents[0].text
                payload = json.loads(raw)
                self.assertLess(raw.index('"provenance"'), raw.index('"files"'))
                self.assertEqual(
                    payload["provenance"]["review"]["status"], "review-complete"
                )
                self.assertEqual(
                    payload["provenance"]["maturity"]["promotion"],
                    "not-authorized",
                )


if __name__ == "__main__":
    unittest.main()
