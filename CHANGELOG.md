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
- Add skill lifecycle guidance for moving community requests through seed,
  review, field testing, maintenance, and deprecation.
- Add ecosystem entry points to the generated static site for adopters,
  contributors, site adapters, integrations, safety review, and RFCs.
- Add GitHub Discussion category forms and setup guidance for adoption, skill
  coverage, site adapters, review process, and integrations.
- Add GitHub milestone metadata and command generator for launch, reviewed-skill
  pilot, integration, adapter, and ecosystem backlog planning.
- Add launch readiness checks for GitHub Discussion forms and milestone
  metadata.
- Add integration guide, integration request template, and starter label for
  downstream registry consumers.
- Add a read-only Slurm efficiency report skill for completed job resource
  review.
- Add a Slurm job dependency chain skill for small multi-stage workflows.
- Add a read-only Slurm pending reason triage skill for queue wait diagnosis.
- Add a PBS submit job skill and scheduler basics collection for OpenPBS/PBS Pro
  starter workloads.
- Add an LSF submit job skill for IBM Spectrum LSF CPU, MPI, and GPU starter
  workloads.
- Add an HTCondor submit job skill for high-throughput single-job, many-task,
  and GPU starter workloads.
- Add a Grid Engine submit job skill for SGE/UGE CPU, parallel environment, and
  array starter workloads.
- Add an Apptainer MPI on Slurm skill for hybrid and bind-model containerized
  MPI launch patterns.
- Add a VS Code Tunnel on Slurm skill for policy-aware IDE sessions on compute
  allocations.
- Add a NAMD on Slurm skill for molecular dynamics jobs with CPU/GPU layout and
  restart planning.
- Add a CP2K on Slurm skill for MPI/OpenMP electronic-structure and molecular
  simulation jobs.
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
- Add a WDL on Slurm skill with miniwdl input, run directory, output JSON, and
  smoke-test controls.

## v0.1.0 - Planned

Initial public seed release.

### Added

- 65 seed HPC skills covering Slurm, PBS/OpenPBS, LSF, HTCondor, Grid Engine,
  job arrays, dependency chains, pending reason triage, monitoring, resource
  estimation, efficiency review, failure triage, checkpoint/restart,
  interactive sessions, notebooks, IDE tunnels, OpenMP
  placement, storage triage, Python/R/Julia/MATLAB software environments,
  Ray, Dask Jobqueue, mpi4py, containers, containerized MPI, Spack, EasyBuild, data movement,
  CWL/WDL, workflow engines, MPI/GPU diagnostics, AI/HPC launches, bioinformatics
  workflows including local BLAST+, molecular dynamics including NAMD,
  electronic-structure and quantum chemistry including CP2K, CFD, weather
  workloads, read-only facility operations, and training onboarding.
- 12 curated collections: `core-hpc`, `scheduler-basics`, `software-stacks`,
  `containers`, `workflow-engines`, `data-movement`, `ai-hpc`,
  `gpu-mpi-performance`, `bioinformatics-workflows`, `simulation-workflows`,
  `facility-ops`, and `training-onboarding`.
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
