# Skill Backlog

This backlog lists high-value HPC skills to develop after the seed registry.
It is intentionally public so contributors can claim focused tasks and propose
new collections.

## Recently Implemented From This Backlog

| Skill id | Category | Risk | Status |
| --- | --- | --- | --- |
| `scratch-storage-management` | data | low | Seed skill added to `core-hpc` and `data-movement`. |
| `quota-and-filesystem-triage` | debugging | low | Seed skill added to `core-hpc` and `data-movement`. |
| `slurm-job-array-patterns` | scheduler | medium | Seed skill added to `core-hpc`. |
| `checkpoint-restart-workflow` | scheduler | medium | Seed skill added to `core-hpc`. |
| `openmp-thread-affinity` | performance | medium | Seed skill added to `core-hpc` and `gpu-mpi-performance`. |
| `jupyter-on-slurm` | interactive | medium | Seed skill added to `core-hpc`. |
| `python-virtualenv-on-hpc` | software | low | Seed skill added to `software-stacks`. |
| `conda-mamba-on-hpc` | software | medium | Seed skill added to `software-stacks`. |
| `compiler-mpi-matrix` | software | low | Seed skill added to `software-stacks` and `gpu-mpi-performance`. |
| `reproducible-run-capture` | debugging | low | Seed skill added to `software-stacks`. |

## Priority 1: Core User Workflows

Priority 1 is implemented in the seed registry. New core workflow requests
should be proposed through skill request issues.

## Priority 2: Software And Reproducibility

| Skill id | Category | Risk | Why it matters |
| --- | --- | --- | --- |
| `container-build-for-hpc` | containers | medium | Users need safe image build and conversion patterns before running containers. |

## Priority 3: Data Movement And Data Lifecycle

| Skill id | Category | Risk | Why it matters |
| --- | --- | --- | --- |
| `rsync-data-transfer` | data | medium | Smaller transfers still need resumable, checksummed command patterns. |
| `checksum-manifest-create` | data | low | Transfer validation should be repeatable and visible. |
| `dataset-staging-to-scratch` | data | medium | Workflows often need input staging and output collection around jobs. |
| `large-file-archive-prepare` | data | medium | Users need packaging and manifest patterns before archival or publication. |

## Priority 4: AI/HPC And Accelerators

| Skill id | Category | Risk | Why it matters |
| --- | --- | --- | --- |
| `pytorch-ddp-on-slurm` | gpu | medium | Distributed training needs launcher, environment, and rank sanity checks. |
| `nccl-diagnostics` | gpu | medium | Multi-GPU and multi-node jobs often fail in communication setup. |
| `deepspeed-on-slurm` | gpu | medium | Large model training needs conservative Slurm and storage patterns. |
| `gpu-memory-triage` | debugging | low | Users need to distinguish allocation, framework, and model memory failures. |

## Priority 5: Domain Collections

| Skill id | Category | Risk | Why it matters |
| --- | --- | --- | --- |
| `nf-core-on-slurm` | workflow | medium | Bioinformatics teams need a reviewed Nextflow pattern for common pipelines. |
| `gatk-workflow-on-hpc` | workflow | medium | Genomics workflows often combine Java, modules, containers, and data staging. |
| `lammps-on-slurm` | mpi | medium | Molecular dynamics users need MPI, GPU, restart, and scaling examples. |
| `gromacs-on-slurm` | gpu | medium | GROMACS runs expose common GPU/MPI/thread placement decisions. |
| `openfoam-on-slurm` | mpi | medium | CFD workflows need decomposition, MPI launch, and output management patterns. |
| `wrf-on-slurm` | mpi | medium | Climate/weather workloads need MPI sizing, restart, and I/O guidance. |

## Priority 6: Facility Operations

These should start as low-risk, read-only skills unless an operations
maintainer explicitly reviews them as high risk.

| Skill id | Category | Risk | Why it matters |
| --- | --- | --- | --- |
| `cluster-usage-report-readonly` | admin | low | Support teams need shareable reporting patterns that do not change state. |
| `node-health-readonly-triage` | admin | low | Read-only node evidence helps separate user errors from system incidents. |
| `module-tree-health-check` | software | low | Broken module paths and stale dependencies are common support issues. |
| `training-cluster-reset-checklist` | education | medium | Workshops need repeatable preflight and cleanup guidance. |

## Picking The Next Skill

Prefer skills that:

- Reduce repeated support questions.
- Have public references and safe examples.
- Can be validated without a private cluster.
- Fit an existing collection.
- Have a likely domain reviewer.

Avoid starting with skills that require private operational details, privileged
access, or large resource allocations unless a maintainer has agreed to own the
review.

## Claiming A Skill

1. Open a skill request issue with the proposed skill id.
2. Link any public references.
3. State target users and expected environment.
4. Create the scaffold with `tools/hpc_skill.py`.
5. Open a draft pull request early so maintainers can shape scope and risk.
