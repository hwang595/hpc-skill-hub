# v0.6 Development Plan

Status: P0 release hygiene merged in PR #48, P1 quarantined intake merged in
PR #50, P2 intake receipts merged in PR #51, and P3 review and adoption
evidence merged in PR #52. P4 trusted agent consumption is complete on the
current branch. P5 remains planned and must preserve the external evidence
boundaries below.

v0.6 focuses on verified community intake and evidence. The release should let
maintainers inspect, quarantine, review, and selectively expose contributed
skills without loading untrusted instructions before policy checks complete.

## P0 Release Hygiene

Implementation status: merged in PR #48. The v0.6 milestone is #7,
the public delivery tracker is issue #49, the completed v0.5 tracker and
milestone are closed, and duplicate or superseded PRs are closed with links to
their replacement.

- Record v0.5 release, workflow, artifact digest, and attestation verification
  facts in a schema-validated provenance receipt.
- Correct release status, website, roadmap, notes, and completion contracts.
- Stop comparing the published v0.5 manifest with the changing development
  tree; continue structural immutable-snapshot validation.
- Refresh GitHub Actions to current Node 24-compatible majors.
- Create the v0.6 milestone and public tracking issue after local gates pass.

## P1 Quarantined Community Intake

Implementation status: merged in PR #50. The installable
`hpc-skill intake` command and standalone repository wrapper share one
standard-library implementation and a schema-validated report contract.

- Add a no-execution intake command that inventories an untrusted directory or
  archive before any `SKILL.md`, README, example, or instruction is loaded.
- Enforce package, path traversal, symlink, archive nesting, file count, file
  size, bundle size, encoding, and binary-content limits.
- Run the existing security policy against staged content and stop on `block`.
- Keep the quarantine workspace outside the contributed package and remove it
  predictably after review or failure.

## P2 Intake Receipts

Implementation status: merged in PR #51. The installable
`hpc-skill receipt create|verify` commands and standalone repository wrapper
share one deterministic, standard-library implementation and two public JSON
schemas for receipts and external maintainer decisions.

- Define a portable JSON receipt for source digest, bounded inventory, scanner
  and policy versions, findings, accepted digest-bound exceptions, reviewer
  disposition, and generated context digest.
- Make receipts deterministic for identical inputs and reject stale source,
  policy, exception, or inventory bindings.
- Distinguish `blocked`, `review-required`, and `accepted` without treating a
  scanner pass as proof of domain correctness.

## P3 Review And Adoption Evidence

Implementation status: merged in PR #52. The installable
`hpc-skill evidence packet|check` commands and standalone wrapper share one
standard-library implementation and four strict public JSON contracts.

- Generate maintainer packets and issue-ready summaries from intake receipts.
- Bind independent review decisions and public-safe adoption reports to exact
  contribution digests and versions.
- Keep safety acceptance, domain review, adoption evidence, and maturity
  promotion as separate decisions with explicit owners.
- Require approved coverage for every declared domain, distinct safety owners
  for submitted safety reviews, and adopters independent of intake and review
  owners.

## P4 Trusted Agent Consumption

Implementation status: complete on the P4 branch. The installable
`hpc-skill community-context build|check|show` commands reconstruct accepted
content from the quarantine snapshot, embed exact-bound P2/P3 evidence, and
share the same validator used by the optional read-only MCP server.

- Expose only accepted, digest-verified community context through installed CLI
  and read-only MCP discovery.
- Surface source, policy, receipt, review, maturity, and risk provenance to
  Codex, Claude Code, and other clients before content is returned.
- Preserve closed-world tool and argument allowlists; intake never grants
  execution, job submission, transfer, install, or private site-policy access.

## P5 Pilot And Release

- Exercise benign, ambiguous, and adversarial fixture bundles across directory
  and archive intake paths.
- Run installed-wheel and MCP isolation tests outside the checkout.
- Publish machine-readable gate status and a public-safe pilot report.
- Cut `v0.6.0` only from a clean reviewed commit with an immutable manifest and
  verified tag-triggered attestations.

## Evidence Boundary

Synthetic fixtures can prove deterministic parsing, isolation, policy, and
receipt behavior. They cannot prove a community skill is operationally correct,
independently reviewed, adopted at an HPC site, or beneficial to an agent. No
maturity promotion or comparative performance claim may be inferred from an
intake receipt alone.
