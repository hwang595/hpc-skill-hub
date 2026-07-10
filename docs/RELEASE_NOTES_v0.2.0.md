# v0.2.0 Release Notes

Status: released on 2026-07-10.

## Summary

`v0.2.0` is the reviewed-skill pilot release. It turns the seed registry from a
large catalog into a reviewable queue: maintainers can identify first review
candidates, route them by domain focus, create maturity-review issues, and
promote skills only after public-safe evidence exists.

The release does not automatically mark skills as `reviewed`. It adds the
process and generated artifacts needed to make those promotions auditable.

It also adds the v0.2 Evidence Pilot infrastructure for measuring whether
Codex and Claude Code improve when repository guidance and registry-backed
skills are available. The release does not claim measured lift until reviewed
agent runs are imported.

## Release Scope

This is an infrastructure and contract release. All 97 skills remain `draft`
and `seed`; no site adapter is promoted to `reviewed`; and the agent benchmark
report contains no scored external-agent runs. Those are explicit evidence
gaps, not implicit maturity claims. Adoption reports, domain review, real site
adapter review, paid agent execution, redaction, and blinded scoring continue
through public follow-up work.

## Registry Contents

- Skills: 97.
- Collections: 12.
- Site adapters: 2, including 1 example adapter and 1 public-doc-backed draft
  adapter.
- Skill maturity target: select seed skills for first `reviewed` review.
- Risk labels: low and medium only.

## Added

- Productization sprint improvements for registry consumers and contributors:
  structured CLI validation JSON, `check` and `new` shortcuts, richer skill
  scaffolds, filtered CLI discovery, and multi-filter static catalog search.
- A generated reviewed-skill pilot packet at
  `docs/REVIEW_PACKET_v0.2.0.md`.
- A `tools/review_packet.py` command that builds or checks the pilot packet
  from `registry/index.json` and `tools/review_candidates.py` scoring.
- Suggested maturity-review issue titles, labels, review focus areas, evidence
  summaries, and promotion gates for the first review queue.
- A `v0.2.0` release manifest target at `registry/releases/v0.2.0.json` so the
  already-published `v0.1.0` snapshot can remain immutable.
- CI coverage for the reviewed-skill pilot packet and the current release
  manifest.
- A 15-case static and fixture benchmark suite for representative skill files,
  public-safe evidence, shell syntax, and site-gated checks.
- Generated Codex and Claude Code repository adapters and router skills.
- Six versioned agent benchmark tasks covering routing, triage, safety,
  repository editing, and public site-adapter behavior.
- Provenance-aware task, plan, and result schemas with repeated trials,
  failure visibility, evaluator metadata, metrics, and artifact hashes.
- A dry-run execution harness that isolates benchmark conditions and expands a
  balanced 54-run Codex/Claude calibration matrix. Real runs require one run
  id, an exact model id, and explicit paid-run acknowledgement.
- Macro-averaged benchmark reporting with failure rate, confidence intervals,
  cost, time, tokens, and paired skill lift.

## Maintainer Workflow

Use the packet to start review work:

```bash
python3 tools/review_packet.py --check
python3 tools/review_packet.py --json --limit 12
python3 tools/review_candidates.py --collection data-movement --limit 8
python3 tools/agent_benchmark_harness.py --check
python3 tools/run_agent_benchmarks.py --check
```

For each selected skill:

1. Open a `maturity-review` issue.
2. Assign a domain reviewer based on the packet review focus.
3. Add `safety-review` when the packet suggests it or when admin, facility,
   quota, accounting, or shared software behavior is in scope.
4. Confirm examples, assumptions, references, and risk labels.
5. Promote from `seed` to `reviewed` only in a pull request that links the
   review issue and passes `make check`.

## Known Limitations

- The packet uses repository metadata and static evidence; it is not a domain
  review decision.
- `field-tested` and `maintained` maturity still require adoption reports or
  explicit maintainer ownership beyond this release.
- Site adapters remain draft until a real site or training environment reviews
  public policy mappings.
- The calibration matrix is validated, but no public scored agent runs are
  bundled yet. Exact models, paid execution, redaction, and blinded review are
  explicit maintainer operations outside CI.

## Release Verification

The release candidate was verified with:

- `make check` passing locally.
- `Validate`, `Package`, and `Publish Pages` passing on the release commit.
- `docs/REVIEW_PACKET_v0.2.0.md` is current.
- `docs/AGENT_BENCHMARK_PLAN.md` and `docs/AGENT_BENCHMARK_REPORT.md` are
  current.
- `registry/releases/v0.2.0.json` is current and published with the GitHub
  release.
- The maturity-review queue is open and no maturity promotion is claimed
  without public review evidence.
