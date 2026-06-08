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
| `container-build-for-hpc` | containers | medium | Seed skill added to `software-stacks`. |
| `checksum-manifest-create` | data | low | Seed skill added to `data-movement`. |
| `rsync-data-transfer` | data | medium | Seed skill added to `data-movement`. |
| `dataset-staging-to-scratch` | data | medium | Seed skill added to `data-movement`. |
| `large-file-archive-prepare` | data | medium | Seed skill added to `data-movement`. |
| `pytorch-ddp-on-slurm` | gpu | medium | Seed skill added to `gpu-mpi-performance`. |
| `nccl-diagnostics` | gpu | medium | Seed skill added to `gpu-mpi-performance`. |
| `gpu-memory-triage` | debugging | low | Seed skill added to `gpu-mpi-performance`. |
| `deepspeed-on-slurm` | gpu | medium | Seed skill added to `gpu-mpi-performance`. |
| `nf-core-on-slurm` | workflow | medium | Seed skill added to `workflow-engines` and `bioinformatics-workflows`. |
| `gatk-workflow-on-hpc` | workflow | medium | Seed skill added to `bioinformatics-workflows`. |
| `lammps-on-slurm` | mpi | medium | Seed skill added to `simulation-workflows`. |
| `gromacs-on-slurm` | gpu | medium | Seed skill added to `simulation-workflows`. |
| `openfoam-on-slurm` | mpi | medium | Seed skill added to `simulation-workflows`. |
| `wrf-on-slurm` | mpi | medium | Seed skill added to `simulation-workflows`. |
| `cluster-usage-report-readonly` | admin | low | Seed skill added to `facility-ops`. |

## Priority 1: Core User Workflows

Priority 1 is implemented in the seed registry. New core workflow requests
should be proposed through skill request issues.

## Priority 2: Software And Reproducibility

Priority 2 is implemented in the seed registry. New software or reproducibility
requests should be proposed through skill request issues.

## Priority 3: Data Movement And Data Lifecycle

Priority 3 is implemented in the seed registry. New transfer, archive,
publication, and data lifecycle requests should be proposed through skill
request issues.

## Priority 4: AI/HPC And Accelerators

Priority 4 is implemented in the seed registry. New AI/HPC and accelerator
requests should be proposed through skill request issues.

## Priority 5: Domain Collections

Priority 5 is implemented in the seed registry. New domain workflow requests
should be proposed through skill request issues.

## Priority 6: Facility Operations

These should start as low-risk, read-only skills unless an operations
maintainer explicitly reviews them as high risk.

| Skill id | Category | Risk | Why it matters |
| --- | --- | --- | --- |
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
