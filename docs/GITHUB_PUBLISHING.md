# GitHub Publishing Guide

This repository is designed to be published as `hpc-skill-hub`.

## Recommended Repository Settings

- Visibility: public.
- Default branch: `main`.
- License: MIT.
- Topics: `hpc`, `slurm`, `apptainer`, `spack`, `easybuild`, `globus`,
  `nextflow`, `snakemake`, `mpi`, `gpu`, `research-computing`.
- Description: Open registry of validated, reusable skills for HPC workflows.
- Issues: enabled.
- Discussions: enabled once there are external users.
- Wiki: disabled; keep docs in the repository.

## Publish With GitHub CLI

Install and authenticate `gh`, then run from the repository root:

```bash
git branch -M main
git add .
git commit -m "Seed HPC Skill Hub registry"
gh repo create hpc-skill-hub --public --source=. --remote=origin --push \
  --description "Open registry of validated, reusable skills for HPC workflows"
```

## Publish With An Existing Empty GitHub Repository

Create an empty public repository on GitHub, then run:

```bash
git branch -M main
git remote add origin git@github.com:<owner>/hpc-skill-hub.git
git add .
git commit -m "Seed HPC Skill Hub registry"
git push -u origin main
```

## First Release Checklist

- `python3 tools/validate_skills.py` passes.
- README, roadmap, contribution guide, security policy, and governance docs are
  present.
- Every skill has a manifest, README, and at least one example artifact.
- Repository topics and description are set.
- Branch protection requires the validation workflow.
- A pinned issue invites external HPC centers to propose skills and adapters.
