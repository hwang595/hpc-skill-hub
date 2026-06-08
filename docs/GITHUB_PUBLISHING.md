# GitHub Publishing Guide

This repository is designed to be published as `hpc-skill-hub`.

After the first push, use [GitHub Repository Setup](GITHUB_REPOSITORY_SETUP.md)
to configure branch protection, Pages, security features, labels, and
maintainer ownership.

Use [Community Launch](COMMUNITY_LAUNCH.md) for the first pinned issue,
discussion prompts, and public adopter invitation.

Use [Triage Runbook](TRIAGE_RUNBOOK.md) for the first public issue and pull
request intake loop after launch.

Use [Public Launch Packet](PUBLIC_LAUNCH_PACKET.md) as a concise handoff for
the GitHub owner or sponsoring organization before running networked commands.

Use [GitHub Owner Checklist](GITHUB_OWNER_CHECKLIST.md) to confirm the owner
identity, repository permissions, maintainer map, and public-safety review
before pushing the seed repository.

## Recommended Repository Settings

Use `.github/repository.json` as the source of truth for repository settings
and `.github/labels.json` as the source of truth for starter labels.

## Publish With GitHub CLI

Install and authenticate `gh`, then run from the repository root:

```bash
python3 tools/github_publish_plan.py --owner <owner>
python3 tools/launch_readiness.py --owner <owner>
python3 tools/launch_evidence.py --owner <owner>
python3 tools/review_candidates.py --limit 12
python3 tools/github_repo.py --owner <owner>
python3 tools/github_labels.py --repo <owner>/hpc-skill-hub
python3 tools/github_milestones.py --repo <owner>/hpc-skill-hub
python3 tools/github_issues.py --repo <owner>/hpc-skill-hub --include-pin-notes
```

Review the printed commands before running them. They are generated from the
versioned metadata files so future edits stay in one place.

For a single ordered publication plan that includes local readiness, repository
creation, labels, milestones, starter issues, branch rulesets, and the first
release commands, run:

```bash
python3 tools/github_publish_plan.py --owner <owner> --run-check
python3 tools/launch_evidence.py --owner <owner> --run-check
python3 tools/review_candidates.py --limit 12
```

These commands are read-only: the publish plan prints commands and current
local readiness, while the evidence report creates a pasteable Markdown or JSON
summary for the launch issue or owner handoff. The review candidate report
prints a local first-review queue for domain reviewer recruitment. They do not
create a repository, push commits, edit settings, open issues, or cut a
release.

## Publish With An Existing Empty GitHub Repository

Create an empty public repository on GitHub. If this checkout already has local
commits, connect it directly and push the existing history:

```bash
git branch -M main
git remote add origin git@github.com:<owner>/hpc-skill-hub.git
git push -u origin main
```

Only run `git add` and `git commit` first if you are publishing from an
uncommitted export rather than this maintained local repository.

## First Release Checklist

- `make check` passes locally and the `Validate` workflow passes in GitHub
  Actions.
- The `Package` workflow builds source and wheel distributions, checks package
  metadata, and smoke tests the installed CLI outside the checkout.
- README, roadmap, contribution guide, security policy, and governance docs are
  present.
- Generated skill catalog, registry health, and compatibility tables are
  current.
- Support and citation metadata are present.
- Changelog and release notes are present.
- Every skill has a manifest, README, and at least one example artifact.
- Registry index, registry health, generated catalog docs, compatibility
  tables, and release manifest are current.
- Repository topics and description are set.
- Repository metadata matches `.github/repository.json`.
- Labels are created from `.github/labels.json`.
- Milestones are created from `.github/milestones.json`.
- GitHub Discussions categories match `.github/DISCUSSION_TEMPLATE/` and
  [GitHub Discussions](GITHUB_DISCUSSIONS.md).
- `python3 tools/launch_readiness.py` reports no local `FAIL` entries.
- `python3 tools/launch_evidence.py --owner <owner> --run-check` produces a
  launch evidence report with no `FAIL` readiness checks.
- `python3 tools/review_candidates.py --limit 12` prints the first reviewed
  skill pilot queue for domain reviewer recruitment.
- `python3 tools/github_repo.py --owner <owner>` prints the expected repository
  creation and metadata commands.
- `python3 tools/github_labels.py --repo <owner>/hpc-skill-hub` prints the
  expected label commands.
- `python3 tools/github_milestones.py --repo <owner>/hpc-skill-hub` prints the
  expected milestone commands.
- `python3 tools/github_issues.py --repo <owner>/hpc-skill-hub --include-pin-notes`
  prints the expected starter issue commands.
- `python3 tools/github_rulesets.py --repo <owner>/hpc-skill-hub` prints the
  expected branch ruleset command after the first `Validate` and `Package`
  workflow runs.
- `python3 tools/github_release.py v0.1.0 --repo <owner>/hpc-skill-hub` prints
  the expected release commands and manifest attachment after Pages and Actions
  are green.
- `python3 tools/github_publish_plan.py --owner <owner> --run-check` prints the
  expected end-to-end publication plan.
- The GitHub owner has completed [GitHub Owner Checklist](GITHUB_OWNER_CHECKLIST.md).
- Branch protection requires the validation and package workflows.
- GitHub Pages is enabled with the `Publish Pages` workflow.
- GitHub Discussions is enabled and seeded with adoption, skill coverage, site
  adapter, review process, and integration categories.
- Dependabot, issue templates, and pull request templates are present.
- A pinned issue invites external HPC centers to propose skills and adapters.
- A triage owner knows how to apply `needs-triage` and
  `needs-domain-review`.

## Publish GitHub Pages

After the repository is pushed to GitHub:

1. Open repository settings.
2. Go to Pages.
3. Set source to GitHub Actions.
4. Run the `Publish Pages` workflow, or push a change to `registry/index.json`
   or `tools/build_site.py`.

The site is generated by:

```bash
python3 tools/build_site.py --output site/index.html
```
