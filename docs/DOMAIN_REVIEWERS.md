# Domain Reviewers

HPC Skill Hub needs domain reviewers before seed skills can become reviewed,
field-tested, or maintained. This document turns the broad review routing rules
into a public recruitment and ownership map.

## Reviewer Responsibilities

Domain reviewers help maintainers decide whether a skill is portable, safe, and
useful across more than one environment. A reviewer should check:

- Assumptions about scheduler, storage, modules, containers, accounts, and
  network access.
- Resource requests, wall times, data movement, cleanup, and side effects.
- Whether site-specific details belong in a site adapter instead of a core
  skill.
- Public references, success criteria, troubleshooting notes, and risk level.
- Whether evidence is strong enough for a maturity promotion.

Reviewers do not need to be project administrators. They can review a single
pull request, help with a collection, or own a domain area over time.

## Seed Reviewer Areas

| Area | Covers | Seed Skills And Collections |
| --- | --- | --- |
| Scheduler and allocation | Slurm jobs, arrays, dependencies, pending reasons, accounting, time limits, partitions, and reservations. | `core-hpc`, `slurm-submit-job`, `slurm-job-array-patterns`, `slurm-job-dependency-chain`, `slurm-pending-reason-triage`, `slurm-monitor-job`, `slurm-resource-estimator`, `slurm-efficiency-report` |
| Storage and data movement | Scratch, project storage, quotas, inode failures, rsync, Globus, checksums, staging, and archive preparation. | `data-movement`, `quota-and-filesystem-triage`, `scratch-storage-management`, `dataset-staging-to-scratch`, `globus-transfer-dataset`, `rsync-data-transfer`, `checksum-manifest-create`, `large-file-archive-prepare` |
| Software environments | Modules, compiler/MPI stacks, Conda, Python virtualenvs, R, Julia, MATLAB, Spack, EasyBuild, and reproducible run capture. | `software-stacks`, `module-environment-debug`, `module-tree-health-check`, `compiler-mpi-matrix`, `conda-mamba-on-hpc`, `python-virtualenv-on-hpc`, `spack-environment-create`, `easybuild-install-software` |
| Containers | Apptainer and Singularity build plans, runtime binds, image portability, containerized MPI, and containerized job patterns. | `containers`, `container-build-for-hpc`, `apptainer-run-container`, `apptainer-mpi-on-slurm` |
| Workflow engines | Nextflow, Snakemake, CWL, WDL, dependency chains, checkpoint/restart, and Dask jobqueue execution. | `workflow-engines`, `nextflow-on-slurm`, `snakemake-on-slurm`, `cwl-on-slurm`, `wdl-on-slurm`, `dask-jobqueue-on-slurm`, `checkpoint-restart-workflow` |
| AI, GPU, and accelerator workflows | CUDA/ROCm visibility, PyTorch DDP, NCCL, DeepSpeed, Ray, GPU memory failures, and accelerator smoke tests. | `ai-hpc`, `gpu-mpi-performance`, `gpu-sanity-check`, `pytorch-ddp-on-slurm`, `nccl-diagnostics`, `gpu-memory-triage`, `deepspeed-on-slurm`, `ray-on-slurm` |
| MPI and performance | MPI launch, containerized MPI, mpi4py, OpenMP placement, simple benchmarks, profiling evidence, and scaling sanity checks. | `gpu-mpi-performance`, `mpi-hello-and-benchmark`, `mpi4py-on-slurm`, `apptainer-mpi-on-slurm`, `openmp-thread-affinity`, `performance-profile-basic` |
| Bioinformatics workflows | nf-core, GATK, BLAST, sample sheets, reference data assumptions, and pipeline resource boundaries. | `bioinformatics-workflows`, `nf-core-on-slurm`, `gatk-workflow-on-hpc`, `blast-on-slurm` |
| Simulation workflows | Molecular dynamics, electronic structure, CFD, weather, MPI decomposition, checkpointing, and restart policy. | `simulation-workflows`, `gromacs-on-slurm`, `lammps-on-slurm`, `quantum-espresso-on-slurm`, `openfoam-on-slurm`, `wrf-on-slurm` |
| Facility operations and training | Read-only node and usage evidence, module tree health, support handoff, workshop reset checks, and onboarding flows. | `facility-ops`, `training-onboarding`, `cluster-usage-report-readonly`, `node-health-readonly-triage`, `training-cluster-reset-checklist`, `interactive-session`, `jupyter-on-slurm` |
| Site adapters | Public local policy mappings, placeholder quality, public documentation links, and boundaries between public and private site details. | `site-adapters/`, `example-campus-cluster` |
| Registry tooling | Schemas, generated indexes, release manifests, CLI behavior, static site output, CI, and compatibility policy. | `schemas/`, `tools/`, `src/`, `registry/`, `docs/COMPATIBILITY.md` |

## Recruiting Priority

Use this order when inviting the first reviewers:

1. Scheduler and allocation, storage and data movement, and software
   environments. These areas affect the most seed skills.
2. AI/GPU, MPI/performance, workflow engines, and containers. These areas have
   higher resource and portability risk.
3. Bioinformatics, simulation workflows, facility operations, training, site
   adapters, and tooling. These areas help the registry become useful to real
   communities and downstream integrations.

## Review Evidence

Good public evidence includes:

- A pull request review that comments on assumptions, examples, risk, and
  portability.
- A public adoption report that uses placeholders and avoids private cluster
  details.
- A successful run on a real environment summarized without hostnames,
  allocation names, private paths, ticket numbers, or unpublished policy.
- A link to public upstream documentation that explains a tool-specific
  behavior used by the skill.

Private logs, incident reports, internal support tickets, and unpublished site
policy should stay outside the public repository.

## Joining As A Reviewer

Potential reviewers can start by commenting on the domain reviewer seed issue,
reviewing one pull request, or opening an adoption report. Maintainers should
record the reviewer area in the issue or pull request, then update CODEOWNERS
only after the repository has stable GitHub users or teams.

Use [Review Routing](REVIEW_ROUTING.md), [Maturity Review](MATURITY_REVIEW.md),
and [Triage Runbook](TRIAGE_RUNBOOK.md) when deciding which reviewer area is
needed for a change.
