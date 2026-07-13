# v0.3 Completion Matrix

Status: v0.3.0 infrastructure scope released; comparative evidence track open.

This matrix separates the released repository contracts from evidence that
must still be collected from clean commits. A dry-run plan, synthetic test, or
signed workflow definition is not evidence that a real agent comparison has
already happened.

## Code Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Community skill security scanner | Complete | Static package scanning, text/JSON/SARIF output, stable findings, risk cross-checks, CLI and CI gates. |
| Cross-agent smoke harness | Complete | Six-run Codex/Claude plan, condition isolation, exact-model preflight, resumable status, and explicit paid-run acknowledgement. |
| Blinded review and scoring | Complete | Digest-bound packets, two independent reviews, disagreement reconciliation, tamper checks, and external public staging. |
| Site-adapter integration contract | Complete | Registry index `0.2.0` ships complete public policy; `hpc-skill resolve` reports mapped, compatible-unmapped, or incompatible. |
| Agent adapter support | Complete | Generated Codex and Claude router guidance consumes the resolver and treats incompatible policy as a stop signal. |
| Release provenance workflow | Complete | Tag-only `actions/attest@v4` covers the versioned release manifest, source distribution, and wheel. |
| Skill-quality baseline | Complete | Ten visible workflow dimensions, bounded evidence bonuses, generated JSON/Markdown reports, and CI freshness checks without maturity promotion. |
| Tier-1 skill depth | Complete | All nine agent-evidence priority skills have explicit prerequisites, validation, failure handling, resource impact, cleanup, site boundaries, and offline reviewers. |
| Local repository gate | Complete | `make check` validates generated artifacts, safety, security, CLI behavior, package data, and tests without launching paid agents. |

## Post-Release Evidence Gates

| Gate | Status | Required next evidence |
| --- | --- | --- |
| Six real smoke runs | Deferred, no runs imported | Install and authenticate both CLIs, then run Codex and Claude Code from one clean commit with exact model ids and explicit quota approval. |
| Independent blinded scores | Pending real runs | Prepare the packet, collect exactly two reviews per case, and reconcile criterion differences of `0.25` or more. |
| First public comparison | Pending reviewed scores | Import only the staged public-safe result and redacted artifact bundle, then regenerate the benchmark report. |
| Repeated-trial calibration | Gated by smoke result | Expand to the 54-run matrix only after the six-run pipeline is valid and the budget is approved. |
| Tag attestation | Required for release | Build from the `v0.3.0` tag and verify the manifest and Python distributions with `gh attestation verify`. |
| External adoption and site review | Community evidence | Keep public adoption, domain review, and real-site adapter validation visible without treating them as synthetic CI results. |

The `v0.3.0` release contains no scored external-agent row and makes no claim
that skills improve agent performance. Missing Claude Code availability during
release preparation was treated as a stop signal for paid cross-agent runs,
not as permission to substitute synthetic evidence.

## Release Order

1. Merge the v0.3 code foundations, skill-quality work, and release candidate
   after CI and review.
2. Build the deterministic `v0.3.0` manifest and release notes from the clean
   release commit.
3. Create the tag and GitHub release, then verify tag-triggered package
   attestations.

## Evidence Order

1. Pin exact Codex and Claude Code model ids and verify both CLIs.
2. Run the six-run campaign from a clean commit with explicit paid-run
   approval.
3. Complete redaction, blinded scoring, reconciliation, and staged import.
4. Publish the smoke comparison with failures and pending runs visible.
5. Decide whether evidence and budget justify the repeated-trial matrix.

The project should not claim that skills improve agent performance until the
real reviewed comparison exists.
