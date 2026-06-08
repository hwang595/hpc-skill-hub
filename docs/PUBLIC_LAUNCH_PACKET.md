# Public Launch Packet

This packet summarizes what is ready locally and what a GitHub owner must do
to publish HPC Skill Hub as an open-source seed registry.

## Current Local Baseline

- Repository name: `hpc-skill-hub`.
- Seed skills: 73.
- Curated collections: 12.
- Site adapters: 2, including one example adapter and one public-doc-backed
  NERSC Perlmutter draft adapter.
- Release target: `v0.1.0`.
- Local release gate: `make check`.
- Current local status: ready except for external GitHub repository creation,
  `origin` configuration, and authenticated `gh` CLI execution.

## What Is Ready To Publish

- Portable skill manifests, READMEs, examples, tests, references, risk labels,
  and maturity metadata under `skills/`.
- Curated adoption paths under `collections/`.
- Public local-policy adapter examples under `site-adapters/`.
- JSON schemas under `schemas/`.
- Generated registry index, health report, compatibility tables, package data,
  release manifest, and static site output.
- GitHub workflows for validation, package checks, and Pages publishing.
- GitHub issue templates, discussion templates, labels, milestones, repository
  metadata, starter ruleset, and seed community issues.
- Governance, safety, contributor, review, maturity, release, adoption, and
  integration documentation.

## External Launch Prerequisites

The publishing environment needs:

- GitHub owner or organization for `<owner>/hpc-skill-hub`.
- Authenticated GitHub CLI.
- Permission to create the repository, edit settings, enable Pages and
  Discussions, create labels and milestones, apply rulesets, open starter
  issues, and publish releases.
- Maintainer GitHub handles or teams for replacing placeholder CODEOWNERS
  ownership.
- Completed [GitHub Owner Checklist](GITHUB_OWNER_CHECKLIST.md), including
  owner identity, launch maintainer, release owner, permissions, and public
  safety review.

## First Commands

Run these from the repository root in the authenticated environment:

```bash
python3 tools/launch_readiness.py --owner <owner> --run-check
python3 tools/github_publish_plan.py --owner <owner> --run-check
```

If the plan looks correct, follow the printed commands in order. The first
networked step is:

```bash
git branch -M main
gh repo create <owner>/hpc-skill-hub --public --source=. --remote=origin --description 'Open registry of validated, reusable skills for HPC workflows.' --push
```

Use [GitHub Publishing Guide](GITHUB_PUBLISHING.md) and
[GitHub Repository Setup](GITHUB_REPOSITORY_SETUP.md) for the detailed setup
steps.

## Launch Sequence

1. Create the public repository and push `main`.
2. Confirm `Validate` and `Package` workflows pass.
3. Apply repository metadata, topics, labels, and milestones from `.github/`.
4. Enable GitHub Pages from Actions and confirm `Publish Pages` succeeds.
5. Enable Discussions and create the documented discussion categories.
6. Open starter community issues and pin the community call issue.
7. Apply the `main` branch ruleset after workflow status checks are visible.
8. Invite initial domain reviewers and site-adapter reviewers.
9. Tag and publish `v0.1.0` with `registry/releases/v0.1.0.json` attached.

## First Outreach Targets

- HPC centers that can review public site adapter patterns.
- Research software engineering groups that maintain training material.
- Workflow-engine maintainers for Nextflow, Snakemake, CWL, WDL, Dask, and Ray.
- AI/HPC support teams that repeatedly help users with GPUs, distributed
  training, TensorBoard, Streamlit, and storage staging.
- Domain reviewers for bioinformatics, simulation, MPI, storage, containers,
  schedulers, and facility operations.

## Success Criteria For Launch

- Public repository exists and `origin` points to it.
- `Validate`, `Package`, and `Publish Pages` workflows are green.
- Generated registry site is linked from the repository homepage.
- Labels, milestones, issue templates, discussion templates, and starter issues
  are live.
- The first pinned issue invites skills, site adapters, adoption reports, and
  domain reviewers.
- At least one external reviewer can run `make check` locally and inspect a
  skill, collection, and site adapter through the CLI.

## Do Not Publish

- Private hostnames, usernames, allocation names, tickets, project ids, tokens,
  internal paths, non-public security procedures, or private cluster policy.
- Exact site limits that are likely to drift unless linked to public
  documentation or represented as placeholders.
- High-risk operational automation without explicit maintainer and safety
  review.
