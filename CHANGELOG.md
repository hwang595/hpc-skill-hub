# Changelog

All notable changes to HPC Skill Hub are tracked here.

This project uses semantic versioning for repository releases. Individual
skills keep their own `version` field in `skills/*/skill.json`.

## Unreleased

- Prepare the seed registry for public GitHub launch, including repository
  metadata, labels, rulesets, issue templates, pull request templates, Pages
  publishing, seed community issues, and governance docs.
- Add the first `facility-ops` collection and a read-only Slurm usage reporting
  skill for support teams.
- Add a read-only Slurm node-health triage skill for facility operations.
- Add a read-only module-tree health check skill for software-stack and
  facility operations support.
- Add a training and onboarding collection with a workshop preflight and reset
  checklist skill.
- Add maturity review guidance and issue template for promoting seed skills.
- Add adopter playbook and adoption report issue template for public pilot
  feedback.
- Add local launch readiness audit for GitHub publishing preparation.
- Add support and citation metadata for public project use.
- Add review routing guidance and CODEOWNERS launch checklist for maintainer
  assignment.
- Add triage runbook and starter labels for public issue and pull request
  intake.
- Add integration guide, integration request template, and starter label for
  downstream registry consumers.
- Add a read-only Slurm efficiency report skill for completed job resource
  review.
- Add a Slurm job dependency chain skill for small multi-stage workflows.
- Add a read-only Slurm pending reason triage skill for queue wait diagnosis.
- Add an Rscript on Slurm skill for batch R workloads with explicit package
  library and output controls.
- Add a Julia on Slurm skill for batch Julia workloads with explicit depot,
  project, and thread settings.
- Add a MATLAB batch on Slurm skill for non-interactive MATLAB workloads with
  explicit logging and license notes.
- Add a mpi4py on Slurm skill for Python MPI workloads with matching MPI module
  and Python environment checks.
- Add a Dask Jobqueue on Slurm skill with dry-run worker job script review and
  bounded worker scaling.
- Add a Ray on Slurm skill with explicit head node selection, resource bounds,
  launch records, and smoke test controls.
- Add a `containers` collection for Apptainer builds, runtime execution, GPU
  checks, data staging, checksums, and reproducible run capture.
- Add an `ai-hpc` collection for distributed AI launch, validation,
  troubleshooting, data staging, and reproducibility workflows.
- Add a BLAST on Slurm skill with local database creation, bounded output
  controls, and a tiny FASTA smoke test.
- Add a Quantum ESPRESSO on Slurm skill with MPI sizing, pseudopotential checks,
  scratch paths, restart planning, and a PWscf input template.
- Add a CWL on Slurm skill with cwltool cache, output, temporary directory, and
  smoke-test controls.

## v0.1.0 - Planned

Initial public seed release.

### Added

- 56 seed HPC skills covering Slurm, job arrays, dependency chains, pending
  reason triage, monitoring, resource estimation, efficiency review, failure
  triage, checkpoint/restart, interactive sessions, notebooks, OpenMP
  placement, storage triage, Python/R/Julia/MATLAB software environments,
  Ray, Dask Jobqueue, mpi4py, containers, Spack, EasyBuild, data movement,
  CWL, workflow engines, MPI/GPU diagnostics, AI/HPC launches, bioinformatics
  workflows including local BLAST+, molecular dynamics, electronic-structure,
  CFD, weather workloads, read-only facility operations, and training
  onboarding.
- 11 curated collections: `core-hpc`, `software-stacks`, `containers`,
  `workflow-engines`, `data-movement`, `ai-hpc`, `gpu-mpi-performance`,
  `bioinformatics-workflows`, `simulation-workflows`, `facility-ops`, and
  `training-onboarding`.
- 1 example public site adapter: `example-campus-cluster`.
- Machine-readable registry index and health reports.
- Installable `hpc-skill` CLI for discovery, validation, scaffolding,
  collections, site adapters, and registry health.
- Static site generation for GitHub Pages.
- JSON schemas for skills, collections, and site adapters.
- GitHub Actions validation, Pages publishing, Dependabot, issue templates,
  pull request templates, starter labels, repository metadata, and starter
  `main` branch ruleset configuration.
- Seed community issues and command generators for launching the public
  contribution queue.
- Governance, safety, release, maintainer handoff, authoring, publishing, and
  community launch documentation.

### Safety Notes

- User-facing examples default to dry-run, read-only, plan-only, or explicitly
  bounded behavior where practical.
- Medium-risk skills document resource impact, output volume, or side effects.
- Site adapters must contain only public, non-sensitive local policy.
- High-risk or facility-operations skills require explicit maintainer review
  before promotion beyond seed maturity.
