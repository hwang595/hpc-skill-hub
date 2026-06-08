# Public Launch Packet

This packet summarizes what is ready locally and what a GitHub owner must do
to publish HPC Skill Hub as an open-source seed registry.

## Current Local Baseline

- Repository name: `hpc-skill-hub`.
- Seed skills: 90.
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
- A reviewed-skill pilot starter issue for turning the first review candidate
  report into public maturity-review work.
- Governance, safety, contributor, review, maturity, release, adoption, and
  integration documentation.
- Local review candidate reporting for the first `reviewed` skill pilot queue.
- Local proposal evidence reporting for owner handoffs, OSPO reviews, and
  open-ecosystem sponsor discussions.

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
python3 tools/launch_evidence.py --owner <owner> --run-check
python3 tools/proposal_evidence.py --owner <owner> --run-check
python3 tools/review_candidates.py --limit 12
python3 tools/github_homepage.py --repo <owner>/hpc-skill-hub
python3 tools/github_post_launch_check.py --repo <owner>/hpc-skill-hub --dry-run
```

Attach the launch evidence report to the launch issue or owner handoff. If the
publish plan looks correct, attach the proposal evidence report to any
sponsoring-organization or open-source review packet, use the review candidate
report to seed first domain reviewer assignments, then follow the printed
commands in order. The first networked step is:

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
5. Link the generated Pages URL from the repository homepage.
6. Enable Discussions and create the documented discussion categories.
7. Open starter community issues and pin the community call issue.
8. Apply the `main` branch ruleset after workflow status checks are visible.
9. Generate the review candidate report and invite initial domain reviewers and
   site-adapter reviewers through the reviewed-skill pilot and domain reviewer
   starter issues.
10. Tag and publish `v0.1.0` with `registry/releases/v0.1.0.json` attached.
11. Run post-launch verification and attach the report to the launch issue.

## First Outreach Targets

- HPC centers that can review public site adapter patterns.
- Research software engineering groups that maintain training material.
- Workflow-engine maintainers for Nextflow, Snakemake, CWL, WDL, Dask, Parsl,
  and Ray.
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
- Post-launch verification reports no `FAIL` entries, or every remaining
  warning or failure has a documented owner and follow-up issue.

## Do Not Publish

- Private hostnames, usernames, allocation names, tickets, project ids, tokens,
  internal paths, non-public security procedures, or private cluster policy.
- Exact site limits that are likely to drift unless linked to public
  documentation or represented as placeholders.
- High-risk operational automation without explicit maintainer and safety
  review.
