# GitHub Repository Setup

Use this checklist after the local repository is pushed to a public GitHub
repository. It turns the seed project into a maintainable open-source registry.

## Repository Basics

- Name: `hpc-skill-hub`.
- Visibility: public.
- Default branch: `main`.
- Description: Open registry of validated, reusable skills for HPC workflows.
- Topics: `hpc`, `slurm`, `apptainer`, `spack`, `easybuild`, `globus`,
  `nextflow`, `snakemake`, `mpi`, `gpu`, `research-computing`.
- Issues: enabled.
- Discussions: enabled once external users start asking design or adoption
  questions.
- Wiki: disabled; keep documentation versioned in this repository.

## Branch Protection

Create a branch protection rule or ruleset for `main`:

- Require pull requests before merging.
- Require the validation workflow to pass.
- Require branches to be up to date before merging when possible.
- Block force pushes.
- Block branch deletion.
- Require at least one review for normal changes.
- Require a domain maintainer review for high-risk skills, facility operations
  guidance, or shared-system behavior.

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

Create these starter labels:

- `skill-request`
- `site-adapter`
- `bug`
- `documentation`
- `schema-change`
- `safety-review`
- `high-risk-skill`
- `governance`
- `good-first-issue`
- `help-wanted`
- `dependencies`
- `ci`
- `python`

## CODEOWNERS

Replace the placeholder `.github/CODEOWNERS` file with real GitHub usernames or
teams once the repository has maintainers. At minimum:

- Route all changes to a small maintainer group.
- Route `skills/` changes to registry maintainers.
- Route high-risk domains to domain maintainers with production HPC experience.
- Route schemas and tooling to maintainers comfortable with compatibility.

## First Public Issue

Pin an issue that invites the community to propose:

- Missing first-batch skills.
- Public site adapters for campus, national lab, cloud, or training clusters.
- Compatibility gaps in the skill schema.
- Safety or review requirements that should become policy.

## First Release

Cut `v0.1.0` after:

- `make check` passes on GitHub Actions.
- The generated registry site is published.
- At least one external contributor can validate a skill locally.
- Maintainers agree the skill schema is stable enough for early adopters.
