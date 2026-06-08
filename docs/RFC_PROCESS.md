# RFC Process

Use an RFC when a proposal changes how the registry works, not just what it
contains. Small skills, documentation fixes, and site adapter updates can go
directly through normal issues and pull requests.

## When To Open An RFC

Open an RFC for:

- Skill manifest schema changes.
- Risk model or maturity model changes.
- New required validation gates.
- New collection or site adapter policy.
- Public governance or maintainer process changes.
- Tooling behavior that affects existing contributors or downstream adopters.

Use a safety review issue instead when the main question is risk, privacy, or
shared-system impact for one concrete change.

## Workflow

1. Open an issue using the RFC proposal template.
2. Copy `docs/rfcs/0000-template.md` into `docs/rfcs/NNNN-short-title.md`.
3. Fill in motivation, design, compatibility, validation, rollout, and safety
   sections.
4. Link the RFC pull request to the issue.
5. Let domain reviewers comment before accepting changes that affect their
   area.
6. If accepted, merge the RFC and record the decision in `docs/decisions/`.

RFC numbers should be assigned in increasing order. Use `0000` only for the
template.

## States

- `draft`: open for shaping.
- `proposed`: ready for maintainer review.
- `accepted`: maintainers agree to implement.
- `superseded`: replaced by a newer RFC or decision.
- `withdrawn`: closed without adoption.

## Decision Records

Decision records capture accepted policy or architecture choices in a shorter
form than an RFC. Use them when the project needs a stable reference for why a
choice was made. They should link to the issue, RFC, or pull request that
contains the discussion.

## Compatibility

Changes that affect existing skills, schemas, generated registry output, or CLI
behavior must explain migration impact. If a change requires contributors to
edit existing skills, the RFC should include a concrete migration checklist.

## Safety And Privacy

RFCs must avoid private hostnames, user data, allocation names, credentials,
internal security procedures, and unpublished cluster policy. When a proposal
touches high-risk behavior, pair the RFC with a safety review issue.
