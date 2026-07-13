# v0.4.0 Release Notes

Status: release-ready on 2026-07-13; tag and attestations pending.

## Summary

`v0.4.0` is the evidence-campaign and maturity-review readiness release. It
adds a bounded, resumable cross-agent campaign control plane, machine-checkable
publication gates, release-scoped skill review bundles, installed review CLI
commands, and public dashboards that expose missing evidence instead of
manufacturing conclusions.

This release contains no paid Codex or Claude Code runs, no comparative
ranking, no measured skill-lift claim, and no skill maturity promotion. The
campaign and review workflows are ready for external use, while their outcome
gates remain closed until real public-safe evidence and independent review
exist.

## Registry Contents

- Skills: 97.
- Collections: 12.
- Site adapters: 2, including one example adapter and one public-doc-backed
  draft adapter.
- Registry schema version: `0.2.0`.
- Skill maturity: all entries remain `seed`; no benchmark result promotes a
  skill automatically.

## Evidence Campaign Foundation

- A versioned 54-run plan covers three public-safe tasks, baseline,
  documentation-only, and skill-enabled conditions, three paired trials, and
  Codex plus Claude Code variants.
- Every real run requires an exact model id, explicit paid-run acknowledgement,
  an isolated context packet, and a USD 0.75 per-run allowance within a USD
  40.50 campaign authorization ceiling.
- Clean-commit locks, task and plan digests, CLI versions, seeded balanced
  execution waves, resumable status, and budget stop conditions make the
  campaign auditable without running agents in CI.
- Finalized staging audits enforce campaign identity, provenance, redaction,
  artifact digests, private-file boundaries, safety review, and independent
  double scoring before import.

## Comparative Publication Decision

- The evidence dashboard remains published with the comparison gate closed.
- No reviewed real-agent results are bundled, so no leaderboard row, paired
  lift, or agent ordering is emitted.
- Future comparisons require two scored agent/model variants, exactly two
  independent blinded reviewers per scored run, no pending reviews, verified
  public artifacts, and at least three paired trials per variant.
- Paid campaign execution is deferred until exact models, authenticated CLIs,
  external quota monitoring, and explicit budget approval are available.

## Reviewed Registry Pilot

- Release-scoped review bundles track five low-risk, strong-quality skills with
  scores of 98-100, no detected documentation gaps, and static plus agent-task
  benchmark coverage.
- Review is pinned to commit
  `55b90ad8dbb8fcf9e1e0656a95889217a02c6ab5` and routed publicly:
  [#30](https://github.com/hwang595/hpc-skill-hub/issues/30),
  [#33](https://github.com/hwang595/hpc-skill-hub/issues/33),
  [#35](https://github.com/hwang595/hpc-skill-hub/issues/35),
  [#36](https://github.com/hwang595/hpc-skill-hub/issues/36), and
  [#37](https://github.com/hwang595/hpc-skill-hub/issues/37).
- `shared-project-permissions-triage` requires both domain and safety review
  because its declared categories include admin scope.
- All five remain `awaiting-review`. Independent approval and a maintainer
  decision are required before any promotion pull request.

## CLI And Public Artifacts

- `hpc-skill review candidates` lists the bounded review queue.
- `hpc-skill review status <skill-id>` exposes static readiness and blockers.
- `hpc-skill review check <bundle>` validates source evidence without treating
  pending external review as malformed data.
- `hpc-skill review packet` emits the generated release-scoped packet.
- Installed packages include `registry/review-status.json`; Pages publishes the
  evidence dashboard, skill review dashboard, packets, and source bundles.

## Safety And Review Notes

- CI never launches paid agents, submits HPC jobs, transfers data, installs
  software, launches containers, opens tunnels, or consumes GPU allocations.
- The skill security scan has no blocking finding. Two recursive-cleanup
  examples remain medium-review items with ownership markers and explicit
  confirmation guards.
- Public review records exclude private hostnames, usernames, allocation names,
  internal project ids, tokens, private paths, and unpublished policy.
- Benchmark coverage supports review routing but is not domain approval,
  adoption evidence, or a maturity decision.

## Release Verification

The release candidate is verified with:

- `make check` passing locally.
- Generated campaign, benchmark, review, registry, package, site, and release
  artifacts current.
- All 97 skills, 12 collections, and 2 site adapters validating successfully.
- `Validate`, `Package`, and `Publish Pages` required to pass on the release
  commit.
- `registry/releases/v0.4.0.json` attached to the GitHub release.
- Tag-triggered manifest, source distribution, and wheel attestations verified
  after the `v0.4.0` workflow completes.
