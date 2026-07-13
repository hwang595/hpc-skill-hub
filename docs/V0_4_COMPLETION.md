# v0.4 Completion Matrix

Status: P0 evidence foundation and P1 campaign control plane merged through
PRs #27 and #28 with required CI checks passing. P2A evidence-backed maturity
review workflow is complete locally with pull-request CI pending. Real evidence
execution and skill promotion remain pending external setup, quota approval,
and independent review.

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
| Clean-run preflight and campaign lock | Control plane merged; external setup pending | Campaign preparation locks one clean commit, plan and task digests, exact model ids, CLI versions, budget enforcement modes, and explicit quota acknowledgement. Real preparation still requires authenticated CLIs. |
| Balanced execution waves | Control plane merged; execution pending | A seeded schedule groups the 54-run matrix into nine randomized six-run task/trial waves. Status emits only the earliest incomplete wave and stops on provenance or budget blockers. |
| Blinded independent review | Pending real runs | Redact artifacts, collect exactly two independent reviews per run, and reconcile rubric differences of `0.25` or more. |
| Public evidence import audit | Control plane merged; evidence pending | Staging audit checks campaign identity, model and CLI locks, clean commit provenance, double-blinded review, public artifact digests, private-file boundaries, safety, and acknowledged security review. |
| Comparative publication | Gate closed | Publish comparisons only after the machine-readable publication gate is open. |

## P2 Reviewed Registry Pilot

| Gate | Status | Required evidence |
| --- | --- | --- |
| Candidate selection | P2A complete locally; remote pending | Five low-risk, strong-quality candidates are tracked through release-scoped evidence bundles, generated status, CLI inspection, and machine-readable promotion blockers. The full local gate passes. |
| Skill depth improvements | Pilot static gate complete | The five pilot candidates score 98-100, have no detected quality gaps, and carry static plus agent benchmark references. External review may still identify changes. |
| Domain review and adoption | Planned | Record public domain review and real adoption evidence without exposing private site policy. |
| Maturity promotion | Planned | Promote only skills that satisfy the existing lifecycle contract; benchmark lift alone is insufficient. |

## P3 Release Readiness

| Gate | Status | Required evidence |
| --- | --- | --- |
| Public dashboard decision | Planned | Either publish gated comparative evidence or state clearly that evidence remains incomplete. |
| Registry and release artifacts | Planned | Regenerate all deterministic artifacts from the release commit and validate immutable snapshots. |
| v0.4.0 release | Planned | Merge reviewed work, tag the clean release commit, publish notes, and verify GitHub attestations. |

## Evidence Boundary

CI may validate plans, context isolation, budget logic, aggregation, review
contracts, artifact digests, and generated output. CI must never launch Codex,
Claude Code, or another paid agent. A passing P0 gate means the campaign is
ready to run; it does not mean the campaign has run.
