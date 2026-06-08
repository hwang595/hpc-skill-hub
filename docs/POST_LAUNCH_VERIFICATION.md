# Post-Launch Verification

Use this checklist after `main` is pushed to the public GitHub repository,
labels and milestones are applied, starter issues are opened, Pages is enabled,
the Pages URL is linked from the repository homepage, rulesets are applied, and
the first release is published.

The verification tool is read-only. It checks the public GitHub repository with
`gh` and does not create repositories, edit settings, open issues, apply
rulesets, or publish releases.

## Run Verification

From an authenticated GitHub CLI environment:

```bash
python3 tools/github_post_launch_check.py --repo <owner>/hpc-skill-hub --version v0.2.0
```

For machine-readable output:

```bash
python3 tools/github_post_launch_check.py --repo <owner>/hpc-skill-hub --json
```

To preview the read-only commands before running them:

```bash
python3 tools/github_post_launch_check.py --repo <owner>/hpc-skill-hub --dry-run
```

Use `--strict` in CI or release checklists when warnings should fail the
verification gate.

## What It Checks

- `origin` remote points at the target GitHub repository when configured.
- GitHub CLI is available for remote checks.
- Repository metadata matches `.github/repository.json`.
- Labels from `.github/labels.json` exist.
- Milestones from `.github/milestones.json` exist.
- Starter issues from `.github/seed_issues.json` exist.
- Workflows under `.github/workflows/` exist on GitHub.
- GitHub Pages is configured.
- The repository homepage points at the GitHub Pages URL.
- The starter `Protect main` ruleset exists and is active.
- The release tag, such as `v0.1.0`, exists as a GitHub release.

## Interpreting Results

- `OK`: the expected published state is present.
- `WARN`: the check needs human follow-up, or local state is not yet wired to
  the published repository.
- `FAIL`: a published repository setting, issue, ruleset, workflow, Pages
  setup, homepage URL, label, milestone, or release is missing or inconsistent.

Expected warnings before the repository is fully published include missing
`origin` or missing `gh`. After launch, those warnings should be resolved or
documented in the launch issue.

## When To Run

Run this check after:

1. `gh repo create` or manual repository creation.
2. `Validate`, `Package`, and `Publish Pages` workflows are green.
3. `python3 tools/github_homepage.py --repo <owner>/hpc-skill-hub` has been
   reviewed and its printed homepage command has been run.
4. Labels, milestones, starter issues, and discussion categories are created.
5. The `Protect main` ruleset is applied.
6. The `v0.1.0` release is published.

Attach the verification report to the launch issue or release handoff so the
first public state is reviewable later.
