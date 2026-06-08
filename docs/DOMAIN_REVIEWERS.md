# Domain Reviewers

HPC Skill Hub needs domain reviewers before seed skills can become reviewed,
field-tested, or maintained. This document turns the broad review routing rules
into a public recruitment and ownership map.

Use `python3 tools/review_candidates.py --limit 12` to generate a local queue of
seed skills that have enough static evidence for first domain review routing.
Use `--collection <collection-id>` when recruiting reviewers for a specific
collection.

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
| Scheduler and allocation | Slurm jobs, arrays, failed-array retry planning, dependencies, pending reasons, maintenance windows, reservations, QOS/account limits, accounting, memory limits, time limits, partitions, preemption, and requeue behavior. | `core-hpc`, `slurm-submit-job`, `slurm-job-array-patterns`, `slurm-array-retry-plan`, `slurm-job-dependency-chain`, `slurm-pending-reason-triage`, `slurm-maintenance-reservation-triage`, `slurm-qos-account-limit-triage`, `slurm-monitor-job`, `slurm-resource-estimator`, `slurm-oom-memory-triage`, `slurm-efficiency-report`, `slurm-preemption-requeue` |
| Storage and data movement | Scratch, node-local temporary storage, project storage, shared permissions, ACLs, quotas, inode failures, file descriptor pressure, rsync, Globus, object storage, checksums, staging, Darshan I/O profile analysis, Lustre striping layout planning, storage smoke benchmarks, and archive preparation. | `data-movement`, `quota-and-filesystem-triage`, `shared-project-permissions-triage`, `file-descriptor-limit-triage`, `scratch-storage-management`, `dataset-staging-to-scratch`, `node-local-scratch-staging`, `darshan-io-profile-analysis`, `lustre-striping-layout-planning`, `ior-mdtest-storage-smoke`, `globus-transfer-dataset`, `rsync-data-transfer`, `object-storage-transfer`, `checksum-manifest-create`, `large-file-archive-prepare` |
| Software environments | Modules, compiler/MPI stacks, CMake builds, parallel HDF5/NetCDF builds, BLAS/OpenMP thread pools, licensed software jobs, Conda, Python virtualenvs, JAX, Accelerate, and TensorFlow environments, Open OnDemand templates, TensorBoard monitors, Streamlit apps, R, RStudio, Julia, MATLAB, IDE tunnels, Spack, EasyBuild, and reproducible run capture. | `software-stacks`, `module-environment-debug`, `module-tree-health-check`, `compiler-mpi-matrix`, `cmake-hpc-build-preflight`, `parallel-hdf5-netcdf-preflight`, `blas-openmp-thread-control`, `license-aware-slurm-job`, `conda-mamba-on-hpc`, `python-virtualenv-on-hpc`, `jax-distributed-on-slurm`, `huggingface-accelerate-on-slurm`, `tensorflow-multiworker-on-slurm`, `open-ondemand-batch-connect`, `tensorboard-on-slurm`, `streamlit-on-slurm`, `rscript-on-slurm`, `rstudio-on-slurm`, `vscode-tunnel-on-slurm`, `spack-environment-create`, `easybuild-install-software` |
| Containers | Apptainer and Singularity build plans, runtime binds, image portability, containerized MPI, and containerized job patterns. | `containers`, `container-build-for-hpc`, `apptainer-run-container`, `apptainer-mpi-on-slurm` |
| Workflow engines | Nextflow, Snakemake, CWL, WDL, dependency chains, array retry planning, checkpoint/restart, Dask jobqueue execution, Parsl worker blocks, and file descriptor pressure from worker fan-out. | `workflow-engines`, `nextflow-on-slurm`, `snakemake-on-slurm`, `cwl-on-slurm`, `wdl-on-slurm`, `file-descriptor-limit-triage`, `slurm-array-retry-plan`, `dask-jobqueue-on-slurm`, `parsl-on-slurm`, `checkpoint-restart-workflow` |
| AI, GPU, and accelerator workflows | CUDA/ROCm visibility, CPU thread pools, file descriptor pressure in data loaders, GPU binding diagnostics, JAX distributed initialization, Hugging Face Accelerate launches, TensorFlow multi-worker jobs, PyTorch DDP, NCCL, DeepSpeed, Ray, TensorBoard monitors, Streamlit demos, GPU memory failures, and accelerator smoke tests. | `ai-hpc`, `gpu-mpi-performance`, `gpu-sanity-check`, `slurm-gpu-binding-diagnostics`, `blas-openmp-thread-control`, `file-descriptor-limit-triage`, `jax-distributed-on-slurm`, `huggingface-accelerate-on-slurm`, `tensorflow-multiworker-on-slurm`, `pytorch-ddp-on-slurm`, `nccl-diagnostics`, `gpu-memory-triage`, `deepspeed-on-slurm`, `ray-on-slurm`, `tensorboard-on-slurm`, `streamlit-on-slurm` |
| MPI and performance | MPI launch, MPI fabric diagnostics, GPU binding diagnostics, rank binding diagnostics, hybrid MPI/OpenMP layouts, BLAS/OpenMP thread pools, CMake build preflight, parallel HDF5/NetCDF preflight, Darshan I/O profile analysis, Lustre striping layout planning, containerized MPI, mpi4py, OpenMP placement, memory triage, simple benchmarks, IOR/MDTest storage smoke evidence, profiling evidence, and scaling sanity checks. | `gpu-mpi-performance`, `mpi-hello-and-benchmark`, `mpi-fabric-diagnostics`, `slurm-gpu-binding-diagnostics`, `mpi-rank-binding-diagnostics`, `hybrid-mpi-openmp-slurm`, `blas-openmp-thread-control`, `cmake-hpc-build-preflight`, `parallel-hdf5-netcdf-preflight`, `darshan-io-profile-analysis`, `lustre-striping-layout-planning`, `mpi4py-on-slurm`, `apptainer-mpi-on-slurm`, `openmp-thread-affinity`, `slurm-oom-memory-triage`, `ior-mdtest-storage-smoke`, `performance-profile-basic` |
| Bioinformatics workflows | nf-core, GATK, BLAST, sample sheets, reference data assumptions, and pipeline resource boundaries. | `bioinformatics-workflows`, `nf-core-on-slurm`, `gatk-workflow-on-hpc`, `blast-on-slurm` |
| Simulation workflows | Molecular dynamics, electronic structure, CFD, weather, MPI decomposition, MPI fabric diagnostics, hybrid MPI/OpenMP layouts, rank binding diagnostics, CMake build preflight, parallel HDF5/NetCDF preflight, Darshan I/O profile analysis, Lustre striping layout planning, storage smoke evidence, checkpointing, and restart policy. | `simulation-workflows`, `gromacs-on-slurm`, `lammps-on-slurm`, `quantum-espresso-on-slurm`, `openfoam-on-slurm`, `wrf-on-slurm`, `mpi-fabric-diagnostics`, `hybrid-mpi-openmp-slurm`, `mpi-rank-binding-diagnostics`, `cmake-hpc-build-preflight`, `parallel-hdf5-netcdf-preflight`, `darshan-io-profile-analysis`, `lustre-striping-layout-planning`, `ior-mdtest-storage-smoke` |
| Facility operations and training | Read-only node, usage, maintenance/reservation, QOS/account, fairshare, OOM memory, file descriptor pressure, and shared permission evidence, module tree health, support handoff, licensed software onboarding, workshop reset checks, Open OnDemand templates, and onboarding flows. | `facility-ops`, `training-onboarding`, `cluster-usage-report-readonly`, `slurm-maintenance-reservation-triage`, `slurm-qos-account-limit-triage`, `slurm-oom-memory-triage`, `file-descriptor-limit-triage`, `shared-project-permissions-triage`, `node-health-readonly-triage`, `training-cluster-reset-checklist`, `license-aware-slurm-job`, `interactive-session`, `open-ondemand-batch-connect`, `jupyter-on-slurm`, `tensorboard-on-slurm`, `streamlit-on-slurm`, `rstudio-on-slurm`, `vscode-tunnel-on-slurm` |
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
