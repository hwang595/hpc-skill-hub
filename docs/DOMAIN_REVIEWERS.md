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
| Scheduler and allocation | Slurm jobs, arrays, dependencies, pending reasons, accounting, time limits, partitions, and reservations. | `core-hpc`, `slurm-submit-job`, `slurm-job-array-patterns`, `slurm-job-dependency-chain`, `slurm-pending-reason-triage`, `slurm-monitor-job`, `slurm-resource-estimator`, `slurm-efficiency-report` |
| Storage and data movement | Scratch, project storage, quotas, inode failures, rsync, Globus, object storage, checksums, staging, storage smoke benchmarks, and archive preparation. | `data-movement`, `quota-and-filesystem-triage`, `scratch-storage-management`, `dataset-staging-to-scratch`, `ior-mdtest-storage-smoke`, `globus-transfer-dataset`, `rsync-data-transfer`, `object-storage-transfer`, `checksum-manifest-create`, `large-file-archive-prepare` |
| Software environments | Modules, compiler/MPI stacks, licensed software jobs, Conda, Python virtualenvs, JAX, Accelerate, and TensorFlow environments, Open OnDemand templates, TensorBoard monitors, Streamlit apps, R, RStudio, Julia, MATLAB, IDE tunnels, Spack, EasyBuild, and reproducible run capture. | `software-stacks`, `module-environment-debug`, `module-tree-health-check`, `compiler-mpi-matrix`, `license-aware-slurm-job`, `conda-mamba-on-hpc`, `python-virtualenv-on-hpc`, `jax-distributed-on-slurm`, `huggingface-accelerate-on-slurm`, `tensorflow-multiworker-on-slurm`, `open-ondemand-batch-connect`, `tensorboard-on-slurm`, `streamlit-on-slurm`, `rscript-on-slurm`, `rstudio-on-slurm`, `vscode-tunnel-on-slurm`, `spack-environment-create`, `easybuild-install-software` |
| Containers | Apptainer and Singularity build plans, runtime binds, image portability, containerized MPI, and containerized job patterns. | `containers`, `container-build-for-hpc`, `apptainer-run-container`, `apptainer-mpi-on-slurm` |
| Workflow engines | Nextflow, Snakemake, CWL, WDL, dependency chains, checkpoint/restart, Dask jobqueue execution, and Parsl worker blocks. | `workflow-engines`, `nextflow-on-slurm`, `snakemake-on-slurm`, `cwl-on-slurm`, `wdl-on-slurm`, `dask-jobqueue-on-slurm`, `parsl-on-slurm`, `checkpoint-restart-workflow` |
| AI, GPU, and accelerator workflows | CUDA/ROCm visibility, JAX distributed initialization, Hugging Face Accelerate launches, TensorFlow multi-worker jobs, PyTorch DDP, NCCL, DeepSpeed, Ray, TensorBoard monitors, Streamlit demos, GPU memory failures, and accelerator smoke tests. | `ai-hpc`, `gpu-mpi-performance`, `gpu-sanity-check`, `jax-distributed-on-slurm`, `huggingface-accelerate-on-slurm`, `tensorflow-multiworker-on-slurm`, `pytorch-ddp-on-slurm`, `nccl-diagnostics`, `gpu-memory-triage`, `deepspeed-on-slurm`, `ray-on-slurm`, `tensorboard-on-slurm`, `streamlit-on-slurm` |
| MPI and performance | MPI launch, rank binding diagnostics, hybrid MPI/OpenMP layouts, containerized MPI, mpi4py, OpenMP placement, simple benchmarks, IOR/MDTest storage smoke evidence, profiling evidence, and scaling sanity checks. | `gpu-mpi-performance`, `mpi-hello-and-benchmark`, `mpi-rank-binding-diagnostics`, `hybrid-mpi-openmp-slurm`, `mpi4py-on-slurm`, `apptainer-mpi-on-slurm`, `openmp-thread-affinity`, `ior-mdtest-storage-smoke`, `performance-profile-basic` |
| Bioinformatics workflows | nf-core, GATK, BLAST, sample sheets, reference data assumptions, and pipeline resource boundaries. | `bioinformatics-workflows`, `nf-core-on-slurm`, `gatk-workflow-on-hpc`, `blast-on-slurm` |
| Simulation workflows | Molecular dynamics, electronic structure, CFD, weather, MPI decomposition, hybrid MPI/OpenMP layouts, rank binding diagnostics, storage smoke evidence, checkpointing, and restart policy. | `simulation-workflows`, `gromacs-on-slurm`, `lammps-on-slurm`, `quantum-espresso-on-slurm`, `openfoam-on-slurm`, `wrf-on-slurm`, `hybrid-mpi-openmp-slurm`, `mpi-rank-binding-diagnostics`, `ior-mdtest-storage-smoke` |
| Facility operations and training | Read-only node and usage evidence, module tree health, support handoff, licensed software onboarding, workshop reset checks, Open OnDemand templates, and onboarding flows. | `facility-ops`, `training-onboarding`, `cluster-usage-report-readonly`, `node-health-readonly-triage`, `training-cluster-reset-checklist`, `license-aware-slurm-job`, `interactive-session`, `open-ondemand-batch-connect`, `jupyter-on-slurm`, `tensorboard-on-slurm`, `streamlit-on-slurm`, `rstudio-on-slurm`, `vscode-tunnel-on-slurm` |
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
