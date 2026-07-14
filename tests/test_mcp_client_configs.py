import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.client_contract import (
    load_client_contract,
    validate_client_contract,
)
from hpc_skill_hub.mcp_server import RESOURCE_NAMES, TOOL_NAMES


try:
    import tomllib
except ImportError:
    tomllib = None

try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None


class McpClientConfigTests(unittest.TestCase):
    def test_canonical_contract_matches_runtime_allowlists(self):
        contract = load_client_contract()
        validate_client_contract(contract)

        server = contract["server"]
        self.assertEqual(tuple(server["tools"]), TOOL_NAMES)
        self.assertEqual(
            tuple(item["name"] for item in server["resources"]),
            RESOURCE_NAMES,
        )
        self.assertEqual(server["transport"], "stdio")
        self.assertTrue(server["read_only"])
        self.assertTrue(all(value is False for value in server["safety_boundary"].values()))

    def test_generated_examples_are_current(self):
        result = subprocess.run(
            ["python3", "tools/build_mcp_client_configs.py", "--check"],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("configuration examples are current", result.stdout)

    @unittest.skipIf(Draft202012Validator is None, "jsonschema is not installed")
    def test_canonical_contract_matches_json_schema(self):
        schema = json.loads(
            (ROOT / "schemas" / "mcp-client-contract.schema.json").read_text(
                encoding="utf-8"
            )
        )
        contract = json.loads(
            (ROOT / "integrations" / "mcp-client.json").read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(contract)

    @unittest.skipIf(tomllib is None, "TOML parser is not in Python 3.9 stdlib")
    def test_codex_example_is_valid_and_bounded(self):
        path = ROOT / "integrations" / "codex.config.toml"
        with path.open("rb") as handle:
            payload = tomllib.load(handle)
        server = payload["mcp_servers"]["hpc-skill-hub"]

        self.assertEqual(server["command"], "hpc-skill-mcp")
        self.assertEqual(server["args"], [])
        self.assertTrue(server["enabled"])
        self.assertFalse(server["required"])
        self.assertEqual(set(server), {
            "command",
            "args",
            "enabled",
            "required",
            "startup_timeout_sec",
            "tool_timeout_sec",
        })

    def test_claude_code_example_is_valid_and_bounded(self):
        path = ROOT / "integrations" / "claude-code.mcp.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        server = payload["mcpServers"]["hpc-skill-hub"]

        self.assertEqual(
            server,
            {
                "args": [],
                "command": "hpc-skill-mcp",
                "env": {},
                "type": "stdio",
            },
        )

    def test_examples_do_not_auto_enable_project_configuration(self):
        self.assertFalse((ROOT / ".codex" / "config.toml").exists())
        self.assertFalse((ROOT / ".mcp.json").exists())

    def test_packaged_contract_matches_canonical_source(self):
        source = ROOT / "integrations" / "mcp-client.json"
        packaged = (
            ROOT
            / "src"
            / "hpc_skill_hub"
            / "data"
            / "integrations"
            / "mcp-client.json"
        )
        self.assertEqual(source.read_bytes(), packaged.read_bytes())


if __name__ == "__main__":
    unittest.main()
