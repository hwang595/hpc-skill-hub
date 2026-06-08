# Adoption Guide

This guide helps HPC centers, research software teams, and training programs
adopt HPC Skill Hub without turning it into a site-specific fork.

## For HPC Centers

Start by contributing a site adapter rather than editing core skills. The
adapter can describe public local conventions for:

- Scheduler partitions.
- Module names.
- Storage areas.
- Container guidance.
- Data transfer guidance.
- Local warnings for generic skills.

Keep internal policy, private hostnames, account names, and unpublished security
details out of the public adapter.

## For Research Groups

Start with a domain skill request or a draft skill package. Good early
contributions include:

- A known-working Slurm template for the application.
- Module or container assumptions.
- Expected input and output layout.
- A small smoke-test dataset or synthetic test command.
- Common failure modes and fixes.

## For Tool Maintainers

Tool maintainers can contribute integration skills that show safe HPC usage for
their tool. Prefer generic patterns first, then add site adapters when a center
has public local conventions.

## For Instructors

Teaching skills should be low-risk, short-running, and explicit about what the
student should observe. Keep examples small enough for shared training clusters
or classroom allocations.

## Suggested Rollout

1. Use the seed skills internally.
2. Add one site adapter with public policy notes.
3. Add one or two site-specific override notes for common user questions.
4. Open issues for missing domain workflows.
5. Promote stable entries from `seed` to `reviewed` after operational review.
6. Publish a release once the registry, adapter, and validator flow is stable.
