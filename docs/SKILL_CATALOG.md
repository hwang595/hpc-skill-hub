# Skill Catalog

This catalog summarizes the seed skills currently maintained in the registry.

## Scheduler And Job Operations

| Skill | Risk | Description |
| --- | --- | --- |
| `slurm-submit-job` | medium | Create Slurm batch scripts for CPU, GPU, MPI, and array jobs. |
| `slurm-monitor-job` | low | Inspect queue, accounting, and controller state for Slurm jobs. |
| `slurm-resource-estimator` | low | Use accounting history to choose memory, CPU, and wall-time requests. |
| `job-failure-triage` | low | Diagnose failed jobs from scheduler state and logs. |
| `interactive-session` | medium | Start short interactive compute sessions for shells and notebooks. |

## Environments, Containers, And Software

| Skill | Risk | Description |
| --- | --- | --- |
| `module-environment-debug` | low | Gather evidence for module, compiler, MPI, and library conflicts. |
| `apptainer-run-container` | medium | Run Apptainer/Singularity images under Slurm with explicit binds. |
| `spack-environment-create` | medium | Create reproducible Spack environments. |
| `easybuild-install-software` | medium | Dry-run and install scientific software with EasyBuild. |

## Data And Workflow Engines

| Skill | Risk | Description |
| --- | --- | --- |
| `globus-transfer-dataset` | medium | Submit and watch reliable Globus transfers for large datasets. |
| `nextflow-on-slurm` | medium | Configure Nextflow pipelines for Slurm execution. |
| `snakemake-on-slurm` | medium | Configure Snakemake workflows with a Slurm profile. |

## MPI, GPU, And Performance

| Skill | Risk | Description |
| --- | --- | --- |
| `mpi-hello-and-benchmark` | medium | Compile and run an MPI hello-world sanity check across nodes. |
| `gpu-sanity-check` | medium | Verify GPU allocation and runtime visibility. |
| `performance-profile-basic` | low | Wrap a command with basic timing, environment, and telemetry capture. |

## Next Candidates

- Open OnDemand app templates.
- PyTorch distributed training on Slurm.
- NCCL multi-node diagnostics.
- Filesystem quota and metadata pressure checks.
- WRF, GROMACS, LAMMPS, OpenFOAM, and Quantum ESPRESSO starter skills.
- Bioinformatics workflows for nf-core, GATK, BLAST, and AlphaFold.
- Facility read-only reports for fairshare, partitions, and node health.
