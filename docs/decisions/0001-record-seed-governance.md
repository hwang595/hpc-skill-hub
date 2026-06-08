# Decision 0001: Record Seed Governance

Date: 2026-06-08

## Status

Accepted.

## Context

HPC Skill Hub is starting as a seed open-source registry with reusable skills,
site adapters, validation tooling, GitHub metadata, and launch documentation.
The project needs lightweight governance that does not block early contribution
but still protects users, shared systems, and site privacy.

## Decision

Use lightweight repository maintainer ownership during the seed stage:

- Keep core skills portable and put public local policy in site adapters.
- Require safety review for high-risk or facility-operations changes.
- Promote skill maturity only with evidence beyond static validation.
- Use RFCs for schema, governance, validation, risk, maturity, and other
  ecosystem-level changes.
- Record accepted project-level decisions in `docs/decisions/`.

## Consequences

- Contributors have a clear path for normal skills, safety reviews, and RFCs.
- Maintainers can evolve quickly while documenting durable choices.
- Private cluster policy stays outside the core registry unless it can be
  published safely.
- The process can be tightened later when external maintainers join.
