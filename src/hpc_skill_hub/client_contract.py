"""Load and validate the canonical MCP client onboarding contract."""

from __future__ import annotations

import importlib.resources as resources
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


PACKAGE_NAME = "hpc_skill_hub"
CONTRACT_FILENAME = "mcp-client.json"
CONTRACT_SCHEMA_VERSION = "0.1.0"
CONTRACT_SCHEMA_POINTER = "../schemas/mcp-client-contract.schema.json"
EXPECTED_SERVER_ID = "hpc-skill-hub"
EXPECTED_COMMAND = "hpc-skill-mcp"


class ClientContractError(ValueError):
    """Raised when the MCP client contract is missing or inconsistent."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ClientContractError(message)


def _repository_contract_path() -> Optional[Path]:
    candidates = []
    env_root = os.environ.get("HPC_SKILL_HUB_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser())
    candidates.append(Path.cwd())
    candidates.extend(Path(__file__).resolve().parents)
    for candidate in candidates:
        path = candidate / "integrations" / CONTRACT_FILENAME
        if path.is_file() and (candidate / "registry" / "index.json").is_file():
            return path
    return None


def contract_bytes() -> Tuple[bytes, str]:
    repository_path = _repository_contract_path()
    if repository_path:
        return repository_path.read_bytes(), "repository"
    try:
        path = resources.files(PACKAGE_NAME).joinpath(
            "data", "integrations", CONTRACT_FILENAME
        )
        return path.read_bytes(), "packaged"
    except FileNotFoundError as exc:
        raise ClientContractError(
            "packaged MCP client contract is missing: "
            f"data/integrations/{CONTRACT_FILENAME}"
        ) from exc


def validate_client_contract(payload: Dict[str, Any]) -> None:
    _require(isinstance(payload, dict), "MCP client contract must be an object")
    _require(
        set(payload) == {"$schema", "schema_version", "server", "providers"},
        "MCP client contract top-level keys mismatch",
    )
    _require(
        payload.get("$schema") == CONTRACT_SCHEMA_POINTER,
        "MCP client contract $schema mismatch",
    )
    _require(
        payload.get("schema_version") == CONTRACT_SCHEMA_VERSION,
        "MCP client contract schema_version mismatch",
    )

    server = payload.get("server")
    _require(isinstance(server, dict), "MCP client contract server must be an object")
    _require(
        set(server) == {
            "id",
            "name",
            "transport",
            "command",
            "args",
            "env",
            "package_extra",
            "registry_schema_version",
            "python",
            "read_only",
            "tools",
            "tool_arguments",
            "resources",
            "safety_boundary",
        },
        "MCP server contract keys mismatch",
    )
    _require(server.get("id") == EXPECTED_SERVER_ID, "MCP server id mismatch")
    _require(server.get("name") == "HPC Skill Hub", "MCP server name mismatch")
    _require(server.get("transport") == "stdio", "MCP transport must be stdio")
    _require(server.get("command") == EXPECTED_COMMAND, "MCP command mismatch")
    _require(server.get("args") == [], "MCP default args must be empty")
    _require(server.get("env") == {}, "MCP default environment must be empty")
    _require(
        server.get("package_extra") == "hpc-skill-hub[mcp]",
        "MCP package extra mismatch",
    )
    _require(
        server.get("registry_schema_version") == "0.2.0",
        "MCP registry schema contract mismatch",
    )
    _require(
        server.get("python") == {"core_minimum": "3.9", "mcp_minimum": "3.10"},
        "MCP Python compatibility contract mismatch",
    )
    _require(server.get("read_only") is True, "MCP contract must be read-only")

    tools = server.get("tools")
    _require(
        isinstance(tools, list)
        and bool(tools)
        and all(isinstance(item, str) and item for item in tools),
        "MCP tool list is invalid",
    )
    _require(len(tools) == len(set(tools)), "MCP tool names must be unique")
    tool_arguments = server.get("tool_arguments")
    _require(
        isinstance(tool_arguments, dict) and set(tool_arguments) == set(tools),
        "MCP tool argument allowlist must exactly cover the tools",
    )
    for tool_name, arguments in tool_arguments.items():
        _require(
            isinstance(arguments, list)
            and len(arguments) == len(set(arguments))
            and all(isinstance(item, str) and item for item in arguments),
            f"{tool_name}: MCP tool argument allowlist is invalid",
        )

    resource_entries = server.get("resources")
    _require(
        isinstance(resource_entries, list) and bool(resource_entries),
        "MCP resource list is invalid",
    )
    resource_names = []
    for entry in resource_entries:
        _require(isinstance(entry, dict), "MCP resource entry must be an object")
        _require(
            set(entry) == {"name", "uri_template", "mime_type"},
            "MCP resource entry keys mismatch",
        )
        _require(
            isinstance(entry["name"], str) and bool(entry["name"]),
            "MCP resource name is invalid",
        )
        _require(
            isinstance(entry["uri_template"], str)
            and "{skill_id}" in entry["uri_template"],
            "MCP resource URI template is invalid",
        )
        _require(
            entry["mime_type"] == "application/json",
            "MCP resource MIME type mismatch",
        )
        resource_names.append(entry["name"])
    _require(
        len(resource_names) == len(set(resource_names)),
        "MCP resource names must be unique",
    )

    expected_safety = {
        "executes_commands": False,
        "writes_files": False,
        "uses_network": False,
        "submits_jobs": False,
        "returns_unreviewed_community_content": False,
        "accepts_private_site_policy": False,
        "uses_mcp_logging": False,
        "logs_sensitive_arguments": False,
    }
    _require(
        server.get("safety_boundary") == expected_safety,
        "MCP safety boundary mismatch",
    )

    providers = payload.get("providers")
    _require(isinstance(providers, dict), "MCP providers must be an object")
    _require(
        set(providers) == {"codex", "claude-code"},
        "MCP providers must be codex and claude-code",
    )
    expected_provider_values = {
        "codex": {
            "config_format": "toml",
            "user_config_path": "~/.codex/config.toml",
            "project_config_path": ".codex/config.toml",
            "example_path": "integrations/codex.config.toml",
            "add_command": "codex mcp add hpc-skill-hub -- hpc-skill-mcp",
            "verify_commands": [
                "codex mcp get hpc-skill-hub",
                "codex mcp list",
            ],
            "documentation_url": "https://developers.openai.com/codex/mcp/",
        },
        "claude-code": {
            "config_format": "json",
            "user_config_path": "~/.claude.json",
            "project_config_path": ".mcp.json",
            "example_path": "integrations/claude-code.mcp.json",
            "add_command": (
                "claude mcp add --transport stdio --scope project "
                "hpc-skill-hub -- hpc-skill-mcp"
            ),
            "verify_commands": [
                "claude mcp get hpc-skill-hub",
                "claude mcp list",
            ],
            "documentation_url": "https://code.claude.com/docs/en/mcp",
        },
    }
    for provider_id, provider in providers.items():
        _require(isinstance(provider, dict), f"{provider_id}: provider must be an object")
        required = {
            "config_format",
            "user_config_path",
            "project_config_path",
            "example_path",
            "add_command",
            "verify_commands",
            "documentation_url",
        }
        _require(set(provider) == required, f"{provider_id}: provider keys mismatch")
        _require(
            provider == expected_provider_values[provider_id],
            f"{provider_id}: provider compatibility contract mismatch",
        )
        for key in (
            "user_config_path",
            "project_config_path",
            "example_path",
            "add_command",
            "documentation_url",
        ):
            _require(
                isinstance(provider[key], str) and bool(provider[key]),
                f"{provider_id}: {key} is invalid",
            )
        _require(
            isinstance(provider["verify_commands"], list)
            and bool(provider["verify_commands"])
            and all(
                isinstance(command, str) and bool(command)
                for command in provider["verify_commands"]
            ),
            f"{provider_id}: verify_commands is invalid",
        )


def load_client_contract() -> Dict[str, Any]:
    raw, _ = contract_bytes()
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClientContractError(
            f"MCP client contract is not valid UTF-8 JSON: {exc}"
        ) from exc
    validate_client_contract(payload)
    return payload


def contract_source_mode() -> str:
    _, source = contract_bytes()
    return source
