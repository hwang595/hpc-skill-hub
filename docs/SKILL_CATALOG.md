# Skill Catalog

This catalog is generated from `skills/*/skill.json` by `tools/build_index.py`.

Current registry size: 15 skills.

## Categories

| Category | Skills |
| --- | ---: |
| `containers` | 1 |
| `data` | 1 |
| `debugging` | 6 |
| `gpu` | 1 |
| `interactive` | 1 |
| `mpi` | 1 |
| `performance` | 2 |
| `scheduler` | 10 |
| `software` | 3 |
| `workflow` | 2 |

## Skills By Category

### Containers

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`apptainer-run-container`](../skills/apptainer-run-container/README.md) | medium | seed | Run Apptainer containers safely on shared HPC systems. |

### Data

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`globus-transfer-dataset`](../skills/globus-transfer-dataset/README.md) | medium | seed | Stage large datasets with Globus transfer and verification steps. |

### Debugging

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`gpu-sanity-check`](../skills/gpu-sanity-check/README.md) | medium | seed | Verify GPU allocation, runtime visibility, and basic framework access. |
| [`job-failure-triage`](../skills/job-failure-triage/README.md) | low | seed | Diagnose common HPC job failures from scheduler and log evidence. |
| [`module-environment-debug`](../skills/module-environment-debug/README.md) | low | seed | Diagnose module, compiler, MPI, and library path conflicts. |
| [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md) | medium | seed | Compile and run MPI sanity checks across allocated nodes. |
| [`performance-profile-basic`](../skills/performance-profile-basic/README.md) | low | seed | Collect first-pass performance evidence for an HPC workload. |
| [`slurm-monitor-job`](../skills/slurm-monitor-job/README.md) | low | seed | Inspect Slurm job state, accounting records, and output paths. |

### GPU

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`gpu-sanity-check`](../skills/gpu-sanity-check/README.md) | medium | seed | Verify GPU allocation, runtime visibility, and basic framework access. |

### Interactive

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`interactive-session`](../skills/interactive-session/README.md) | medium | seed | Start short interactive compute sessions for debugging and notebooks. |

### MPI

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md) | medium | seed | Compile and run MPI sanity checks across allocated nodes. |

### Performance

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`performance-profile-basic`](../skills/performance-profile-basic/README.md) | low | seed | Collect first-pass performance evidence for an HPC workload. |
| [`slurm-resource-estimator`](../skills/slurm-resource-estimator/README.md) | low | seed | Estimate future Slurm resource requests from accounting history. |

### Scheduler

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`apptainer-run-container`](../skills/apptainer-run-container/README.md) | medium | seed | Run Apptainer containers safely on shared HPC systems. |
| [`gpu-sanity-check`](../skills/gpu-sanity-check/README.md) | medium | seed | Verify GPU allocation, runtime visibility, and basic framework access. |
| [`interactive-session`](../skills/interactive-session/README.md) | medium | seed | Start short interactive compute sessions for debugging and notebooks. |
| [`job-failure-triage`](../skills/job-failure-triage/README.md) | low | seed | Diagnose common HPC job failures from scheduler and log evidence. |
| [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md) | medium | seed | Compile and run MPI sanity checks across allocated nodes. |
| [`nextflow-on-slurm`](../skills/nextflow-on-slurm/README.md) | medium | seed | Configure Nextflow pipelines to run through the Slurm executor. |
| [`slurm-monitor-job`](../skills/slurm-monitor-job/README.md) | low | seed | Inspect Slurm job state, accounting records, and output paths. |
| [`slurm-resource-estimator`](../skills/slurm-resource-estimator/README.md) | low | seed | Estimate future Slurm resource requests from accounting history. |
| [`slurm-submit-job`](../skills/slurm-submit-job/README.md) | medium | seed | Generate safe Slurm batch scripts for common HPC job shapes. |
| [`snakemake-on-slurm`](../skills/snakemake-on-slurm/README.md) | medium | seed | Configure Snakemake workflows to submit jobs through Slurm. |

### Software

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`easybuild-install-software`](../skills/easybuild-install-software/README.md) | medium | seed | Install scientific software with EasyBuild and generated modules. |
| [`module-environment-debug`](../skills/module-environment-debug/README.md) | low | seed | Diagnose module, compiler, MPI, and library path conflicts. |
| [`spack-environment-create`](../skills/spack-environment-create/README.md) | medium | seed | Create reproducible Spack environments for HPC software stacks. |

### Workflow

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`nextflow-on-slurm`](../skills/nextflow-on-slurm/README.md) | medium | seed | Configure Nextflow pipelines to run through the Slurm executor. |
| [`snakemake-on-slurm`](../skills/snakemake-on-slurm/README.md) | medium | seed | Configure Snakemake workflows to submit jobs through Slurm. |

## Site Adapters

| Adapter | Status | Scheduler | Description |
| --- | --- | --- | --- |
| [`example-campus-cluster`](../site-adapters/example-campus-cluster/README.md) | example | slurm | A non-production adapter showing how a site can map generic skills to local HPC policy. |

## Next Candidates

- Open OnDemand app templates.
- PyTorch distributed training on Slurm.
- NCCL multi-node diagnostics.
- Filesystem quota and metadata pressure checks.
- WRF, GROMACS, LAMMPS, OpenFOAM, and Quantum ESPRESSO starter skills.
- Bioinformatics workflows for nf-core, GATK, BLAST, and AlphaFold.
- Facility read-only reports for fairshare, partitions, and node health.
