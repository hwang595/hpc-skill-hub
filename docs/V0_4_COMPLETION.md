# v0.4 Completion Matrix

Status: P0 evidence foundation complete locally; pull-request CI pending.

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
| Local and CI validation | Local complete; remote pending | Generated plans, report, dashboard, schemas, 121 tests, and the full `make check` gate pass without launching an agent. Pull-request CI remains required. |

The P0 implementation is ready for pull-request review. P0 is release-complete
only after remote CI passes. It does not include paid execution and does not
establish measured skill lift.

## P1 Real Evidence Campaign

| Gate | Status | Required evidence |
| --- | --- | --- |
| Clean-run preflight | Pending external setup | Install and authenticate both CLIs, pin exact model ids, approve quota, and use one clean repository commit. |
| Repeated paired runs | Pending approval | Execute the 54-run matrix one run at a time within the campaign budget. Keep failures and stopped runs visible. |
| Blinded independent review | Pending real runs | Redact artifacts, collect exactly two independent reviews per run, and reconcile rubric differences of `0.25` or more. |
| Public evidence import | Pending review | Import only digest-bound, public-safe result records and artifacts, then regenerate the report and dashboard. |
| Comparative publication | Gate closed | Publish comparisons only after the machine-readable publication gate is open. |

## P2 Reviewed Registry Pilot

| Gate | Status | Required evidence |
| --- | --- | --- |
| Candidate selection | Planned | Select a bounded set of high-value skills using quality gaps, benchmark coverage, adoption evidence, and reviewer availability. |
| Skill depth improvements | Planned | Close documented prerequisites, validation, failure handling, cost, cleanup, site-boundary, and example gaps. |
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
