# Maintainer Handoff

This document helps a new maintainer take over routine operation of the HPC
Skill Hub repository without relying on private context.

## Maintainer Roles

- Project lead: coordinates roadmap, releases, and community governance.
- Registry maintainer: reviews skill manifests, examples, collections, and
  generated registry output.
- Domain maintainer: reviews specialized skills such as MPI, GPU, workflow
  engines, containers, data movement, or facility operations.
- Tooling maintainer: owns validators, generated docs, CLI behavior, tests, and
  GitHub workflows.
- Release owner: prepares release notes and confirms generated artifacts match
  the committed source.

One person can hold multiple roles during the seed stage. As adoption grows,
split these responsibilities across institutions and domains.

## Weekly Maintenance Loop

1. Review open pull requests and label anything that needs triage or domain
   review.
2. Run or confirm `make check` for pending changes.
3. Check new issues for private cluster details and ask reporters to remove
   sensitive information when needed.
4. Triage Dependabot pull requests and merge low-risk CI or packaging updates
   after checks pass.
5. Promote well-scoped requests into `good-first-issue` or `help-wanted`.

Use [Triage Runbook](TRIAGE_RUNBOOK.md) for the intake loop and
[Review Routing](REVIEW_ROUTING.md) when assigning domain reviewers.

## Pull Request Review Expectations

- Schema, CLI, validator, or registry-generation changes need tests.
- New skills need a manifest, README, examples, and clear risk notes.
- Site adapters must use public documentation and avoid private operational
  details.
- High-risk skills need review from someone with production HPC operations
  experience.
- Generated files should be refreshed in the same pull request as their source
  changes.

## Release Handoff

Before transferring release responsibility:

- Confirm `docs/RELEASE_PROCESS.md` is current.
- Confirm `registry/index.json`, `registry/health.json`, generated catalog
  docs, and compatibility tables are fresh.
- Confirm the release owner can build and install the package locally.
- Confirm the release owner has GitHub permission to create releases and manage
  Pages workflows.

## Sensitive Information

The public repository should not contain private hostnames, usernames, account
names, internal project identifiers, tokens, unpublished policy, or private data
paths. Move sensitive reports to private maintainer channels or GitHub private
vulnerability reporting, then summarize only the public remediation in issues or
release notes.

## Continuity Notes

When a maintainer rotates off:

- Transfer open pull request context in comments.
- Assign a new owner for any high-risk review queue.
- Update CODEOWNERS if GitHub usernames or teams change.
- Record any schema compatibility decisions in `docs/SKILL_SPEC.md` or an
  issue, rather than in private chat.
