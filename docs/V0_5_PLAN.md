# v0.5 Development Plan

Status: released. P0 read-only MCP MVP merged through PR #41, P1 verified context bundles
merged through PR #42, P2 onboarding/diagnostics merged through PR #43, and P3
Trust Policy Packs merged through PR #44, release preparation merged in PR #45,
and the website upgrade merged in PR #46. `v0.5.0` was published from commit
`22be6ae` on 2026-07-14 and its tag-triggered artifact attestations were
verified. Authenticated paid runs and independent review remain intentionally
pending external evidence.

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

Implementation status: complete for the repository capability. The generated
bundle covers every current registry skill and declared artifact, is included
in package data, and is exercised through the official MCP SDK's in-memory
resource client.

- Generate bounded context bundles containing validated skill README and
  example content, source paths, versions, and SHA-256 digests.
- Include security-scan provenance and reject stale, oversized, missing, or
  untracked content during generation.
- Package the bundles so installed clients can inspect full workflows without
  a source checkout.
- Expose bundles as read-only MCP resources while keeping unreviewed community
  content outside the packaged trust boundary.

## P2 Codex And Claude Code Onboarding

Implementation status: complete for the repository capability. Provider
examples are generated from a packaged canonical contract, and the doctor can
validate both a core-only install and the full official-SDK protocol path.

- Generate provider-specific stdio configuration examples from one canonical
  contract.
- Add a doctor command for Python version, optional dependency, registry
  schema, package data, context digests, and tool-capability checks.
- Test installed-wheel operation outside the repository for both metadata and
  full context retrieval.

## P3 Trust Policy Packs

Implementation status: complete for the repository capability. The packaged
baseline is separate from scanner code, external packs can only strengthen it,
reviewed exceptions bind exact findings and expire, and MCP capability/privacy
boundaries are enforced in code and tests.

- Version community-skill security policy separately from scanner code.
- Add explicit rule enablement, severity overrides, reviewed exceptions, and
  provenance receipts without allowing a package to weaken its own policy.
- Keep sensitive arguments and private site policy out of MCP logs and public
  evidence.
- Treat MCP annotations as client hints; enforce the actual allowlist in server
  code and tests.

## P4 Evidence And Review

Implementation status: complete for the repository capability. The v0.5 plan
defines 72 balanced runs, MCP contexts remain isolated from direct skill files,
preflight binds a passing installed MCP runtime, campaign locks preserve the
contract digest and package version, and the report exposes closed MCP
comparison gates until reviewed evidence is complete.

- Add an `mcp-enabled` benchmark condition beside baseline, docs-only, and
  skill-enabled conditions.
- Run real Codex and Claude Code campaigns only after exact models,
  authenticated clients, explicit paid-run authorization, and independent
  reviewers are available.
- Keep incomplete runs and closed comparison gates visible.
- Continue the five public v0.4 maturity reviews as an independent track; no
  benchmark result automatically promotes a skill.

## P5 Release

Implementation status: released and verified. The generated status,
operational registry explorer, versioned manifest, core/MCP wheel smoke tests,
tag workflow, and artifact attestation verification are complete.

- Publish compatibility, context-bundle, MCP, benchmark, review, and security
  status in generated artifacts.
- Publish a responsive registry explorer with release-gate visibility,
  collection-first discovery, shareable filters, and table/card views.
- Build and smoke-test core and MCP extras from the wheel.
- Publish an immutable v0.5.0 manifest and verify manifest, wheel, and source
  distribution attestations from the release tag.

## Completion Boundary

P0-P5 establish repository and release capability. P4 outcome claims still
require external evidence and explicit authorization. A passing CI gate and a
verified release prove protocol, policy, build, and provenance behavior; they do
not prove agent lift, domain correctness, adoption, or reviewed maturity.
