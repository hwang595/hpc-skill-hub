# Contributor Ladder

HPC Skill Hub should be easy to join without relying on private maintainer
context. This ladder describes how contributors can move from one-off reports
to recurring review and maintainer roles as the project grows.

## Principles

- Keep contribution paths public, documented, and reversible.
- Reward useful review, testing, documentation, and adoption reports, not only
  new code.
- Require public-safe evidence before increasing responsibility.
- Separate domain authority from repository administration.
- Rotate responsibilities when people step back.

## Roles

| Role | Typical Contributions | Trust Signal | Permissions |
| --- | --- | --- | --- |
| User or reporter | Opens bug reports, skill requests, adoption reports, or documentation issues. | Public-safe issue with clear environment assumptions and no private cluster details. | No repository permissions required. |
| First-time contributor | Fixes docs, adds examples, updates metadata, or proposes a focused skill. | One pull request that follows the templates and passes `make check`. | No repository permissions required. |
| Recurring contributor | Maintains a small area, responds to review, refreshes generated artifacts, or improves tests. | Multiple accepted pull requests or sustained issue triage. | No repository permissions required. |
| Domain reviewer | Reviews skills in one of the areas listed in [Domain Reviewers](DOMAIN_REVIEWERS.md). | Public reviews, adoption evidence, or operational expertise relevant to the area. | Review requests; no merge permission required. |
| Registry maintainer | Reviews schema, validation, generated registry output, collections, and general contribution flow. | Sustained contributions plus trusted judgment on portability, safety, and compatibility. | May receive triage and merge permissions after public nomination. |
| Tooling maintainer | Owns CLI behavior, validators, generated docs, static site output, packaging, and CI. | Accepted tooling changes with tests and release-awareness. | May receive merge permissions for tooling paths. |
| Release owner | Coordinates a specific release checklist, tag, notes, manifest, and GitHub release. | Maintainer trust plus successful dry-run of the release process. | Temporary or ongoing release permissions. |

## Progression

1. Start with a public issue, adoption report, or focused pull request.
2. Use templates and keep examples public-safe.
3. Run `make check` before asking for review.
4. Ask for domain review when a change crosses scheduler, storage, software,
   GPU, workflow, facility, or site-adapter boundaries.
5. After repeated useful contributions, ask in a governance or maintainer issue
   whether a reviewer or maintainer role would help the project.

Maintainers should make role changes in public whenever possible. If private
coordination is needed for security or account administration, summarize the
public outcome in an issue or pull request.

## Reviewer Onboarding

Before assigning recurring reviewer work, maintainers should confirm:

- The reviewer area is listed in [Domain Reviewers](DOMAIN_REVIEWERS.md).
- The reviewer understands the public-safe boundary in [Safety Model](SAFETY_MODEL.md).
- The reviewer can point to public evidence, public documentation, or a
  relevant adoption report.
- The reviewer knows how to use [Review Routing](REVIEW_ROUTING.md) and
  [Maturity Review](MATURITY_REVIEW.md).

Domain reviewers can stay lightweight. A reviewer may help with only one skill
or collection without becoming a repository maintainer.

## Maintainer Onboarding

Before granting maintainer permissions:

- Confirm the person has made or reviewed multiple public-safe contributions.
- Confirm they understand generated artifacts, release manifests, and
  `make check`.
- Confirm the paths they will own in `.github/CODEOWNERS`.
- Record the role and expected scope in a public issue or pull request.
- Use [Maintainer Handoff](MAINTAINER_HANDOFF.md) for operational continuity.

## Rotation And Stepping Back

Roles are not permanent obligations. When someone steps back:

- Transfer open review context in public comments.
- Remove or narrow CODEOWNERS entries when needed.
- Assign another owner for release, tooling, or high-risk queues.
- Keep historical credit in commits, issues, and release notes.

The project should prefer a small active maintainer set over a large stale
permission list.
