# Maintainer Guide

For maintainer rotation, role ownership, and operational continuity, see
[Maintainer Handoff](MAINTAINER_HANDOFF.md). For project-level review policy,
domain ownership, and maturity promotion, see [Governance](GOVERNANCE.md) and
[Maturity Review](MATURITY_REVIEW.md). For routing pull requests and issues to
the right maintainers, see [Review Routing](REVIEW_ROUTING.md). For day-to-day
issue and pull request intake, see [Triage Runbook](TRIAGE_RUNBOOK.md).

## Review Checklist

- The skill id matches the directory name.
- The README explains target users, assumptions, and risks.
- Examples avoid private hostnames, usernames, accounts, tokens, and dataset
  paths.
- Resource requests are conservative.
- Medium and high-risk skills explain cost, side effects, and rollback or
  cleanup expectations.
- Upstream references point to primary documentation where possible.
- `python3 tools/validate_skills.py` passes.

## Release Guidance

Until the registry reaches version `0.1.0`, use lightweight tags only when a
meaningful batch of skills or schema changes lands.

Suggested release notes sections:

- Added skills.
- Changed skill metadata.
- Validator changes.
- Breaking schema changes.
- Security or safety notes.

## Ownership

Each skill should eventually have at least one domain maintainer. Facility
operations, admin, and security-sensitive skills should require review from a
maintainer with production HPC experience.

## Review Routing

Use [Review Routing](REVIEW_ROUTING.md) to map changed paths, labels, skill
domains, and risk levels to the smallest reviewer set that covers format,
domain correctness, and shared-system safety. Update `.github/CODEOWNERS` after
the public repository has real GitHub users or teams.

Use [Triage Runbook](TRIAGE_RUNBOOK.md) before routing when an issue or pull
request still needs its scope, sensitivity, label set, or next action clarified.

## Maturity Promotion

Use the maturity review issue template before changing a skill from `seed` to a
higher maturity level. Promotion pull requests should update the manifest,
refresh generated registry files, link public evidence, and keep private site
details out of the repository.
