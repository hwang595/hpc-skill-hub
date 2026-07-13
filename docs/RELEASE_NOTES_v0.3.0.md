# v0.3.0 Release Notes

Status: released on 2026-07-13.

## Summary

`v0.3.0` is the security, agent-compatibility, and skill-quality release. It
adds a reviewable boundary for community-contributed skills, completes the
Codex and Claude Code adapter contracts, introduces blinded benchmark review
tooling, and deepens the nine skills used by the cross-agent evidence pilot.

This is an infrastructure and contract release. It does not include scored
external-agent runs, does not publish a leaderboard row, and does not claim
that adopting a skill improves an agent. Real Codex/Claude execution remains a
separate paid evidence campaign requiring exact model ids, clean commits,
public-safe artifacts, independent reviews, and explicit quota approval.

## Registry Contents

- Skills: 97.
- Collections: 12.
- Site adapters: 2, including one example adapter and one public-doc-backed
  draft adapter.
- Registry schema version: `0.2.0`.
- Skill maturity: all entries remain `seed` and `draft` unless future public
  review evidence supports promotion.

## Community Skill Security

- Deterministic text, JSON, and SARIF scanning for prompt injection, concealed
  behavior, dangerous commands, persistence, ambient credential access,
  package-boundary violations, and understated manifest risk.
- CLI and CI adoption gates that treat community skill content as untrusted,
  block high-severity findings, and require review of medium findings.
- Stable findings suitable for contributor feedback and downstream registry
  integrations without executing scanned content.

## Agent And Site Compatibility

- Generated Codex and Claude Code router skills backed by the same registry
  discovery, safety, and site-resolution contract.
- Read-only site-adapter resolution with mapped, compatible-unmapped, and
  incompatible outcomes.
- Complete public policy in registry index contract `0.2.0`, while preserving
  placeholders for private account, partition, module, path, and endpoint
  values.

## Skill Quality And Evidence Depth

- A deterministic ten-dimension quality baseline covering scope,
  prerequisites, workflow, inputs/outputs, validation, failure handling,
  safety, resource impact, cleanup, and site boundaries.
- Versioned JSON Schema, machine-readable registry report, generated Markdown
  report, launch-readiness integration, and non-threshold CI freshness checks.
- All nine tier-1 agent-evidence skills now cover every quality dimension and
  include offline review paths or bounded, opt-in execution examples.
- Expanded synthetic fixtures, static benchmark cases, and process-level
  regression tests for Slurm, GPU, MPI, permissions, and storage workflows.

## Storage Benchmark Safety

- The IOR/MDTest example defaults to a true no-write plan-only path.
- Real execution requires both `RUN_BENCHMARK=1` and
  `CONFIRM_STORAGE_POLICY=1` after local path and policy review.
- Task counts, iterations, file counts, depth, transfer size, and block size
  are capped for a smoke-test envelope.
- Existing output directories are rejected, summaries require an ownership
  marker and complete evidence files, and cleanup remains marker guarded.

## Blinded Review And Benchmarking

- A six-run Codex/Claude smoke plan covering baseline, documentation-only, and
  skill-enabled conditions without enabling networked task contracts.
- Exact-model and executable preflight, isolated context materialization,
  resumable status, and an explicit `--allow-paid-run` gate.
- Digest-bound blinded packets, exactly two reviews per case, disagreement
  reconciliation, redaction and tamper checks, and public-safe staged import.
- No real smoke result is bundled in this release. The generated agent
  benchmark report remains explicit about missing, pending, and failed runs.

## Provenance

- Published release manifests remain immutable historical snapshots.
- The tag-only `Package` workflow builds and tests source and wheel
  distributions, then uses `actions/attest@v4` for the `v0.3.0` manifest and
  Python artifacts.
- Release consumers can verify downloaded artifacts with
  `gh attestation verify --repo hwang595/hpc-skill-hub`.

## Safety And Review Notes

- No example job, data transfer, package installation, container launch, GPU
  allocation, or paid agent run is performed by repository validation.
- The full skill security scan has no blocking finding. Two recursive cleanup
  examples remain medium-review items and retain explicit ownership-marker and
  confirmation guards.
- Site-specific values remain placeholders; private hostnames, allocation
  names, project ids, credentials, and unpublished policy are not release
  content.

## Release Verification

The release candidate is verified with:

- `make check` passing locally.
- Generated registry, health, compatibility, skill-quality, package, static
  benchmark, and agent benchmark reports current.
- All 97 skills, 12 collections, and 2 site adapters validating successfully.
- `Validate`, `Package`, and `Publish Pages` required to pass on the release
  commit.
- `registry/releases/v0.3.0.json` published with the GitHub release.
- Tag-triggered manifest, source distribution, and wheel attestations verified
  after the `v0.3.0` workflow completes.
