import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.mcp_server import (
    RESOURCE_NAMES,
    TOOL_NAMES,
    TOOL_ARGUMENT_ALLOWLIST,
    create_server,
    list_collections,
    main,
    read_skill_context,
    registry_status,
    resolve_site_policy,
    search_skills,
    show_site_adapters,
    show_skill,
    skill_context,
)


class McpRegistryToolTests(unittest.TestCase):
    def test_invalid_repository_root_is_rejected_before_server_start(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(main(["--root", tmpdir]), 2)

    def test_search_skills_filters_and_bounds_results(self):
        payload = search_skills(
            "slurm memory", scheduler="slurm", risk="low", limit=2
        )

        self.assertTrue(payload["ok"])
        self.assertLessEqual(payload["returned"], 2)
        self.assertGreater(payload["total"], 0)
        for skill in payload["skills"]:
            self.assertIn("slurm", skill["schedulers"])
            self.assertEqual(skill["risk_level"], "low")

    def test_search_skills_rejects_invalid_limit(self):
        payload = search_skills("slurm", limit=0)

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["code"], "invalid-limit")

    def test_tool_results_do_not_reflect_raw_arguments(self):
        marker = "private-token-shaped-marker"

        search = json.dumps(search_skills(marker), sort_keys=True)
        unknown = json.dumps(show_skill(marker), sort_keys=True)

        self.assertNotIn(marker, search)
        self.assertNotIn(marker, unknown)

    def test_show_skill_includes_agent_safety_contract(self):
        payload = show_skill("slurm-oom-memory-triage")

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skill"]["maturity"], "seed")
        self.assertEqual(payload["content_scope"], "verified-readme-and-artifacts")
        self.assertEqual(
            payload["context_resource"]["uri"],
            "hpc-skill://skills/slurm-oom-memory-triage",
        )
        self.assertGreater(payload["context_resource"]["file_count"], 0)
        self.assertTrue(
            payload["usage_contract"][
                "require_explicit_intent_for_operational_actions"
            ]
        )

    def test_unknown_items_return_machine_readable_errors(self):
        self.assertEqual(
            show_skill("not-a-skill")["error"]["code"], "unknown-skill"
        )
        self.assertEqual(
            list_collections("not-a-collection")["error"]["code"],
            "unknown-collection",
        )
        self.assertEqual(
            show_site_adapters("not-an-adapter")["error"]["code"],
            "unknown-site-adapter",
        )
        self.assertEqual(
            skill_context("not-a-skill")["error"]["code"], "unknown-skill"
        )

    def test_skill_context_returns_verified_full_content_and_safety_contract(self):
        payload = json.loads(read_skill_context("slurm-submit-job"))

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["bundle_schema_version"], "0.2.0")
        self.assertTrue(
            any(
                item["role"] == "readme" and "Slurm" in item["content"]
                for item in payload["skill_context"]["files"]
            )
        )
        self.assertFalse(
            payload["usage_contract"]["execute_examples_automatically"]
        )

    def test_resolve_site_policy_preserves_review_boundary(self):
        payload = resolve_site_policy(
            "slurm-submit-job", "example-campus-cluster"
        )

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["resolution"]["resolution_status"], "mapped")
        self.assertTrue(payload["resolution"]["review"]["required"])

    def test_registry_status_declares_closed_read_only_surface(self):
        payload = registry_status()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["server"]["tools"], list(TOOL_NAMES))
        self.assertEqual(payload["server"]["resources"], list(RESOURCE_NAMES))
        self.assertTrue(payload["server"]["read_only"])
        self.assertFalse(payload["safety_boundary"]["uses_network"])
        self.assertFalse(payload["safety_boundary"]["writes_files"])
        self.assertFalse(payload["safety_boundary"]["accepts_private_site_policy"])
        self.assertFalse(payload["safety_boundary"]["uses_mcp_logging"])
        self.assertFalse(payload["safety_boundary"]["logs_sensitive_arguments"])
        self.assertEqual(payload["registry"]["skill_count"], 97)
        self.assertEqual(payload["context"]["file_count"], 344)


try:
    from mcp.shared.memory import create_connected_server_and_client_session
    from pydantic import AnyUrl
except ImportError:
    create_connected_server_and_client_session = None
    AnyUrl = None


@unittest.skipIf(
    create_connected_server_and_client_session is None,
    "optional MCP SDK is not installed",
)
class McpProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_in_memory_protocol_lists_and_calls_read_only_tools(self):
        server = create_server()
        async with create_connected_server_and_client_session(
            server, raise_exceptions=True
        ) as session:
            listed = await session.list_tools()
            tools = {tool.name: tool for tool in listed.tools}

            self.assertEqual(set(tools), set(TOOL_NAMES))
            for tool in tools.values():
                self.assertTrue(tool.annotations.readOnlyHint)
                self.assertFalse(tool.annotations.destructiveHint)
                self.assertTrue(tool.annotations.idempotentHint)
                self.assertFalse(tool.annotations.openWorldHint)
                self.assertEqual(
                    set(tool.inputSchema.get("properties", {})),
                    set(TOOL_ARGUMENT_ALLOWLIST[tool.name]),
                )

            sensitive_fragments = {
                "account",
                "allocation",
                "credential",
                "hostname",
                "password",
                "private_policy",
                "secret",
                "token",
                "username",
            }
            exposed_arguments = {
                argument
                for arguments in TOOL_ARGUMENT_ALLOWLIST.values()
                for argument in arguments
            }
            self.assertFalse(
                any(
                    fragment in argument
                    for argument in exposed_arguments
                    for fragment in sensitive_fragments
                )
            )

            result = await session.call_tool(
                "search_skills", {"query": "slurm oom", "limit": 3}
            )
            self.assertFalse(result.isError)
            payload = result.structuredContent["result"]
            self.assertTrue(payload["ok"])
            self.assertGreater(payload["returned"], 0)

            templates = await session.list_resource_templates()
            by_name = {item.name: item for item in templates.resourceTemplates}
            self.assertEqual(set(by_name), set(RESOURCE_NAMES))
            self.assertEqual(
                str(by_name["skill_context"].uriTemplate),
                "hpc-skill://skills/{skill_id}",
            )
            self.assertEqual(by_name["skill_context"].mimeType, "application/json")

            resource = await session.read_resource(
                AnyUrl("hpc-skill://skills/slurm-submit-job")
            )
            resource_payload = json.loads(resource.contents[0].text)
            self.assertTrue(resource_payload["ok"])
            self.assertEqual(
                resource_payload["skill_context"]["id"], "slurm-submit-job"
            )
            self.assertTrue(resource_payload["skill_context"]["files"])


if __name__ == "__main__":
    unittest.main()
