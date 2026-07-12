# v0.3 Completion Matrix

Status: code-ready for pull request; not release-ready.

This matrix separates repository implementation from evidence that must be
collected from a clean merged commit. A dry-run plan, synthetic test, or signed
workflow definition is not evidence that a real agent comparison or release
attestation has already happened.

## Code Gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Community skill security scanner | Complete | Static package scanning, text/JSON/SARIF output, stable findings, risk cross-checks, CLI and CI gates. |
| Cross-agent smoke harness | Complete | Six-run Codex/Claude plan, condition isolation, exact-model preflight, resumable status, and explicit paid-run acknowledgement. |
| Blinded review and scoring | Complete | Digest-bound packets, two independent reviews, disagreement reconciliation, tamper checks, and external public staging. |
| Site-adapter integration contract | Complete | Registry index `0.2.0` ships complete public policy; `hpc-skill resolve` reports mapped, compatible-unmapped, or incompatible. |
| Agent adapter support | Complete | Generated Codex and Claude router guidance consumes the resolver and treats incompatible policy as a stop signal. |
| Release provenance workflow | Complete | Tag-only `actions/attest@v4` covers the versioned release manifest, source distribution, and wheel. |
| Local repository gate | Complete when current branch passes | `make check` validates generated artifacts, safety, security, CLI behavior, package data, and tests without launching paid agents. |

## Release Evidence Gates

| Gate | Status | Required next evidence |
| --- | --- | --- |
| Six real smoke runs | Pending after merge | Run Codex and Claude Code from one clean commit with exact model ids and explicit quota approval. |
| Independent blinded scores | Pending real runs | Prepare the packet, collect exactly two reviews per case, and reconcile criterion differences of `0.25` or more. |
| First public comparison | Pending reviewed scores | Import only the staged public-safe result and redacted artifact bundle, then regenerate the benchmark report. |
| Repeated-trial calibration | Gated by smoke result | Expand to the 54-run matrix only after the six-run pipeline is valid and the budget is approved. |
| Tag attestation | Pending v0.3 tag | Build from the release tag and verify every attached artifact with `gh attestation verify`. |
| External adoption and site review | Community evidence | Keep public adoption, domain review, and real-site adapter validation visible without treating them as synthetic CI results. |

## Required Order

1. Merge the v0.3 code-foundation pull request after CI and review.
2. Pin exact Codex and Claude Code model ids and verify both CLIs.
3. Run the six-run campaign from the clean merged commit with explicit paid-run
   approval.
4. Complete redaction, blinded scoring, reconciliation, and staged import.
5. Publish the smoke comparison with failures and pending runs visible.
6. Decide whether evidence and budget justify the repeated-trial matrix.
7. Prepare the v0.3 release manifest and notes, create the tag, and verify the
   generated attestations.

The project should not claim that skills improve agent performance until the
real reviewed comparison exists.
