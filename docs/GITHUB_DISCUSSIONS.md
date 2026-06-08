# GitHub Discussions

Use Discussions for open-ended ecosystem conversations that are not ready for a
focused issue or pull request. Use issues when the next action is concrete,
trackable, and belongs in the maintainer queue.

GitHub discussion category forms live under `.github/DISCUSSION_TEMPLATE/`.
GitHub uses a form when its filename matches the slug of a discussion category.
For example, a category named `Skill coverage` should use
`.github/DISCUSSION_TEMPLATE/skill-coverage.yml`.

## Recommended Categories

Create these categories after the repository is pushed and Discussions are
enabled:

| Category | Slug | Template | Use for |
| --- | --- | --- | --- |
| Adoption | `adoption` | `.github/DISCUSSION_TEMPLATE/adoption.yml` | Public-safe pilot reports, local adaptation notes, and adopter feedback. |
| Skill coverage | `skill-coverage` | `.github/DISCUSSION_TEMPLATE/skill-coverage.yml` | Broad discussion of missing repeated HPC workflows before opening a skill request issue. |
| Site adapters | `site-adapters` | `.github/DISCUSSION_TEMPLATE/site-adapters.yml` | Public local policy that might become a site adapter. |
| Review process | `review-process` | `.github/DISCUSSION_TEMPLATE/review-process.yml` | Risk, maturity, reviewer coverage, and governance discussion. |
| Integrations | `integrations` | `.github/DISCUSSION_TEMPLATE/integrations.yml` | Portals, assistants, workflow tools, and downstream registry consumers. |

## When To Move To Issues

Move a discussion into an issue when:

- A skill id, scope, risk level, references, and validation idea are clear.
- A site adapter has public documentation and a bounded set of local notes.
- An integration needs schema, CLI, generated artifact, or governance changes.
- A maturity review, safety review, or RFC has enough evidence to route.
- A maintainer can name the next expected action.

Link the issue back to the discussion so context is preserved.

## Moderation And Privacy

Discussions must stay public-safe. Ask authors to edit or remove private
hostnames, usernames, allocation names, tokens, private storage paths, internal
project identifiers, unpublished operating procedures, and private dataset
details before continuing the thread.

Use [Triage Runbook](TRIAGE_RUNBOOK.md) for weekly intake and
[Safety Model](SAFETY_MODEL.md) when a discussion touches shared-system impact
or privacy-sensitive behavior.
