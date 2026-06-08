# Changelog

All notable changes to HPC Skill Hub are tracked here.

This project uses semantic versioning for repository releases. Individual
skills keep their own `version` field in `skills/*/skill.json`.

## Unreleased

- Add a Lustre striping layout planning seed skill for read-only `lfs`
  evidence, review-only `setstripe` planning, and site policy checks before
  changing data-intensive workflow layouts.
- Add a Darshan I/O profile analysis seed skill for turning existing Darshan
  logs into parser output, optional summary commands, and review notes for
  POSIX, MPI-IO, HDF5, and PnetCDF access patterns.
- Add a parallel HDF5 and NetCDF preflight seed skill for MPI-IO wrapper,
  build-configuration, and tiny smoke-test planning.
- Add a Slurm QOS and account limit triage seed skill for read-only
  association, QOS, fairshare, and pending reason evidence.
- Add a Slurm preemption and requeue seed skill for signal-aware jobs,
  restart-safe checkpoint state, and operator-reviewed manual requeue decisions.
- Add an MPI fabric diagnostics seed skill for collecting MPI, UCX,
  libfabric, Open MPI MCA, PMIx, and tiny communication probe evidence.
- Add a Slurm GPU binding diagnostics seed skill for collecting per-task
  `CUDA_VISIBLE_DEVICES`, Slurm GPU variables, and optional vendor telemetry.
- Add a hybrid MPI/OpenMP on Slurm seed skill for aligning MPI task shape,
  `cpus-per-task`, OpenMP thread settings, and CPU binding evidence.
- Add a license-aware Slurm job seed skill for planning `--licenses` requests,
  visible license evidence, and guarded licensed application dry-runs.
- Add an MPI rank binding diagnostics seed skill for collecting Slurm task
  placement, CPU affinity, and topology evidence from small MPI probe jobs.
- Add a Parsl on Slurm seed skill with bounded SlurmProvider and
  HighThroughputExecutor launch planning plus a tiny Python app smoke workflow.
- Extend registry artifact validation to catch stale public collection and site
  adapter counts in launch and proposal materials.
- Add a GitHub Pages homepage command generator and post-launch homepage URL
  check for confirming the published repository links to its generated site.
- Add a post-launch GitHub verification tool for checking published repository
  metadata, labels, milestones, starter issues, workflows, Pages, rulesets, and
  releases.
- Add a proposal evidence report generator for owner handoffs, open-source
  review packets, and ecosystem sponsor discussions.
- Add a reviewed-skill pilot starter issue for routing the first seed skill
  maturity reviews from the local review candidate report.
- Add a review candidate report generator for ranking seed skills that are
  ready for first domain review routing and `reviewed` maturity pilot planning.
- Add a launch evidence report generator for maintainer handoff, launch issues,
  and open-source proposal evidence without taking networked action.
- Add an object storage transfer seed skill with rclone dry-run copy planning,
  guarded sync mode, optional AWS CLI S3 sync planning, bounded transfer
  settings, and validation logs.
- Add a TensorFlow multi-worker on Slurm seed skill with TF_CONFIG launch
  planning, worker index mapping, strategy initialization, and a tiny
  distributed tensor reduction smoke test.
- Add a Hugging Face Accelerate on Slurm seed skill with dry-run launch
  planning, explicit multi-node launch arguments, and a tiny Accelerate tensor
  collective smoke test.
- Add a JAX distributed on Slurm seed skill with dry-run launch planning,
  accelerator visibility checks, distributed initialization, and tiny compiled
  computation smoke-test examples.
- Add a GitHub owner checklist for confirming repository ownership,
  permissions, maintainer queues, public-safety review, and launch decision
  records before networked publication.
- Add a public launch packet that summarizes local readiness, GitHub owner
  prerequisites, launch sequence, outreach targets, and success criteria for
  the first open-source publication.
- Add a public-doc-backed draft NERSC Perlmutter site adapter, covering Slurm
  constraints, QOS notes, Lmod, scratch storage, Globus/DTN transfer guidance,
  and container adaptation notes from public NERSC documentation.
- Add an Open OnDemand Batch Connect skill for reviewable Slurm-backed portal
  app skeletons, and extend safety auditing to cover `.erb` templates.
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
- Add an RStudio on Slurm skill for policy-aware Posit or RStudio sessions on
  scheduled compute allocations.
- Add a Streamlit on Slurm skill for policy-aware Python data apps and AI demos
  on scheduled compute allocations.
- Add a TensorBoard on Slurm skill for policy-aware training monitors on short
  compute allocations.
- Add an IOR and MDTest storage smoke skill for small, policy-aware filesystem
  benchmark evidence on Slurm.
- Expand the technical roadmap with current registry baseline, GitHub launch
  gates, integration tracks, maturity evidence, and open ecosystem milestones.
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

- 85 seed HPC skills covering Slurm, PBS/OpenPBS, LSF, HTCondor, Grid Engine,
  job arrays, dependency chains, pending reason triage, monitoring, resource
  estimation, QOS/account limit evidence, efficiency review, license-aware jobs, failure triage, checkpoint/restart,
  preemption and requeue-safe restart behavior,
  interactive sessions, Open OnDemand Batch Connect templates, notebooks, RStudio, IDE tunnels, OpenMP
  placement, storage triage, Python/R/Julia/MATLAB software environments,
  parallel HDF5/NetCDF preflight, Darshan I/O profile analysis, Lustre
  striping layout planning,
  TensorBoard, Streamlit, Ray, Dask Jobqueue, Parsl, JAX, Hugging Face Accelerate, TensorFlow, mpi4py, containers, containerized MPI, Spack, EasyBuild, object storage, data movement,
  storage smoke benchmarks, CWL/WDL, workflow engines, GPU binding diagnostics, MPI fabric diagnostics, MPI/GPU diagnostics,
  MPI rank binding diagnostics, hybrid MPI/OpenMP layouts,
  AI/HPC launches, bioinformatics workflows including local BLAST+, molecular dynamics including NAMD,
  electronic-structure and quantum chemistry including CP2K, CFD, weather
  workloads, read-only facility operations, and training onboarding.
- 12 curated collections: `core-hpc`, `scheduler-basics`, `software-stacks`,
  `containers`, `workflow-engines`, `data-movement`, `ai-hpc`,
  `gpu-mpi-performance`, `bioinformatics-workflows`, `simulation-workflows`,
  `facility-ops`, and `training-onboarding`.
- 2 site adapters: `example-campus-cluster` and the public-doc-backed draft
  `nersc-perlmutter-public`.
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
  community launch documentation, plus a technical roadmap for public launch,
  registry growth, integrations, and ecosystem stewardship.

### Safety Notes

- User-facing examples default to dry-run, read-only, plan-only, or explicitly
  bounded behavior where practical.
- Medium-risk skills document resource impact, output volume, or side effects.
- Site adapters must contain only public, non-sensitive local policy.
- High-risk or facility-operations skills require explicit maintainer review
  before promotion beyond seed maturity.
