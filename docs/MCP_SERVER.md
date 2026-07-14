# Read-Only MCP Server

The optional `hpc-skill-mcp` command exposes validated registry metadata to MCP
clients over stdio. It does not run HPC commands or provide an operational
execution tool.

## Requirements

- Core `hpc-skill` CLI: Python 3.9 or later.
- Optional MCP server: Python 3.10 or later.
- MCP dependency: stable official SDK v1, constrained to `mcp>=1.27,<2`.

The upper bound is deliberate: MCP Python SDK v2 is not yet the stable line.

Install the optional integration:

```bash
python3 -m pip install 'hpc-skill-hub[mcp]'
```

During repository development:

```bash
python3 -m pip install '.[mcp]'
hpc-skill-mcp --root /path/to/hpc-skill-hub
```

An MCP client should launch `hpc-skill-mcp` as a local stdio command. P0 does
not expose an HTTP listener.

## Tool Surface

| Tool | Purpose |
| --- | --- |
| `search_skills` | Search validated metadata with category, scheduler, risk, maturity, status, tool, and collection filters. |
| `show_skill` | Return one skill's metadata, source paths, collection membership, and usage contract. |
| `list_collections` | List collections or inspect one collection. |
| `show_site_adapters` | List site adapters or inspect one adapter's public policy. |
| `resolve_site_policy` | Resolve one skill through one public adapter without filling unknown local values. |
| `registry_status` | Return registry health, review queue state, server capabilities, and the safety boundary. |

Search results are capped at 50 records. P0 returns packaged registry metadata,
not full README or example contents. Digest-verified full context is P1 work.

## Safety Boundary

Every tool is annotated as read-only, non-destructive, idempotent, and
closed-world. These annotations help clients describe the tools, but they are
not the enforcement boundary. The server itself registers only the six named
functions and contains no tool that:

- executes commands or example scripts;
- writes files or changes registry state;
- submits, cancels, or modifies scheduler jobs;
- transfers data, installs software, or launches containers;
- opens tunnels, listeners, or remote network sessions; or
- returns unreviewed community skill content.

Clients must still treat `maturity: seed` as a review signal, preserve site
placeholders, inspect referenced README and example sources, and obtain explicit
user intent before operational HPC actions.

## Validation

Run the dependency-independent checks:

```bash
PYTHONPATH=src python3 -m hpc_skill_hub.mcp_server --help
python3 -m unittest tests.test_mcp_server
```

With the optional MCP dependency installed, the same test module creates an
official in-memory client/server session, lists tools, verifies annotations,
and calls `search_skills` through the protocol.
