# v0.4 Completion Matrix

Status: released as `v0.4.0` on 2026-07-13 from commit `cee22c6`. P0 and P1
control planes merged through PRs #27 and #28, P2A merged through PR #29, and
release preparation merged through PR #38. Validate, Package, Pages, and
tag-triggered attestations passed. Real agent execution and maturity promotion
remain explicitly deferred rather than claimed complete.

v0.4 is the evidence and reviewed-registry release. It must distinguish
repository capability from externally collected evidence: deterministic plans,
schemas, and dashboards can be completed in CI, while comparative claims
require real runs, public-safe artifacts, and independent review.

## P0 Evidence Foundation

| Gate | Status | Evidence |
| --- | --- | --- |
| Versioned evidence campaign | Complete locally | `evidence-v0.4.json` defines three public-safe tasks, three conditions, three paired trials, and Codex plus Claude Code variants. |
| Bounded execution contract | Complete locally | Every run requires explicit paid-run acknowledgement and an exact model id. The plan has a USD 0.75 allowance and USD 40.50 campaign ceiling; preflight identifies Claude's provider CLI hard limit and Codex's required external quota monitoring. |
| Resumable campaign accounting | Complete locally | Campaign status records completed states, recorded cost, remaining budget, and the next planned run. |
| Evidence publication gate | Complete locally | Comparative output requires two scored agent/model variants, no pending reviews, exactly two independent blinded reviewers per scored run, digest-verified public artifacts, and at least three paired trials for every agent/model variant. |
| Static evidence dashboard | Complete locally | The generated dashboard shows coverage, condition outcomes, paired lift, public run provenance, and explicit blockers. It suppresses comparative ranking while the gate is closed. |
| Local and CI validation | Complete | Generated plans, report, dashboard, schemas, and the full `make check` gate pass without launching an agent. PRs #27 and #28 passed the required Validate and Package checks. |

The P0 implementation is merged and has passed remote CI. It does not include
paid execution and does not establish measured skill lift.

## P1 Real Evidence Campaign

| Gate | Status | Required evidence |
| --- | --- | --- |
| Clean-run preflight and campaign lock | Control plane merged; execution deferred | Campaign preparation locks one clean commit, plan and task digests, exact model ids, CLI versions, budget enforcement modes, and explicit quota acknowledgement. No paid execution was authorized for this release. |
| Balanced execution waves | Control plane merged; execution deferred | A seeded schedule groups the 54-run matrix into nine randomized six-run task/trial waves. It remains available for a later explicitly approved campaign. |
| Blinded independent review | Deferred with real runs | No synthetic review substitutes for missing agent outputs. Future runs must be redacted, independently double scored, and reconciled. |
| Public evidence import audit | Control plane merged; evidence pending | Staging audit is available, but no reviewed real-run bundle is imported in v0.4.0. |
| Comparative publication | Gate closed by release decision | The public dashboard reports missing evidence and emits no comparative ranking or measured-lift claim. |

## P2 Reviewed Registry Pilot

| Gate | Status | Required evidence |
| --- | --- | --- |
| Candidate selection | Complete and merged | Five low-risk, strong-quality candidates are tracked through release-scoped evidence bundles, generated status, CLI inspection, and machine-readable promotion blockers. PR #29 passed required CI. |
| Skill depth improvements | Pilot static gate complete | The five pilot candidates score 98-100, have no detected quality gaps, and carry static plus agent benchmark references. External review may still identify changes. |
| Domain review and adoption | Public review routed; approval pending | Review is pinned to commit `55b90ad8dbb8fcf9e1e0656a95889217a02c6ab5` in issues #30, #33, #35, #36, and #37. No adoption report or reviewer approval is fabricated. |
| Maturity promotion | Deferred | All skills remain `seed`. Promotion requires the linked independent domain approval, required safety approval for shared permissions, and a recorded maintainer decision. |

## P3 Release Readiness

| Gate | Status | Required evidence |
| --- | --- | --- |
| Public dashboard decision | Complete | Publish the dashboard with the comparison gate closed and explicit missing-evidence blockers. Do not publish a leaderboard row. |
| Registry and release artifacts | Complete | Version metadata, release notes, deterministic registry artifacts, package data, and `registry/releases/v0.4.0.json` were published and validated. |
| v0.4.0 release | Released and verified | PR #38 merged, annotated tag `v0.4.0` points to `cee22c6`, the GitHub Release and manifest are public, Pages is live, and the manifest, wheel, and source distribution attestations verify against the tag. |

## Evidence Boundary

CI may validate plans, context isolation, budget logic, aggregation, review
contracts, artifact digests, and generated output. CI must never launch Codex,
Claude Code, or another paid agent. A passing P0 gate means the campaign is
ready to run; it does not mean the campaign has run.

The v0.4.0 release decision is to ship the validated evidence and review
control planes while keeping both outcome gates closed. This preserves a
reproducible path to later evidence without turning missing external work into
a release claim.
