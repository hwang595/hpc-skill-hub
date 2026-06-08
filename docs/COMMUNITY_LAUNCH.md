# Community Launch

Use this guide after the repository is pushed to GitHub and the validation
workflow is green. It gives maintainers ready-to-use text and a small launch
sequence for opening the project as an ecosystem.

## Repository Metadata

Use `.github/repository.json` as the source of truth for repository name,
description, topics, visibility, and feature settings.

Use `.github/labels.json` as the source of truth for starter labels. Create or
update these labels before inviting external contributors so issue templates and
triage labels line up.

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
and simulation workloads.

We are looking for:

- Skill requests for repeated HPC support tasks.
- Public site adapters for campus, training, national facility, or cloud HPC
  environments.
- Domain reviewers for schedulers, containers, software stacks, data movement,
  AI/HPC, bioinformatics, molecular dynamics, CFD, climate/weather, and
  facility operations.
- Feedback on schema fields, risk labels, and review policy.

Please avoid sharing private hostnames, usernames, allocation names, internal
project identifiers, unpublished security procedures, or private dataset paths.
Use the issue templates so maintainers can triage requests quickly.
```

Labels:

```text
help-wanted, good-first-issue, governance
```

## First Discussion Prompts

- Adoption: "What would your center need before recommending HPC Skill Hub to
  users?"
- Skill coverage: "Which repeated support tasks are missing from the first
  batch?"
- Site adapters: "What public local policy belongs in a site adapter, and what
  must stay private?"
- Review process: "What evidence should be required before promoting a skill
  from seed to reviewed?"

## Launch Checklist

- Push `main` to a public GitHub repository.
- Confirm the `Validate` workflow passes.
- Enable GitHub Pages from Actions and confirm `Publish Pages` succeeds.
- Apply repository description, topics, and feature settings from
  `.github/repository.json`.
- Apply labels from `.github/labels.json`.
- Pin the first community issue.
- Link the generated Pages site in the repository homepage.
- Invite the first three to five domain reviewers.
