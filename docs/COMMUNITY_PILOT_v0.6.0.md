# v0.6 Community Intake Pilot

This is a deterministic synthetic safety pilot. It validates repository
contracts only; it is not evidence of a real community acceptance, external
domain review, site adoption, maturity promotion, or agent-performance lift.

## Result

- Matrix: 9/9 cases passed.
- Policy: `community-default@0.1.0`.
- Accepted pipeline: `review-complete` with maturity `not-authorized`.
- Machine-readable report: `registry/community-pilot-v0.6.0.json`.
- Report digest: `775e3d09e48c02e3f153ef5604589a6380ae75ea8a4e1c22cca495358f627b20`.

## Fixture Matrix

| Fixture | Transport | Expected | Observed | Findings | Result |
| --- | --- | --- | --- | --- | --- |
| `benign` | `directory` | `ready-for-review` | `ready-for-review` | `none` | pass |
| `benign` | `zip` | `ready-for-review` | `ready-for-review` | `none` | pass |
| `benign` | `tar` | `ready-for-review` | `ready-for-review` | `none` | pass |
| `ambiguous` | `directory` | `review-required` | `review-required` | `execution.dynamic-eval` | pass |
| `ambiguous` | `zip` | `review-required` | `review-required` | `execution.dynamic-eval` | pass |
| `ambiguous` | `tar` | `review-required` | `review-required` | `execution.dynamic-eval` | pass |
| `adversarial` | `directory` | `blocked` | `blocked` | `prompt.ignore-instructions` | pass |
| `adversarial` | `zip` | `blocked` | `blocked` | `prompt.ignore-instructions` | pass |
| `adversarial` | `tar` | `blocked` | `blocked` | `prompt.ignore-instructions` | pass |

Every intake case kept context loading disabled, performed no execution,
returned no instruction content, and cleaned its temporary quarantine.
Directory, deterministic ZIP, and deterministic TAR inputs produced the
same inventory digest for each fixture.

## Accepted Pipeline

The benign fixture additionally exercises an exact-bound accepted P2 receipt,
synthetic P3 domain and safety decisions, and P4 context construction. The
result is review-complete but remains non-authorizing: examples do not execute
automatically, operational actions require explicit intent, and maturity
promotion remains `not-authorized`.

## Installed Isolation

CI must build the wheel and run `tools/installed_release_smoke.py` from a
temporary directory for both core and MCP modes. The verifier removes
`PYTHONPATH`, checks the imported module path is outside the checkout, requires
zero community resources by default, and verifies one explicit review-complete
bundle without exposing it through the metadata-only catalog.

## Evidence Boundary

The fixtures are controlled repository test data and the reviewer identities
are synthetic. A passing report cannot promote a skill, establish operational
correctness, or open comparative and adoption evidence gates.
