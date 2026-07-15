# v0.6 Completion Matrix

Status: P0 release hygiene merged in PR #48. P1 quarantined intake is complete
on its release branch with review and merge pending. P2 through P5 remain
planned. No community bundle acceptance, independent review, adoption, maturity
promotion, or measured agent-lift outcome is claimed.

| Phase | Status | Completion gate |
| --- | --- | --- |
| P0 release hygiene | Merged in PR #48 | v0.5 provenance receipt, corrected release state, immutable snapshot checks, refreshed CI actions, v0.6 milestone #7 and tracker #49, 192-test local gate, and passing Validate/Package CI. |
| P1 quarantined intake | Complete on P1 branch | Untrusted directories, ZIP files, and TAR files are bounded, staged, scanned, cleaned, and rejected before instruction loading or execution; reports always keep context loading disabled; the 210-test local gate and an isolated installed-wheel smoke pass. |
| P2 intake receipts | Planned | Deterministic receipts bind source, inventory, policy, findings, exceptions, review disposition, and accepted context digest. |
| P3 review and adoption evidence | Planned | Independent decisions and public-safe adoption reports bind exact contribution digests without automatic maturity promotion. |
| P4 trusted agent consumption | Planned | CLI and MCP return only accepted context with visible trust provenance and no operational action surface. |
| P5 pilot and release | Planned | Fixture pilot, installed isolation, honest gate status, immutable manifest, clean tag, and verified attestations pass. |

## External Gates

| Gate | Status | Required evidence |
| --- | --- | --- |
| Community acceptance | Closed | A real contribution must complete quarantine, scanner review, and maintainer disposition. |
| Independent domain review | Closed | Reviewers must assess exact source digests using public-safe evidence. |
| Adoption evidence | Closed | A public report must bind a released skill version and describe the site-safe outcome. |
| Maturity promotion | Closed | Lifecycle requirements, independent approvals, and maintainer decision must all pass. |
| Comparative agent evidence | Closed | Authorized real runs, redaction, blinded scoring, reconciliation, and publication gates are required. |
