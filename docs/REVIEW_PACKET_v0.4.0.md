# v0.4.0 Skill Review Packet

This generated packet tracks evidence-backed maturity review without
promoting skills automatically. Static readiness is not domain approval.

## Summary

- Candidates: 5
- Static ready: 5
- Promotion ready: 0
- Status counts: `{"awaiting-review": 5, "blocked": 0, "promoted": 0, "promotion-ready": 0}`

## Candidate Queue

| Skill | Quality | Risk | Status | Safety review | Blockers |
| --- | ---: | --- | --- | --- | --- |
| `job-failure-triage` | 98 | `low` | `awaiting-review` | not required | public-review-issue, review-commit, domain-review, maintainer-decision |
| `shared-project-permissions-triage` | 100 | `low` | `awaiting-review` | required | public-review-issue, review-commit, domain-review, safety-review, maintainer-decision |
| `slurm-oom-memory-triage` | 100 | `low` | `awaiting-review` | not required | public-review-issue, review-commit, domain-review, maintainer-decision |
| `slurm-output-log-triage` | 100 | `low` | `awaiting-review` | not required | public-review-issue, review-commit, domain-review, maintainer-decision |
| `slurm-pending-reason-triage` | 98 | `low` | `awaiting-review` | not required | public-review-issue, review-commit, domain-review, maintainer-decision |

## Promotion Boundary

- Open and link a public maturity-review issue.
- Pin review to one full Git commit.
- Record an independent domain approval for that commit.
- Complete safety review when risk or admin scope requires it.
- Record a maintainer decision before changing `skill.json` maturity.
- Adoption evidence is optional for `reviewed` and required later for `field-tested`.
