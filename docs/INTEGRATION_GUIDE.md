# Integration Guide

This guide is for downstream tools, portals, assistants, training platforms,
and workflow projects that want to consume HPC Skill Hub as a public registry.

Use this together with [Skill Specification](SKILL_SPEC.md),
[Site Adapters](SITE_ADAPTERS.md), and [Safety Model](SAFETY_MODEL.md).

## Integration Surfaces

The stable seed-stage surfaces are:

| Surface | Purpose |
| --- | --- |
| `registry/index.json` | Machine-readable registry summary for skills, collections, public site-adapter policy, categories, risk, maturity, and paths. |
| `docs/COMPATIBILITY.md` | Generated compatibility view for schedulers, collections, workflow engines, containers, domains, and tool signals. |
| `schemas/*.schema.json` | Validation contracts for skill manifests, collections, site adapters, registry index, registry health, and release manifests. |
| `skills/*/README.md` | Human-readable operating notes, assumptions, safety notes, and examples. |
| `skills/*/examples/` | Reviewable example scripts, batch files, configs, and checklists. |
| `collections/*.json` | Curated adoption paths for users, domains, or roles. |
| `site-adapters/*/site.json` | Public local policy mappings for clusters, training environments, or public cloud HPC. |
| `registry/skill-context.json` | Bounded, digest-verified README and declared artifact content for every validated skill. |
| `registry/release-status.json` | Package-versioned capability status and explicit repository, comparative-evidence, maturity, and release-provenance gates. |
| `integrations/mcp-client.json` | Canonical local stdio, capability, provider, and safety contract for MCP clients. |
| `security/policies/community-default.json` | Versioned fail-closed community-skill policy, packaged independently from scanner code. |
| `schemas/community-skill-intake-*.schema.json` | Portable P1 report, P2 maintainer decision, and deterministic receipt contracts for untrusted community intake. |
| `schemas/community-skill-{review-packet,independent-review,adoption-report,evidence-status}.schema.json` | Exact-bound P3 community review and public-safe adoption evidence contracts. |
| `integrations/codex.config.toml` and `integrations/claude-code.mcp.json` | Generated, reviewable provider configuration examples. |
| `python3 tools/hpc_skill.py ... --json` | Local CLI access for tools that prefer command output over direct file reads, including structured validation results. |
| `hpc-skill ... --json` | Installed package access to the packaged registry snapshot for read-only discovery and site-policy resolution. |
| `hpc-skill-mcp` | Optional read-only stdio server for metadata queries and verified full-context resources. |
| `hpc-skill doctor --json` | Installed-runtime diagnostics for package data, digests, client contract, dependencies, and MCP capabilities. |

Prefer `registry/index.json` for search and discovery. Load individual skill
manifests only when you need full metadata beyond the compact index.

Use `registry/release-status.json` or the MCP `registry_status` tool before
making release-wide claims. An open repository gate means the implementation
artifacts are coherent; closed comparative or maturity gates mean no measured
lift or promotion should be inferred.

## Consumption Contract

- Treat all paths in `registry/index.json` as repository-relative paths.
- Treat `schema_version` as the registry contract version, not an individual
  skill version.
- Treat skill `version` as local to one skill package.
- Treat `risk_level` and `maturity` as user-facing signals that should be shown
  before recommending commands.
- Treat `status: draft` and `maturity: seed` as reviewable starting points, not
  production guarantees.
- Do not execute example commands automatically. Present them for review, adapt
  placeholders, and require explicit user intent.
- Do not invent local cluster policy. Use site adapters when public local
  policy exists; otherwise ask the user to confirm scheduler, account,
  partition, storage, module, and container assumptions.
- Preserve links back to the source skill README and examples so users can audit
  the guidance.

## Recommended Flow

1. Clone or fetch the repository at a release tag or pinned commit.
2. Run `python3 tools/validate_skills.py` or `make check` before packaging the
   registry into another tool.
3. Parse `registry/index.json`.
4. Filter by `categories`, `tags`, `schedulers`, `tools`, `risk_level`,
   `maturity`, collection membership, or site adapter overrides.
5. Show the user the skill summary, risk, maturity, assumptions, source README,
   and example paths before suggesting commands.
6. Rebuild or refresh your cache only when the repository commit, release tag,
   or `schema_version` changes.

For stricter artifact validation, run:

```bash
python3 tools/validate_registry_artifacts.py
```

If your integration only needs read-only discovery, the Python package can be
used as a pinned registry snapshot. The installed `hpc-skill` command supports
JSON output for list, search, show, collection, adapter, resolve, and health commands
without requiring a checkout at runtime. Contribution, validation, scaffolding,
and release workflows should still use a full repository checkout.

For MCP clients, install `hpc-skill-hub[mcp]`, run
`hpc-skill doctor --require-mcp`, and follow the generated
[MCP Client Setup](MCP_CLIENT_SETUP.md). The doctor uses an in-memory transport;
it opens no listener and executes no skill content.

Apply only operator-reviewed external trust policies stored outside the scanned
community package. See [Trust Policy Packs](TRUST_POLICY_PACKS.md) for the
monotonic override, reviewed-exception, and provenance contract.

Before an integration exposes community-contributed content, run
`hpc-skill intake`, create an external exact-binding maintainer decision, and
verify the resulting receipt with `hpc-skill receipt verify`. Only an
`accepted` receipt may advance to the P4 context builder, which must reconstruct
and verify every file against `accepted_context.accepted_digest`. The receipt is
a drift-detection record, not a signature or domain review. See
[Community Intake Receipts](INTAKE_RECEIPTS.md).

Before P4 consumption, generate and verify the P3 packet with
`hpc-skill evidence packet|check`. Keep intake, domain, safety, adoption, and
maturity owners separate; require approved coverage for every declared domain;
and preserve the aggregate `maturity_promotion: not-authorized` result. P3
status is review routing evidence, not context-loading or execution authority.
See [Community Review And Adoption Evidence](COMMUNITY_EVIDENCE.md).

Minimal Python example:

```python
import json
from pathlib import Path

index = json.loads(Path("registry/index.json").read_text(encoding="utf-8"))
slurm_skills = [
    skill
    for skill in index["skills"]
    if "slurm" in skill.get("schedulers", [])
    and skill["risk_level"] in {"low", "medium"}
]
for skill in slurm_skills:
    print(skill["id"], skill["risk_level"], skill["maturity"], skill["readme"])
```

## Assistant And Agent Integrations

When using skills inside an assistant, IDE, workflow helper, or agent:

- Cite the skill id, version, maturity, and source path used for the
  recommendation.
- Show risk and site assumptions before proposing a command.
- Prefer dry-run, read-only, static, or short smoke-test examples first.
- Ask for explicit confirmation before submitting jobs, moving data, installing
  software, launching containers, or consuming GPU allocations.
- Keep private cluster details outside prompts, logs, examples, and public
  issues.
- Prefer a site adapter over hard-coding local policy into the integration.
- Treat `resolve ... --adapter ... --json` as a read-only policy packet, never
  as authorization to submit a job or replace placeholders.

## Portal And Search Integrations

Search portals can safely index:

- Skill id, name, summary, description, categories, tags, scheduler, tools,
  risk level, maturity, README path, and example titles.
- Collection id, audience, status, summary, and skill ids.
- Site adapter id, status, institution type, scheduler, public partitions, and
  skill override ids.

Avoid indexing private deployment notes or local user data. Site adapters in
this repository should be public-safe, but downstream deployments may layer
private policy outside the public registry.

## Site Adapter Use

Use site adapters to adapt portable skills to public local policy:

- Map generic scheduler guidance to public partitions or queues.
- Link public module, container, storage, and data transfer documentation.
- Add public warnings for skills that need local constraints.
- Keep private hostnames, allocation names, usernames, internal project ids,
  and unpublished security procedures out of the adapter.

Use the structured resolver instead of joining adapter and skill JSON with
ad-hoc string rules:

```bash
hpc-skill resolve slurm-submit-job \
  --adapter example-campus-cluster \
  --json
```

The response follows
[`site-adapter-resolution.schema.json`](../schemas/site-adapter-resolution.schema.json).
Stop on `incompatible`, surface every review reason, and keep
`compatible-unmapped` generic unless the user confirms additional public local
policy.

If no site adapter exists, tools should keep recommendations generic and ask
users to fill in local values.

## Compatibility And Change Management

During the seed stage, integrations should pin to a release tag or commit. The
project uses RFCs for changes that affect schemas, generated registry output,
validation behavior, risk policy, maturity policy, or downstream tooling.

Open an integration request issue when:

- A field needed by downstream tooling is missing.
- A schema change would make integration safer or easier.
- A site adapter needs additional public metadata.
- A CLI `--json` command would avoid ad hoc parsing.
- A new collection would help a specific user journey.

Use [RFC Process](RFC_PROCESS.md) for project-level compatibility changes.

## Validation Checklist

Before publishing a downstream integration:

- [ ] Pin the repository tag or commit used by the integration.
- [ ] Confirm `registry/index.json` is current.
- [ ] Confirm schemas validate in your build or release process.
- [ ] Confirm risk and maturity are visible in the user experience.
- [ ] Confirm commands are not executed without explicit user intent.
- [ ] Confirm site-specific values come from public site adapters or user input.
- [ ] Confirm your integration has a path for reporting bugs or missing skills.
