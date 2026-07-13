# Skill Lifecycle

This document describes how a community idea becomes a maintained HPC Skill Hub
skill. Use it with the [Skill Authoring Guide](SKILL_AUTHORING_GUIDE.md),
[Triage Runbook](TRIAGE_RUNBOOK.md), [Review Routing](REVIEW_ROUTING.md), and
[Maturity Review](MATURITY_REVIEW.md).

## Lifecycle Stages

| Stage | Owner | Evidence | Exit criteria |
| --- | --- | --- | --- |
| Request | Contributor or adopter | Skill request, adoption report, or integration request | Scope, users, risk, public references, and validation idea are clear. |
| Shaping | Contributor with maintainer input | Issue discussion or draft pull request | Skill id, collection fit, examples, and site assumptions are agreed. |
| Seed | Contributor | Manifest, README, examples, generated registry files, and passing checks | Skill is discoverable, public-safe, and conservative enough for early adopters. |
| Reviewed | Domain maintainer | Maturity review issue and linked pull request | Domain assumptions, risk level, examples, and references have been reviewed. |
| Field-tested | Adopter and domain maintainer | Public-safe adoption report or site adapter evidence | The skill has been tried or reviewed in a real environment without private details. |
| Maintained | Named maintainer or group | Ownership note, review cadence, and current checks | A maintainer accepts responsibility for periodic review and user feedback. |
| Deprecated | Maintainer | Deprecation note, replacement path, and changelog entry | Users have a clear migration path or reason to stop using the skill. |

All new skills start at `seed` maturity unless a maintainer explicitly approves
a higher level through the maturity review process.

## Intake Lanes

Use the smallest public issue type that captures the work:

- Skill request: a new repeated HPC task belongs in the registry.
- Site adapter request: a public center or training environment needs local
  policy notes without forking core skills.
- Integration request: a portal, assistant, workflow tool, or package wants to
  consume registry metadata.
- Adoption report: someone tried a skill, collection, adapter, or workflow and
  can share public-safe feedback.
- Safety review: risk, privacy, shared-system impact, or high-risk behavior is
  the main question.
- RFC proposal: the proposal changes schemas, validation, governance, risk,
  maturity, site adapter policy, or downstream compatibility.

If a request mixes lanes, triage the smallest concrete contribution first and
link follow-up issues for the rest.

## Shaping Checklist

Before implementation starts, confirm:

- The skill id is lowercase kebab-case and names the task, not one site.
- Target users and expected environment are specific enough to review.
- The proposed risk level matches the most powerful command or recommendation.
- Public references exist for the scheduler, runtime, tool, or workflow.
- Examples can be inspected without private cluster access.
- Resource requests are conservative and bounded.
- Site-specific policy belongs in a site adapter instead of the portable skill.
- The skill fits at least one existing collection or justifies a collection
  update.

## Seed Implementation Gate

A seed skill pull request should include:

- `skills/<skill-id>/skill.json`
- `skills/<skill-id>/README.md`
- At least one example artifact under `skills/<skill-id>/examples/`
- Risk, safety, assumptions, and cleanup notes in the README
- Public references in the manifest
- Collection updates when the skill is part of an adoption path
- Refreshed generated registry artifacts

Run:

```bash
python3 tools/hpc_skill.py validate --skill <skill-id>
python3 tools/build_index.py
python3 tools/build_health.py
python3 tools/build_compatibility.py
python3 tools/build_package_data.py
python3 tools/validate_registry_artifacts.py
make check
```

## Review And Promotion

Promotion from `seed` to `reviewed`, `field-tested`, or `maintained` requires a
maturity review issue. The linked pull request should update the manifest,
generated registry files, and release notes or changelog when appropriate.
For release-scoped pilots, it should also update the source bundle under
`reviews/<release>/` and pass `hpc-skill review check`.

Reviewers should check:

- The examples match the declared risk level.
- The README explains costs, side effects, assumptions, and cleanup.
- Commands avoid private hostnames, accounts, usernames, tokens, and paths.
- References are public and current enough for the claimed maturity.
- Any site-specific behavior is represented through a site adapter.
- The skill still passes local validation and registry artifact checks.

Field-test evidence can describe an environment type, public documentation,
what was run or reviewed, and what changed because of the test. It must not
include private hostnames, allocation names, internal project identifiers,
private paths, tickets, or unpublished operating procedures.

## Deprecation

Deprecate a skill when it is unsafe, obsolete, replaced by a better workflow, or
no longer has maintainable public references. A deprecation pull request should:

- Explain why the skill is deprecated.
- Link a replacement skill or external public reference when one exists.
- Keep the skill discoverable long enough for users to migrate.
- Update collections, generated registry artifacts, release notes, and the
  changelog.
- Avoid deleting examples unless they create a safety or privacy problem.

## Maintainer Operating Loop

On a regular maintenance pass:

1. Triage new requests into the intake lanes above.
2. Mark well-scoped starter work as `good-first-issue` or `help-wanted`.
3. Route domain or high-risk changes using review routing.
4. Ask for safety review when a change may expose private policy or affect
   shared systems.
5. Invite adoption reports after a skill, collection, or adapter is tried.
6. Promote or deprecate skills only when the public evidence supports it.

This keeps the registry open to new contributors while preserving the review
discipline needed for shared HPC environments.
