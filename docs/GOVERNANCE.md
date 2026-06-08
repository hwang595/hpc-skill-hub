# Governance

HPC Skill Hub starts with lightweight maintainer ownership and a bias toward
transparent review. The goal is to let HPC centers, research groups, tool
maintainers, and instructors contribute reusable operational knowledge without
turning the core registry into a collection of private cluster policies.

## Maintainer Roles

- Registry maintainers own schemas, validation, releases, and general review.
- Domain maintainers review skills in areas such as schedulers, containers,
  data movement, AI/HPC, bioinformatics, molecular dynamics, CFD, climate, and
  facility operations. Use [Domain Reviewers](DOMAIN_REVIEWERS.md) to recruit
  and route seed-stage reviewers.
- Site adapter maintainers own public local policy mappings for a specific
  institution, training cluster, or public environment.

One person may hold more than one role during the seed stage.

## Contributor Growth

Use [Contributor Ladder](CONTRIBUTOR_LADDER.md) for the path from first issue or
pull request to recurring contributor, domain reviewer, maintainer, or release
owner. Role changes should be based on public-safe evidence and documented
scope, not private context.

## Review Expectations

- Low-risk changes can be reviewed by any registry maintainer.
- Medium-risk skills need review for resource impact, file output, cleanup, and
  portability.
- High-risk skills need explicit domain maintainer approval before promotion.
- Facility operations, admin behavior, security-sensitive guidance, and
  shared-system changes require production HPC experience in review.
- Private hostnames, usernames, allocations, internal project identifiers,
  credentials, and unpublished security procedures do not belong in public
  issues, pull requests, examples, or site adapters.

## Skill Maturity

- `seed`: useful starting point with static validation and conservative
  examples.
- `reviewed`: checked by a maintainer with relevant domain knowledge.
- `field-tested`: exercised on at least one real environment with public notes.
- `maintained`: has an active owner and current upstream references.

Promotion should be evidence-based. A passing validator is necessary, but not
enough by itself for higher maturity.

Use [Maturity Review](MATURITY_REVIEW.md) and the maturity review issue
template when requesting promotion from `seed` to `reviewed`, `field-tested`,
or `maintained`.

## Decision Process

Most decisions should happen in pull requests and issues. Maintainers should
prefer small, reversible decisions and document tradeoffs when a change affects
schema compatibility, safety policy, or public adoption paths.

Use the [RFC Process](RFC_PROCESS.md) for project-level changes such as schema
updates, validation gates, risk or maturity policy, site adapter policy, or
governance changes. Accepted project-level decisions should be recorded in
`docs/decisions/`.

Escalate to a dedicated safety review issue when a contribution:

- Could affect shared systems or facility operations.
- Encourages expensive or destructive commands.
- Uses site-specific policy that may expose private operational details.
- Changes risk labels, maturity labels, schemas, or validation rules.

## Site Policy Boundary

Core skills should stay portable. Site-specific details belong in site adapters
when they can be public, or outside the repository when they are private. A
site adapter may document public partitions, modules, containers, storage
classes, and support links, but it must not encode private hostnames,
allocation names, internal security procedures, or user data.

## Maintainer Rotation

For operational continuity, use [Maintainer Handoff](MAINTAINER_HANDOFF.md)
when adding or rotating maintainers. CODEOWNERS should be updated after the
GitHub organization or repository owner is known.
