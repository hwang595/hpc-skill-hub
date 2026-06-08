# Skill Backlog

This backlog lists high-value HPC skills to develop after the seed registry.
It is intentionally public so contributors can claim focused tasks and propose
new collections.

## Priority 1: Core User Workflows

| Skill id | Category | Risk | Why it matters |
| --- | --- | --- | --- |
| `scratch-storage-management` | data | low | Users need safe patterns for scratch, project, and home storage usage. |
| `quota-and-filesystem-triage` | debugging | low | Many failed jobs come from full quotas, inode limits, or slow metadata access. |
| `slurm-job-array-patterns` | scheduler | medium | Arrays are essential for parameter sweeps and embarrassingly parallel work. |
| `checkpoint-restart-workflow` | scheduler | medium | Long jobs need restartable patterns to survive limits and preemption. |
| `openmp-thread-affinity` | performance | medium | Thread placement mistakes waste CPU allocations and distort benchmarks. |
| `jupyter-on-slurm` | interactive | medium | Notebook workflows need scheduler-backed sessions and clear tunnel guidance. |

## Priority 2: Software And Reproducibility

| Skill id | Category | Risk | Why it matters |
| --- | --- | --- | --- |
| `python-virtualenv-on-hpc` | software | low | Python environments are common and need clean module/compiler assumptions. |
| `conda-mamba-on-hpc` | software | medium | Conda environments can overload shared filesystems without careful guidance. |
| `compiler-mpi-matrix` | software | low | Users need to match compiler, MPI, modules, and application binaries. |
| `reproducible-run-capture` | debugging | low | Capturing modules, environment, git SHA, and inputs improves supportability. |
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
