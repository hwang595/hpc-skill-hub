# v0.5 Development Plan

Status: P0 read-only MCP MVP complete locally on 2026-07-13; pull-request CI
pending. Public delivery is tracked in issue
[#40](https://github.com/hwang595/hpc-skill-hub/issues/40).

v0.5 focuses on trusted agent distribution. The release should make the
validated registry easier for Codex, Claude Code, and other MCP clients to
consume without weakening the existing safety, provenance, or maturity
boundaries.

## P0 Read-Only MCP MVP

- Ship an optional `hpc-skill-mcp` stdio server using the stable v1 line of the
  official MCP Python SDK.
- Expose only registry discovery, skill inspection, collection listing, public
  site-adapter inspection, site-policy resolution, and registry status.
- Mark every tool read-only, non-destructive, idempotent, and closed-world.
- Keep job submission, file writes, transfers, installs, tunnels, containers,
  network services, and GPU allocation actions outside the server.
- Preserve Python 3.9 support for the core CLI; require Python 3.10 or later
  only for the optional MCP integration.
- Validate the protocol with the official SDK's in-memory client/session test.

## P1 Verified Context Bundles

- Generate bounded context bundles containing validated skill README and
  example content, source paths, versions, and SHA-256 digests.
- Include security-scan provenance and reject stale, oversized, missing, or
  untracked content during generation.
- Package the bundles so installed clients can inspect full workflows without
  a source checkout.
- Expose bundles as read-only MCP resources while keeping unreviewed community
  content outside the packaged trust boundary.

## P2 Codex And Claude Code Onboarding

- Generate provider-specific stdio configuration examples from one canonical
  contract.
- Add a doctor command for Python version, optional dependency, registry
  schema, package data, context digests, and tool-capability checks.
- Test installed-wheel operation outside the repository for both metadata and
  full context retrieval.

## P3 Trust Policy Packs

- Version community-skill security policy separately from scanner code.
- Add explicit rule enablement, severity overrides, reviewed exceptions, and
  provenance receipts without allowing a package to weaken its own policy.
- Keep sensitive arguments and private site policy out of MCP logs and public
  evidence.
- Treat MCP annotations as client hints; enforce the actual allowlist in server
  code and tests.

## P4 Evidence And Review

- Add an `mcp-enabled` benchmark condition beside baseline, docs-only, and
  skill-enabled conditions.
- Run real Codex and Claude Code campaigns only after exact models,
  authenticated clients, explicit paid-run authorization, and independent
  reviewers are available.
- Keep incomplete runs and closed comparison gates visible.
- Continue the five public v0.4 maturity reviews as an independent track; no
  benchmark result automatically promotes a skill.

## P5 Release

- Publish compatibility, context-bundle, MCP, benchmark, review, and security
  status in generated artifacts.
- Build and smoke-test core and MCP extras from the wheel.
- Publish an immutable v0.5.0 manifest and verify manifest, wheel, and source
  distribution attestations from the release tag.

## Completion Boundary

P0-P3 are repository capabilities. P4 requires external evidence and explicit
authorization. A passing CI gate proves protocol and policy behavior; it does
not prove agent lift, domain correctness, adoption, or reviewed maturity.
