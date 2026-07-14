import unittest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.mcp_server import (
    TOOL_NAMES,
    create_server,
    list_collections,
    registry_status,
    resolve_site_policy,
    search_skills,
    show_site_adapters,
    show_skill,
)


class McpRegistryToolTests(unittest.TestCase):
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

    def test_show_skill_includes_agent_safety_contract(self):
        payload = show_skill("slurm-oom-memory-triage")

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skill"]["maturity"], "seed")
        self.assertEqual(payload["content_scope"], "metadata-only")
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
        self.assertTrue(payload["server"]["read_only"])
        self.assertFalse(payload["safety_boundary"]["uses_network"])
        self.assertFalse(payload["safety_boundary"]["writes_files"])
        self.assertEqual(payload["registry"]["skill_count"], 97)


try:
    from mcp.shared.memory import create_connected_server_and_client_session
except ImportError:
    create_connected_server_and_client_session = None


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

            result = await session.call_tool(
                "search_skills", {"query": "slurm oom", "limit": 3}
            )
            self.assertFalse(result.isError)
            payload = result.structuredContent["result"]
            self.assertTrue(payload["ok"])
            self.assertGreater(payload["returned"], 0)


if __name__ == "__main__":
    unittest.main()
