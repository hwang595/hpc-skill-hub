# v0.5 Completion Matrix

Status: released. P0 through P3 merged through PR #44, release preparation
merged in PR #45, and the website upgrade merged in PR #46. `v0.5.0` was
published from commit `22be6ae` on 2026-07-14. Validate, Package, Pages, and the
tag-triggered attestation jobs passed. Paid-run, comparative, and independent
maturity-review outcomes are not claimed here.

v0.5 is the trusted agent distribution release. It packages reviewed registry
content behind a closed read-only MCP surface and publishes machine-readable
status that distinguishes repository capability from external evidence.

## P0 Read-Only MCP MVP

| Gate | Status | Evidence |
| --- | --- | --- |
| Closed tool surface | Complete | Six allowlisted discovery and policy tools expose no job submission, execution, transfer, install, tunnel, container, or write action. |
| Protocol contract | Complete | Official SDK in-memory tests verify stdio registration, read-only annotations, exact arguments, and closed-world hints. |
| Optional packaging | Complete | Core remains Python 3.9 compatible; `hpc-skill-hub[mcp]` requires Python 3.10+ and MCP SDK stable v1. |

## P1 Verified Context Bundles

| Gate | Status | Evidence |
| --- | --- | --- |
| Registry coverage | Complete | `registry/skill-context.json` contains all 97 skills and 344 declared files. |
| Integrity and bounds | Complete | File, skill, bundle, source-index, and security-report digests are checked with explicit file, skill, and bundle size limits. |
| Installed access | Complete | The bundle is packaged and exposed through `hpc-skill://skills/{skill_id}` without requiring a checkout. |

## P2 Onboarding And Diagnostics

| Gate | Status | Evidence |
| --- | --- | --- |
| Provider examples | Complete | Codex TOML and Claude Code JSON are generated from one canonical packaged contract. |
| Runtime doctor | Complete | Core and strict-MCP modes validate package metadata, registry data, context, policy, contract, dependency, and protocol behavior. |
| Wheel isolation | Complete in CI contract | Package workflow installs and exercises core and MCP-extra wheels outside the source checkout. |

## P3 Trust Policy Packs

| Gate | Status | Evidence |
| --- | --- | --- |
| Versioned baseline | Complete | The 26-rule community policy is packaged separately from scanner code and fails closed when invalid. |
| Monotonic customization | Complete | External policy may strengthen severity and add digest-bound expiring exceptions, but cannot disable or weaken baseline rules. |
| MCP privacy boundary | Complete | Exact tool/argument allowlists and tests exclude private site policy, raw argument reflection, and MCP logging. |

## P4 Evidence And Review

| Gate | Status | Required evidence |
| --- | --- | --- |
| MCP campaign contract | Complete locally | `evidence-v0.5.json` defines 72 runs: two agents, three tasks, four isolated conditions, and three trials. |
| MCP isolation and provenance | Complete locally | MCP workspaces receive fixtures plus client configuration, while campaign locks bind contract digest and exact installed package version. |
| Real execution | Deferred | No paid run is authorized by CI or this release. Exact models, authenticated CLIs, quota approval, and explicit per-run authorization are required. |
| Comparative publication | Gate closed | There are zero scored results; MCP-versus-baseline and MCP-versus-skill gates are both 0/6. No ranking or lift claim is emitted. |
| Maturity promotion | Gate closed | Five v0.4 candidates still require independent domain review, one requires safety review, and all require a maintainer decision. |

## P5 Release

| Gate | Status | Evidence |
| --- | --- | --- |
| Unified generated status | Complete | `registry/release-status.json` summarizes compatibility, context, MCP, benchmark, review, security, and verified release provenance while preserving closed external evidence gates. |
| Registry web explorer | Complete | The generated Pages site surfaces release status, collection entry points, responsive table/card views, sorting, shareable URL filters, and bounded mobile card expansion without adding a runtime framework. |
| Version consistency | Complete | Package metadata, module version, citation metadata, README badge, notes, tag, and immutable manifest all target `0.5.0`. |
| Distribution smoke tests | Complete | Package workflow built sdist/wheel, ran `twine check`, and tested both core and MCP-extra installs outside the checkout. |
| Immutable manifest | Complete | `registry/releases/v0.5.0.json` records the released tree and is now checked only as an immutable published snapshot. |
| Release provenance | Verified | `registry/provenance/v0.5.0.json` binds commit `22be6ae`, successful Package run `29375502297`, and verified SHA-256 digests for the manifest, wheel, and sdist. |

## Release Decision Boundary

The release may ship the trusted distribution and validated campaign control
plane with comparative and maturity gates closed. It must not claim that MCP or
skills improve agent performance until real outputs complete redaction,
independent blinded review, reconciliation, and the publication contract.
