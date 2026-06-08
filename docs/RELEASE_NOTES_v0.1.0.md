# v0.1.0 Release Notes

Status: planned seed release.

## Summary

`v0.1.0` is the first public snapshot of HPC Skill Hub: an open registry of
reusable, reviewable skills for running, debugging, optimizing, and maintaining
HPC workflows.

The release is intended for early adopters, HPC centers, research software
engineers, instructors, and domain reviewers who want to test the skill format,
request missing workflows, or contribute public site adapters.

## Registry Contents

- Skills: 43.
- Collections: 8.
- Site adapters: 1 example adapter.
- Skill maturity: all seed.
- Risk labels: low and medium only in the seed registry.

## Skill Coverage

- Core HPC: Slurm submission, arrays, monitoring, resource estimation,
  checkpoint/restart, failure triage, interactive sessions, Jupyter, OpenMP
  placement, quota triage, and scratch management.
- Software stacks: module debugging, module tree health, compiler/MPI
  compatibility, reproducible run capture, Python virtualenv, Conda/Mamba,
  Apptainer builds and runtime, Spack, and EasyBuild.
- Workflow engines: Nextflow, Snakemake, and nf-core on Slurm.
- Data movement: Globus, rsync, checksum manifests, scratch staging, archive
  preparation, scratch inventory, and filesystem quota triage.
- GPU/MPI performance: MPI sanity checks, GPU sanity checks, PyTorch DDP,
  NCCL diagnostics, GPU memory triage, DeepSpeed, OpenMP placement, and basic
  profiling.
- Bioinformatics: nf-core and GATK workflow patterns with data staging and
  checksum practices.
- Simulation: LAMMPS, GROMACS, OpenFOAM, WRF, MPI launch checks, OpenMP
  placement, restart planning, profiling, and reproducibility.
- Facility operations: read-only Slurm usage reporting, node-health triage, and
  module tree health checks for support teams and facility maintainers.

## Tooling

- `python3 tools/hpc_skill.py validate`
- `python3 tools/hpc_skill.py list`
- `python3 tools/hpc_skill.py search <query>`
- `python3 tools/hpc_skill.py show <skill-id> --examples`
- `python3 tools/hpc_skill.py collections`
- `python3 tools/hpc_skill.py collection <collection-id>`
- `python3 tools/hpc_skill.py adapter <adapter-id>`
- `python3 tools/hpc_skill.py scaffold skill <skill-id>`
- `python3 tools/hpc_skill.py scaffold site-adapter <adapter-id>`
- `python3 tools/hpc_skill.py health`

## GitHub Launch Readiness

- Validation workflow for every pull request and push to `main`.
- GitHub Pages publishing workflow for the generated static registry.
- Dependabot configuration for GitHub Actions and Python packaging.
- Issue templates for bugs, docs, skill requests, site adapters, and safety
  review.
- Pull request template with validation, risk, privacy, and reviewer prompts.
- Repository metadata, labels, and starter ruleset files.
- Seed community issues for launch coordination.
- Command generators for repository setup, labels, starter issues, rulesets,
  and release publication.

## Known Limitations

- Skills are seed maturity and should be reviewed by domain maintainers before
  being treated as field-tested.
- The example site adapter is intentionally non-production.
- GitHub remote creation, label application, ruleset application, and Pages
  activation must be performed in an authenticated GitHub environment.
- No private cluster policy, credentials, allocation names, hostnames, or
  unpublished security procedures should be added to the public registry.

## Release Checks

Before tagging `v0.1.0`, maintainers should confirm:

- `make check` passes locally and in GitHub Actions.
- `registry/index.json`, `registry/health.json`, `docs/SKILL_CATALOG.md`, and
  `docs/REGISTRY_HEALTH.md` are current.
- GitHub repository metadata, labels, and rulesets match `.github/`.
- The generated Pages site is published.
- The first community issue is pinned.
