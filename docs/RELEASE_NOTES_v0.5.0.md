# v0.5.0 Release Notes

Status: release candidate; merge, tag, and tag-triggered attestation verification
are pending.

## Summary

`v0.5.0` is the trusted agent distribution release. It adds an optional
read-only MCP server, digest-verified packaged skill context, generated Codex
and Claude Code onboarding, installed-runtime diagnostics, versioned trust
policy packs, and an MCP-aware evidence campaign contract.

This candidate contains no paid Codex or Claude Code runs, no comparative
ranking, no measured MCP or skill-lift claim, and no maturity promotion. Those
outcomes remain behind explicit execution, redaction, independent review, and
publication gates.

## Registry Contents

- Skills: 97.
- Collections: 12.
- Site adapters: 2.
- Registry schema version: `0.2.0`.
- Skill maturity: all entries remain `seed`.

## Trusted Agent Distribution

- `hpc-skill-mcp` exposes six allowlisted read-only tools and one verified skill
  context resource over local stdio.
- The server has no command execution, file write, network, job submission,
  transfer, install, tunnel, container, or GPU allocation capability.
- All 97 skills and 344 registry-declared files are available through bounded,
  digest-verified context bundles in installed wheels.
- Codex and Claude Code examples are generated from one canonical packaged MCP
  client contract rather than maintained independently.
- `hpc-skill doctor` validates core-only installs and, with `--require-mcp`, the
  official SDK dependency plus the full in-memory protocol path.

## Trust Policy Packs

- The packaged 26-rule community baseline is versioned separately from scanner
  code and fails closed when missing or invalid.
- External policy packs may strengthen severities and add reviewed,
  finding-bound, expiring exceptions; they cannot disable or weaken baseline
  protections.
- Security and context artifacts record policy, target, rule-catalog, and
  exception provenance.
- Two guarded recursive-cleanup examples remain visible medium-review findings;
  there are no blocking findings.

## MCP Evidence Campaign

- The v0.5 plan defines 72 balanced runs across Codex and Claude Code, three
  public-safe tasks, baseline, docs-only, skill-enabled, and MCP-enabled
  conditions, and three trials.
- MCP workspaces contain only task fixtures and generated client configuration,
  not direct registry, skill, adapter, or documentation files.
- Preflight requires a passing installed MCP doctor, an exact `0.5.0` package,
  the canonical contract digest, exact model ids, authenticated clients, and
  explicit paid-run authorization.
- The dashboard reports MCP-versus-baseline and MCP-versus-skill gates as closed
  at 0/6 because no reviewed real-agent results are bundled.

## Release Status And Packaging

- `registry/release-status.json` is a generated, packaged summary of
  compatibility, context, MCP, benchmark, review, security, and release gates.
- The generated registry website now puts release readiness beside the catalog,
  supports collection-first discovery, responsive table and card views,
  sorting, shareable URL filters, and bounded mobile result expansion.
- MCP `registry_status` and `hpc-skill doctor` consume the same status artifact,
  so installed clients can distinguish repository readiness from pending
  external evidence.
- Package CI builds source and wheel distributions, tests metadata, exercises
  core and MCP-extra installs outside the checkout, and checks verified context
  plus release status.
- Tag-only GitHub provenance will attest the immutable manifest, wheel, and
  source distribution after `v0.5.0` is published.

## Safety And Evidence Boundary

- CI never launches paid agents or executes skill examples.
- Skill content is instructional context, not authorization for operational HPC
  actions.
- Seed maturity, medium security findings, missing independent review, and
  closed benchmark gates remain visible to consumers.
- Benchmark evidence never promotes a skill automatically.
