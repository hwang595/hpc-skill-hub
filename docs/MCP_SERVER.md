# Read-Only MCP Server

The optional `hpc-skill-mcp` command exposes validated registry metadata and
verified skill context to MCP clients over stdio. It does not run HPC commands
or provide an operational execution tool.

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

An MCP client should launch `hpc-skill-mcp` as a local stdio command. The
server does not expose an HTTP listener.

Generated Codex and Claude Code examples, official client commands, and trust
notes are in [MCP Client Setup](MCP_CLIENT_SETUP.md). All provider output is
derived from `integrations/mcp-client.json`; the examples do not automatically
enable a project server.

Diagnose a core-only install without requiring the optional SDK:

```bash
hpc-skill doctor --json
```

Require the full dependency and in-memory protocol/resource probe:

```bash
hpc-skill doctor --require-mcp
```

## Tool Surface

| Tool | Purpose |
| --- | --- |
| `search_skills` | Search validated metadata with category, scheduler, risk, maturity, status, tool, and collection filters. |
| `show_skill` | Return one skill's metadata, source paths, collection membership, and usage contract. |
| `list_collections` | List collections or inspect one collection. |
| `show_site_adapters` | List site adapters or inspect one adapter's public policy. |
| `resolve_site_policy` | Resolve one skill through one public adapter without filling unknown local values. |
| `registry_status` | Return registry health, release capability gates, review queue state, server capabilities, and the safety boundary. |

Search results are capped at 50 records. `show_skill` returns validated metadata
plus the URI, digest, file count, and byte count for the corresponding verified
context resource.

## Resource Surface

The resource template is:

```text
hpc-skill://skills/{skill_id}
```

For example, after calling `show_skill("slurm-submit-job")`, a client can read
`hpc-skill://skills/slurm-submit-job`. The JSON resource contains:

- skill id, version, status, maturity, risk, and source path;
- exact UTF-8 content for README and every manifest-declared artifact;
- source byte counts and SHA-256 digests;
- a per-skill digest and the enclosing bundle digest;
- manifest provenance and static security-scan provenance; and
- an explicit usage contract that content is instruction, not authorization.

`registry/skill-context.json` is generated deterministically. Current limits
are 64 KiB per file, 64 files and 256 KiB per skill, and 2 MiB of source content
for the complete registry. Generation fails for stale, missing, undeclared,
non-UTF-8, oversized, symlinked, path-escaping, or security-blocked content.
Installed wheels carry an identical package snapshot.

At runtime the loader recomputes every file, skill, and bundle digest, then
checks that the bundle is bound to the exact packaged `registry/index.json`.
SHA-256 detects corruption and stale data; it is not a signature and does not
replace release attestations or human review. Server startup fails closed when
the selected repository or packaged bundle does not pass these checks.

## Safety Boundary

Every tool is annotated as read-only, non-destructive, idempotent, and
closed-world. These annotations help clients describe the tools, but they are
not the enforcement boundary. The server itself registers only the six named
functions and one bounded resource template. It contains no tool that:

- executes commands or example scripts;
- writes files or changes registry state;
- submits, cancels, or modifies scheduler jobs;
- transfers data, installs software, or launches containers;
- opens tunnels, listeners, or remote network sessions; or
- returns unreviewed community skill content.

Only content already admitted to the generated public registry can enter the
resource bundle. Arbitrary community paths cannot be passed to the MCP server.
Security `review` findings and the versioned trust-policy receipt remain
visible; `block` prevents generation.

The server defines an exact argument allowlist for each tool and checks it
against callable signatures before registration. The doctor and official SDK
tests compare the protocol `inputSchema` properties with the same allowlist.
The server does not accept private site policy, enable MCP logging, or echo raw
search and unknown-id arguments into responses. Tool annotations remain client
hints; this server-side allowlist is the capability boundary.

Clients must still treat `maturity: seed` as a review signal, preserve site
placeholders, inspect referenced README and example sources, and obtain explicit
user intent before operational HPC actions.

## Validation

Run the dependency-independent checks:

```bash
PYTHONPATH=src python3 -m hpc_skill_hub.mcp_server --help
python3 -m unittest tests.test_mcp_server
python3 -m unittest tests.test_skill_context
python3 tools/build_skill_context.py --check
python3 tools/build_mcp_client_configs.py --check
hpc-skill doctor --require-mcp
```

With the optional MCP dependency installed, the same test module creates an
official in-memory client/server session, lists tools, verifies annotations,
calls `search_skills`, lists the resource template, and reads a verified skill
context through the protocol.
