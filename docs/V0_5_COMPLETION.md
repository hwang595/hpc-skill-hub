# v0.5 Completion Matrix

Status: release candidate. P0 through P3 are merged through PR #44. P4's
repository-side MCP evidence capability and P5's local release contracts are
implemented on the candidate branch. Merge, tag, GitHub workflow, attestation,
paid-run, and independent-review outcomes are not claimed here.

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
| Real execution | Deferred | No paid run is authorized by CI or this release candidate. Exact models, authenticated CLIs, quota approval, and explicit per-run authorization are required. |
| Comparative publication | Gate closed | There are zero scored results; MCP-versus-baseline and MCP-versus-skill gates are both 0/6. No ranking or lift claim is emitted. |
| Maturity promotion | Gate closed | Five v0.4 candidates still require independent domain review, one requires safety review, and all require a maintainer decision. |

## P5 Release Candidate

| Gate | Status | Evidence |
| --- | --- | --- |
| Unified generated status | Complete locally | `registry/release-status.json` summarizes compatibility, context, MCP, benchmark, review, and security artifacts and preserves closed external gates. |
| Registry web explorer | Complete locally | The generated Pages site surfaces release readiness, collection entry points, responsive table/card views, sorting, shareable URL filters, and bounded mobile card expansion without adding a runtime framework. |
| Version consistency | Complete locally | Package metadata, module version, citation metadata, README badge, notes, and candidate manifest target `0.5.0`. |
| Distribution smoke tests | CI contract complete; candidate run required | Package workflow builds sdist/wheel, runs `twine check`, and tests both core and MCP-extra installs outside the checkout. |
| Immutable manifest | Complete locally | `registry/releases/v0.5.0.json` checksums the candidate tree and CI requires it to pass `--check`. |
| Release provenance | Pending tag | Manifest, wheel, and sdist attestations can only be created and verified after the reviewed commit is tagged `v0.5.0`. |

## Release Decision Boundary

The release may ship the trusted distribution and validated campaign control
plane with comparative and maturity gates closed. It must not claim that MCP or
skills improve agent performance until real outputs complete redaction,
independent blinded review, reconciliation, and the publication contract.
