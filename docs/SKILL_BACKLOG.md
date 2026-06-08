# Skill Backlog

This backlog lists high-value HPC skills to develop after the seed registry.
It is intentionally public so contributors can claim focused tasks and propose
new collections.

## Recently Implemented From This Backlog

| Skill id | Category | Risk | Status |
| --- | --- | --- | --- |
| `pbs-submit-job` | scheduler | medium | Seed skill added to `scheduler-basics`. |
| `lsf-submit-job` | scheduler | medium | Seed skill added to `scheduler-basics`. |
| `htcondor-submit-job` | scheduler | medium | Seed skill added to `scheduler-basics`. |
| `grid-engine-submit-job` | scheduler | medium | Seed skill added to `scheduler-basics`. |
| `scratch-storage-management` | data | low | Seed skill added to `core-hpc` and `data-movement`. |
| `quota-and-filesystem-triage` | debugging | low | Seed skill added to `core-hpc` and `data-movement`. |
| `slurm-job-array-patterns` | scheduler | medium | Seed skill added to `core-hpc`. |
| `slurm-job-dependency-chain` | scheduler | medium | Seed skill added to `core-hpc` and `workflow-engines`. |
| `slurm-pending-reason-triage` | scheduler | low | Seed skill added to `core-hpc` and `facility-ops`. |
| `slurm-efficiency-report` | scheduler | low | Seed skill added to `core-hpc` and `gpu-mpi-performance`. |
| `license-aware-slurm-job` | scheduler | medium | Seed skill added to `core-hpc`, `software-stacks`, and `training-onboarding`. |
| `checkpoint-restart-workflow` | scheduler | medium | Seed skill added to `core-hpc`. |
| `slurm-preemption-requeue` | scheduler | medium | Seed skill added to `core-hpc` and `training-onboarding`. |
| `openmp-thread-affinity` | performance | medium | Seed skill added to `core-hpc` and `gpu-mpi-performance`. |
| `jupyter-on-slurm` | interactive | medium | Seed skill added to `core-hpc`. |
| `rstudio-on-slurm` | interactive | medium | Seed skill added to `core-hpc`, `software-stacks`, and `training-onboarding`. |
| `vscode-tunnel-on-slurm` | interactive | medium | Seed skill added to `core-hpc`, `software-stacks`, and `training-onboarding`. |
| `python-virtualenv-on-hpc` | software | low | Seed skill added to `software-stacks`. |
| `open-ondemand-batch-connect` | interactive | medium | Seed skill added to `software-stacks` and `training-onboarding`. |
| `tensorboard-on-slurm` | interactive | medium | Seed skill added to `ai-hpc`, `gpu-mpi-performance`, `software-stacks`, and `training-onboarding`. |
| `streamlit-on-slurm` | interactive | medium | Seed skill added to `software-stacks`, `training-onboarding`, and `ai-hpc`. |
| `ray-on-slurm` | gpu | medium | Seed skill added to `software-stacks` and `gpu-mpi-performance`. |
| `dask-jobqueue-on-slurm` | workflow | medium | Seed skill added to `software-stacks` and `workflow-engines`. |
| `parsl-on-slurm` | workflow | medium | Seed skill added to `software-stacks` and `workflow-engines`. |
| `jax-distributed-on-slurm` | gpu | medium | Seed skill added to `ai-hpc`, `gpu-mpi-performance`, and `software-stacks`. |
| `huggingface-accelerate-on-slurm` | gpu | medium | Seed skill added to `ai-hpc`, `gpu-mpi-performance`, and `software-stacks`. |
| `tensorflow-multiworker-on-slurm` | gpu | medium | Seed skill added to `ai-hpc`, `gpu-mpi-performance`, and `software-stacks`. |
| `mpi4py-on-slurm` | software | medium | Seed skill added to `software-stacks` and `gpu-mpi-performance`. |
| `mpi-fabric-diagnostics` | mpi | medium | Seed skill added to `gpu-mpi-performance` and `simulation-workflows`. |
| `mpi-rank-binding-diagnostics` | mpi | medium | Seed skill added to `gpu-mpi-performance` and `simulation-workflows`. |
| `hybrid-mpi-openmp-slurm` | mpi | medium | Seed skill added to `gpu-mpi-performance` and `simulation-workflows`. |
| `rscript-on-slurm` | software | medium | Seed skill added to `software-stacks` and `training-onboarding`. |
| `julia-on-slurm` | software | medium | Seed skill added to `software-stacks` and `training-onboarding`. |
| `matlab-batch-on-slurm` | software | medium | Seed skill added to `software-stacks` and `training-onboarding`. |
| `conda-mamba-on-hpc` | software | medium | Seed skill added to `software-stacks`. |
| `compiler-mpi-matrix` | software | low | Seed skill added to `software-stacks` and `gpu-mpi-performance`. |
| `reproducible-run-capture` | debugging | low | Seed skill added to `software-stacks`. |
| `container-build-for-hpc` | containers | medium | Seed skill added to `software-stacks`. |
| `apptainer-mpi-on-slurm` | containers | medium | Seed skill added to `containers`, `software-stacks`, and `gpu-mpi-performance`. |
| `checksum-manifest-create` | data | low | Seed skill added to `data-movement`. |
| `rsync-data-transfer` | data | medium | Seed skill added to `data-movement`. |
| `object-storage-transfer` | data | medium | Seed skill added to `data-movement`. |
| `dataset-staging-to-scratch` | data | medium | Seed skill added to `data-movement`. |
| `ior-mdtest-storage-smoke` | performance | medium | Seed skill added to `data-movement`, `gpu-mpi-performance`, and `simulation-workflows`. |
| `large-file-archive-prepare` | data | medium | Seed skill added to `data-movement`. |
| `cwl-on-slurm` | workflow | medium | Seed skill added to `workflow-engines`. |
| `wdl-on-slurm` | workflow | medium | Seed skill added to `workflow-engines`. |
| `pytorch-ddp-on-slurm` | gpu | medium | Seed skill added to `gpu-mpi-performance`. |
| `nccl-diagnostics` | gpu | medium | Seed skill added to `gpu-mpi-performance`. |
| `slurm-gpu-binding-diagnostics` | gpu | medium | Seed skill added to `ai-hpc` and `gpu-mpi-performance`. |
| `gpu-memory-triage` | debugging | low | Seed skill added to `gpu-mpi-performance`. |
| `deepspeed-on-slurm` | gpu | medium | Seed skill added to `gpu-mpi-performance`. |
| `nf-core-on-slurm` | workflow | medium | Seed skill added to `workflow-engines` and `bioinformatics-workflows`. |
| `gatk-workflow-on-hpc` | workflow | medium | Seed skill added to `bioinformatics-workflows`. |
| `blast-on-slurm` | workflow | medium | Seed skill added to `bioinformatics-workflows`. |
| `lammps-on-slurm` | mpi | medium | Seed skill added to `simulation-workflows`. |
| `gromacs-on-slurm` | gpu | medium | Seed skill added to `simulation-workflows`. |
| `namd-on-slurm` | mpi | medium | Seed skill added to `simulation-workflows`. |
| `quantum-espresso-on-slurm` | mpi | medium | Seed skill added to `simulation-workflows`. |
| `cp2k-on-slurm` | mpi | medium | Seed skill added to `simulation-workflows`. |
| `openfoam-on-slurm` | mpi | medium | Seed skill added to `simulation-workflows`. |
| `wrf-on-slurm` | mpi | medium | Seed skill added to `simulation-workflows`. |
| `cluster-usage-report-readonly` | admin | low | Seed skill added to `facility-ops`. |
| `node-health-readonly-triage` | admin | low | Seed skill added to `facility-ops`. |
| `module-tree-health-check` | software | low | Seed skill added to `software-stacks` and `facility-ops`. |
| `training-cluster-reset-checklist` | education | medium | Seed skill added to `training-onboarding`. |

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

## Priority 6: Facility Operations And Training

These should start as low-risk, read-only skills unless an operations
maintainer explicitly reviews them as high risk.

| Skill id | Category | Risk | Why it matters |
| --- | --- | --- | --- |
| _none currently listed_ | | | New requests should come through skill request issues. |

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

Use [Skill Lifecycle](SKILL_LIFECYCLE.md) to decide when a backlog request is
ready for implementation, maturity review, field testing, maintenance, or
deprecation.
