# Community Launch

Use this guide after the repository is pushed to GitHub and the validation and
package workflows are green. It gives maintainers ready-to-use text and a small
launch sequence for opening the project as an ecosystem.

Use [Public Launch Packet](PUBLIC_LAUNCH_PACKET.md) when sharing the current
local readiness state and first GitHub actions with a repository owner,
maintainer team, or sponsoring organization.

## Repository Metadata

Use `.github/repository.json` as the source of truth for repository name,
description, topics, visibility, and feature settings.

Use `.github/labels.json` as the source of truth for starter labels. Create or
update these labels before inviting external contributors so issue templates and
triage labels line up. Use [Triage Runbook](TRIAGE_RUNBOOK.md) for the first
week of issue and pull request intake after launch.

Use `.github/milestones.json` as the source of truth for launch and ecosystem
planning milestones. Use [GitHub Milestones](GITHUB_MILESTONES.md) to group
seed launch work, reviewed-skill pilots, integrations, adapters, and backlog
requests.

## Starter Issues

Use `.github/seed_issues.json` and `.github/seed-issues/*.md` as the source of
truth for launch issues. These include the pinned community call, public site
adapter recruitment, domain reviewer recruitment, the first reviewed-skill
pilot, and next-wave skill requests. After labels are created, inspect the
commands:

```bash
python3 tools/github_issues.py --repo <owner>/hpc-skill-hub --include-pin-notes
```

Run the printed `gh issue create` commands, then pin the issue marked in the
printed note.

## First Pinned Issue

Title:

```text
Community call: skills, site adapters, and domain reviewers wanted
```

Body:

```markdown
HPC Skill Hub is a seed registry of reusable, reviewable skills for common HPC
workflows. The first batch covers Slurm, storage, software stacks, containers,
workflow engines, data movement, MPI/GPU diagnostics, AI/HPC, bioinformatics,
simulation workloads, and read-only facility operations.

We are looking for:

- Skill requests for repeated HPC support tasks.
- Public site adapters for campus, training, national facility, or cloud HPC
  environments.
- Domain reviewers for schedulers, containers, software stacks, data movement,
  AI/HPC, bioinformatics, molecular dynamics, CFD, climate/weather, and
  facility operations.
- Feedback on schema fields, risk labels, and review policy.
- Maturity review evidence for skills that should move from seed to reviewed or
  field-tested.
- Adoption reports from centers, research groups, tool maintainers, and
  training programs that tried the seed registry.
- Integration requests from portals, assistants, workflow tools, and other
  downstream consumers.

Please avoid sharing private hostnames, usernames, allocation names, internal
project identifiers, unpublished security procedures, or private dataset paths.
Use the issue templates so maintainers can triage requests quickly.
```

Labels:

```text
help-wanted, good-first-issue, governance
```

## First Discussion Prompts

Use [GitHub Discussions](GITHUB_DISCUSSIONS.md) to create categories matching
the discussion forms under `.github/DISCUSSION_TEMPLATE/`.

- Adoption: "What would your center need before recommending HPC Skill Hub to
  users?"
- Skill coverage: "Which repeated support tasks are missing from the first
  batch?"
- Site adapters: "What public local policy belongs in a site adapter, and what
  must stay private?"
- Review process: "What evidence should be required before promoting a skill
  from seed to reviewed?"
- Adoption reports: "What worked during a 30-60-90 day pilot, and what needed
  a site adapter or new skill?"
- Integrations: "What metadata would a portal, assistant, or workflow tool need
  to consume this registry safely?"

## Launch Checklist

- Push `main` to a public GitHub repository.
- Confirm the `Validate` and `Package` workflows pass.
- Enable GitHub Pages from Actions and confirm `Publish Pages` succeeds.
- Apply repository description, topics, and feature settings from
  `.github/repository.json`.
- Apply labels from `.github/labels.json`.
- Create milestones from `.github/milestones.json`.
- Create starter issues from `.github/seed_issues.json`.
- Run `python3 tools/review_candidates.py --limit 12` and use the reviewed-skill
  pilot issue to route the first maturity reviews.
- Pin the first community issue.
- Create the recommended Discussion categories and confirm their forms load.
- Run the first weekly triage loop from [Triage Runbook](TRIAGE_RUNBOOK.md).
- Run `python3 tools/github_homepage.py --repo <owner>/hpc-skill-hub` and use
  the printed command to link the generated Pages site in the repository
  homepage.
- Invite the first three to five domain reviewers using
  [Domain Reviewers](DOMAIN_REVIEWERS.md).
