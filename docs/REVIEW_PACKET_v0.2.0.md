# v0.2.0 Reviewed-Skill Pilot Packet

This packet is generated from `registry/index.json` through
`tools/review_packet.py`. It routes seed skills toward first domain
review without promoting maturity automatically.

## Summary

- Target version: `v0.2.0`
- Milestone: `v0.2.0 reviewed-skill pilot`
- Skills: 97
- Seed skills: 97
- Candidate pool: 97
- Display limit: 12
- Collection filter: `all`
- Risk counts: {"low": 27, "medium": 70}

## Promotion Gate

- Maturity-review issue is open and linked from the pull request.
- A domain reviewer confirms scope, examples, assumptions, and references.
- Safety review is completed when suggested by risk level or admin scope.
- The pull request updates skill.json, generated registry artifacts, and release notes.
- Public evidence excludes hostnames, usernames, allocations, tickets, tokens, and private paths.
- make check passes locally and in GitHub Actions.

## Reviewer Queue

| Review focus | Candidates | Skill ids |
| --- | ---: | --- |
| AI, GPU, and accelerator workflows | 1 | `gpu-memory-triage` |
| Facility operations and training | 7 | `cluster-usage-report-readonly`, `module-tree-health-check`, `node-health-readonly-triage`, `shared-project-permissions-triage`, `slurm-maintenance-reservation-triage`, `slurm-node-failure-triage`, `slurm-qos-account-limit-triage` |
| MPI and performance | 4 | `blas-openmp-thread-control`, `compiler-mpi-matrix`, `darshan-io-profile-analysis`, `performance-profile-basic` |

## Candidate Issues

| Skill | Risk | Score | Review focus | Suggested labels | Evidence |
| --- | --- | ---: | --- | --- | --- |
| `gpu-memory-triage` | `low` | 8 | AI, GPU, and accelerator workflows | maturity-review, needs-domain-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `cluster-usage-report-readonly` | `low` | 8 | Facility operations and training | maturity-review, needs-domain-review, safety-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `module-tree-health-check` | `low` | 8 | Facility operations and training | maturity-review, needs-domain-review, safety-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `node-health-readonly-triage` | `low` | 8 | Facility operations and training | maturity-review, needs-domain-review, safety-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `shared-project-permissions-triage` | `low` | 8 | Facility operations and training | maturity-review, needs-domain-review, safety-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `slurm-maintenance-reservation-triage` | `low` | 8 | Facility operations and training | maturity-review, needs-domain-review, safety-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `slurm-node-failure-triage` | `low` | 8 | Facility operations and training | maturity-review, needs-domain-review, safety-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `slurm-qos-account-limit-triage` | `low` | 8 | Facility operations and training | maturity-review, needs-domain-review, safety-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `blas-openmp-thread-control` | `low` | 8 | MPI and performance | maturity-review, needs-domain-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `compiler-mpi-matrix` | `low` | 8 | MPI and performance | maturity-review, needs-domain-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `darshan-io-profile-analysis` | `low` | 8 | MPI and performance | maturity-review, needs-domain-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |
| `performance-profile-basic` | `low` | 8 | MPI and performance | maturity-review, needs-domain-review, good-first-issue | low risk, examples, references, static or dry-run test, collection coverage, README |

## Issue Body Template

Use this template for each candidate before changing maturity:

```markdown
## Skill

- Skill id: `<skill-id>`
- Current maturity: `seed`
- Requested maturity: `reviewed`
- Review focus: `<review-focus>`

## Evidence

- [ ] Domain reviewer has checked scope and assumptions.
- [ ] Examples are conservative for shared HPC systems.
- [ ] Risk level matches the strongest action in the skill.
- [ ] Public references are current enough for adoption.
- [ ] No private hostnames, usernames, allocations, tickets, tokens, or internal paths are included.
- [ ] `make check` passes in the linked pull request.

## Follow-up

- PR: `<link>`
- Safety review issue, if needed: `<link>`
- Adoption report, if available: `<link>`
```

## Maintainer Notes

- Do not promote a skill only because it scores highly in this packet.
- Use `safety-review` when the skill touches admin evidence, facility operations, shared software policy, quotas, or larger side effects.
- Use adoption reports for `field-tested`; this packet targets `reviewed` only.
