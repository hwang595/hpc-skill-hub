# v0.6 Completion Matrix

Status: P0 release hygiene merged in PR #48, P1 quarantined intake merged in PR
#50, P2 deterministic intake receipts merged in PR #51, and P3 review and
adoption evidence merged in PR #52. P4 trusted agent consumption is complete on
the current branch; P5 remains planned.
No real community bundle acceptance, independent review, adoption, maturity
promotion, or measured agent-lift outcome is claimed.

| Phase | Status | Completion gate |
| --- | --- | --- |
| P0 release hygiene | Merged in PR #48 | v0.5 provenance receipt, corrected release state, immutable snapshot checks, refreshed CI actions, v0.6 milestone #7 and tracker #49, 192-test local gate, and passing Validate/Package CI. |
| P1 quarantined intake | Merged in PR #50 | Untrusted directories, ZIP files, and TAR files are bounded, staged, scanned, cleaned, and rejected before instruction loading or execution; reports always keep context loading disabled; the 210-test local gate and an isolated installed-wheel smoke pass. |
| P2 intake receipts | Merged in PR #51 | Deterministic receipts and external maintainer decisions bind source, bounded inventory, scanner, policy, findings, exceptions, and candidate/accepted context digests; fresh verification rejects stale evidence and keeps domain and independent review explicitly incomplete; the 225-test full local gate passes. |
| P3 review and adoption evidence | Merged in PR #52 | Deterministic packets and issue summaries fresh-verify accepted P2 receipts; independent domain and safety decisions plus public-safe adoption reports bind exact source, context, contribution, and review-basis digests; declared-domain coverage and distinct owners are enforced; aggregate status never authorizes maturity promotion; the 242-test full suite passes with 7 optional-dependency skips. |
| P4 trusted agent consumption | Complete on P4 branch | CLI reconstructs content only from the bounded quarantine snapshot after `review-complete`; portable bundles embed exact receipt, packet, review, status, policy, risk, and maturity evidence; `check` returns no content; MCP is disabled for community content by default and accepts only startup-time prebuilt bundles through a seven-tool, two-resource closed-world surface; all 252 tests pass on Python 3.11 with schema and MCP dependencies, plus an isolated installed-wheel context/resource smoke test. |
| P5 pilot and release | Planned | Fixture pilot, installed isolation, honest gate status, immutable manifest, clean tag, and verified attestations pass. |

## External Gates

| Gate | Status | Required evidence |
| --- | --- | --- |
| Community acceptance | Closed | A real contribution must complete quarantine, scanner review, and maintainer disposition. |
| Independent domain review | Closed | Reviewers must assess exact source digests using public-safe evidence. |
| Adoption evidence | Closed | A public report must bind a released skill version and describe the site-safe outcome. |
| Maturity promotion | Closed | Lifecycle requirements, independent approvals, and maintainer decision must all pass. |
| Comparative agent evidence | Closed | Authorized real runs, redaction, blinded scoring, reconciliation, and publication gates are required. |
