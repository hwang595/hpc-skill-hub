# Triage Runbook

Use this runbook to turn incoming issues and pull requests into clear, public,
reviewable work. It complements [Review Routing](REVIEW_ROUTING.md), which
decides who should review a change after the triage owner understands its
scope.

## Intake Loop

Run this loop at least weekly during the seed stage, and more often after a
public launch:

1. Check new issues, pull requests, and Dependabot updates.
2. Remove or ask reporters to remove private cluster details before deeper
   discussion.
3. Apply one primary type label such as `skill-request`, `site-adapter`, `bug`,
   `documentation`, `adoption`, `integration`, `rfc`, or `maturity-review`.
4. Add state labels such as `needs-triage`, `needs-domain-review`,
   `safety-review`, `good-first-issue`, or `help-wanted` when useful.
5. Route domain-sensitive work through [Review Routing](REVIEW_ROUTING.md).
6. Leave a short public comment that names the next expected action.

## Issue Triage

| Incoming Work | First Action | Likely Labels |
| --- | --- | --- |
| New reusable workflow request | Confirm scope, expected users, risk, and public references. | `skill-request`, `needs-triage` |
| Site adapter request | Confirm all local policy details can be public. | `site-adapter`, `needs-triage` |
| Bug report | Reproduce with public-safe steps or ask for a smaller example. | `bug`, `needs-triage` |
| Documentation request | Identify whether it affects contributor, adopter, or maintainer docs. | `documentation`, `good-first-issue` |
| Adoption report | Capture public-safe results and follow-up requests. | `adoption`, `needs-domain-review` |
| Integration request | Identify the registry surface, compatibility needs, and safety model. | `integration`, `needs-triage` |
| Safety concern | Move sensitive details out of public view and request operations review. | `safety-review`, `high-risk-skill` |
| Schema or policy proposal | Decide whether normal PR review is enough or an RFC is needed. | `schema-change`, `rfc`, `governance` |

## Pull Request Triage

For each pull request:

1. Check whether the change has a matching issue, RFC, maturity review, safety
   review, or adoption report.
2. Confirm the validation checklist in the pull request template is complete or
   clearly marked as not applicable.
3. Ask for generated files when source changes affect `registry/`,
   `docs/SKILL_CATALOG.md`, or `docs/REGISTRY_HEALTH.md`.
4. Add `needs-domain-review` when domain judgment is required before merge.
5. Add `safety-review` for facility operations, admin behavior, destructive
   cleanup, quota/accounting behavior, security-sensitive guidance, or
   high-risk examples.
6. Use `good-first-issue` only when the scope is small, low-risk, and unlikely
   to require private site knowledge.

## Label Semantics

- `needs-triage`: maintainers have not yet confirmed scope, sensitivity, and
  next action.
- `needs-domain-review`: a domain reviewer should check portability, safety,
  assumptions, and references.
- `help-wanted`: maintainers welcome external work or review.
- `good-first-issue`: maintainers believe the task is small and low-risk for a
  first-time contributor.
- `safety-review`: review is needed for risk, privacy, shared-system impact, or
  high-risk behavior.
- `maturity-review`: evidence is being reviewed before a skill moves beyond
  `seed`.
- `integration`: a downstream tool, portal, assistant, workflow project, or
  registry consumer needs maintainer input.

Remove `needs-triage` after the next action is clear. Remove
`needs-domain-review` only after the relevant reviewer has commented or the
scope changes so domain review is no longer required.

## Escalation Rules

Escalate from ordinary triage when:

- The report includes private hostnames, usernames, account names, allocation
  names, internal project identifiers, tokens, unpublished security procedures,
  or private dataset paths.
- The change could alter shared system state, scheduler behavior, storage
  policy, accounting, quotas, node state, or admin workflows.
- A skill would encourage expensive resource use without clear bounds.
- A proposal changes schemas, risk labels, maturity policy, governance, release
  process, or site adapter boundaries.

Use a safety review issue for risk and privacy questions. Use the RFC process
for project-level decisions. Use maturity review only after the skill already
has enough public evidence to consider promotion.

## Response Targets

These are seed-stage targets, not strict service-level agreements:

- New issue or pull request: initial triage within 7 days.
- Safety concern: acknowledge within 2 business days and move sensitive details
  out of public discussion.
- External pull request: request validation or reviewer routing within 7 days.
- Maturity review: identify the missing evidence or reviewer within 14 days.
- Release blocker: assign an owner before the next planned release tag.

## Closing Guidance

Close issues when the request is resolved, withdrawn, not public-safe, or out
of scope for a portable HPC registry. Before closing, leave a short explanation
and, when possible, point to the relevant skill, doc, RFC, safety review,
maturity review, or future backlog item.
