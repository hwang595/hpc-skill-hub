# GitHub Repository Setup

Use this checklist after the local repository is pushed to a public GitHub
repository. It turns the seed project into a maintainable open-source registry.

## Repository Basics

Use `.github/repository.json` as the source of truth for repository name,
visibility, default branch, description, topics, and feature settings.

To inspect the full ordered publication plan before making any networked GitHub
changes, run:

```bash
python3 tools/github_publish_plan.py --owner <owner> --run-check
```

After installing and authenticating GitHub CLI, inspect the repository setup
commands:

```bash
python3 tools/github_repo.py --owner <owner>
```

Run the printed commands when they look correct.

## Branch Protection

Use `.github/rulesets/main.json` as the source of truth for the starter `main`
branch ruleset. It requires pull requests, one approving review, the `skills`
and `wheel` CI checks, up-to-date checks, and blocks branch deletion and force
pushes.

After the first push and successful `Validate` and `Package` workflow runs,
inspect the ruleset command:

```bash
python3 tools/github_rulesets.py --repo <owner>/hpc-skill-hub
```

Run the printed command when it looks correct. If GitHub shows the required
status check under a different context name, update `.github/rulesets/main.json`
before applying it.

## GitHub Pages

- Set Pages source to GitHub Actions.
- Confirm the `Publish Pages` workflow succeeds after the first push.
- Link the generated site from the repository homepage when the URL is
  available.

## Security Features

- Enable private vulnerability reporting.
- Enable Dependabot alerts.
- Enable Dependabot security updates.
- Enable secret scanning if it is available for the repository.
- Keep security reports out of public issues until sensitive details are
  removed.

## Labels

Create or update labels from `.github/labels.json`. The test suite checks that
issue templates only reference labels defined there.

After installing and authenticating GitHub CLI, inspect the label commands:

```bash
python3 tools/github_labels.py --repo <owner>/hpc-skill-hub
```

Run the printed commands when they look correct.

## Starter Issues

Create launch issues from `.github/seed_issues.json` after labels exist:

```bash
python3 tools/github_issues.py --repo <owner>/hpc-skill-hub --include-pin-notes
```

Run the printed commands when they look correct, then pin the issue identified
by the printed note.

## CODEOWNERS

Replace the placeholder `.github/CODEOWNERS` file with real GitHub usernames or
teams once the repository has maintainers. Use
[Review Routing](REVIEW_ROUTING.md) as the policy source. At minimum:

- Route all changes to a small maintainer group.
- Route `skills/` changes to registry maintainers.
- Route high-risk domains to domain maintainers with production HPC experience.
- Route schemas and tooling to maintainers comfortable with compatibility.

## First Public Issue

Use [Community Launch](COMMUNITY_LAUNCH.md) for a ready-to-pin first issue and
starter discussion prompts.

## First Release

Cut `v0.1.0` after:

- `Validate` and `Package` pass on GitHub Actions.
- The generated registry site is published.
- At least one external contributor can validate a skill locally.
- Maintainers agree the skill schema is stable enough for early adopters.
