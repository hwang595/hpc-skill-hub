# HPC Skill Hub v0.6.0

Status: release candidate. The repository capability and release-candidate
manifest are ready for review. The tag, GitHub release, tag-triggered Package
run, and artifact attestations do not exist yet, so release provenance remains
pending.

v0.6 adds a verified path for community-contributed skills: quarantine first,
bind every decision to exact evidence, and expose instructions to agents only
after applicable review gates complete. None of these contracts grants
permission to execute examples or perform operational HPC actions.

## Registry Snapshot

- Skills: 97.
- Collections: 12.
- Site adapters: 2.
- Registry schema: `0.2.0`.
- Package version: `0.6.0`.
- Community pilot: 9/9 synthetic cases pass.
- Test suite: 263/263 pass on Python 3.11 with MCP and schema dependencies.

## Added

- No-execution intake for untrusted directories, ZIP files, and TAR files with
  traversal, symlink, nesting, portability, encoding, binary, count, size, and
  compression bounds.
- Deterministic P2 receipts binding source, inventory, scanner, policy,
  findings, accepted exceptions, maintainer disposition, and accepted context.
- P3 review packets, exact-bound domain and safety decisions, public-safe
  adoption reports, ownership separation, and aggregate evidence status.
- P4 community context bundles that reconstruct accepted text from the
  quarantine snapshot and revalidate source, policy, receipt, review, risk,
  maturity, file, and bundle digests.
- `hpc-skill community-context build|check|show`, with metadata-only checking
  separate from the explicit full-content operation.
- An optional MCP `list_community_contexts` tool and
  `hpc-skill://community/{contribution_id}/{version}` resource. Community
  context is disabled by default and only prebuilt, review-complete bundles can
  be configured at server startup.
- A deterministic P5 pilot covering benign, ambiguous, and adversarial fixtures
  through directory, ZIP, and TAR transports.
- A reusable installed-wheel verifier that creates a temporary venv, removes
  source-path overrides, validates the imported module location, rebuilds the
  accepted synthetic context, and probes both default and configured MCP modes.

## Safety Results

- Benign fixtures become `ready-for-review`; they are never instruction-loaded
  during intake.
- Ambiguous dynamic evaluation becomes `review-required` under
  `execution.dynamic-eval`.
- Adversarial prompt injection becomes `blocked` under
  `prompt.ignore-instructions`.
- Every pilot case reports no execution, no instruction content returned,
  disabled context loading, complete inventory, and cleaned quarantine.
- The accepted synthetic pipeline reaches `review-complete` but keeps maturity
  promotion `not-authorized`, records zero adoption reports, and authorizes no
  execution, submission, transfer, install, or private site-policy access.

## Installed Isolation

The Package workflow builds and checks the wheel, then runs reusable core and
MCP isolation probes outside the checkout. MCP starts with zero community
contexts by default. Its explicit pilot bundle appears in metadata-only
discovery without `files`, while the separately requested resource presents
provenance before the bounded content.

## Evidence Boundary

The P5 fixtures and reviewer identities are controlled synthetic test data.
This release does not claim:

- acceptance of a real community contribution;
- independent external domain or safety review;
- successful adoption at an HPC site;
- promotion of any skill beyond its current maturity;
- comparative improvement from skills or MCP in real agent workloads.

Those gates remain closed until exact public-safe external evidence satisfies
their separate contracts.

## Release Verification

Before creating `v0.6.0`, merge the reviewed release commit and require green
Validate and Package workflows. After the tag-triggered Package and attestation
jobs complete, download the manifest, wheel, and source distribution, verify
each with `gh attestation verify`, and only then add
`registry/provenance/v0.6.0.json`. The existing v0.5 provenance receipt remains
the latest verified release record until that post-release step is complete.
