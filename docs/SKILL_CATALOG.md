# Skill Catalog

This catalog is generated from `skills/*/skill.json` by `tools/build_index.py`.

Current registry size: 27 skills.

## Categories

| Category | Skills |
| --- | ---: |
| `containers` | 2 |
| `data` | 4 |
| `debugging` | 11 |
| `gpu` | 1 |
| `interactive` | 2 |
| `mpi` | 2 |
| `performance` | 3 |
| `scheduler` | 14 |
| `software` | 8 |
| `workflow` | 2 |

## Skills By Category

### Containers

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`apptainer-run-container`](../skills/apptainer-run-container/README.md) | medium | seed | Run Apptainer containers safely on shared HPC systems. |
| [`container-build-for-hpc`](../skills/container-build-for-hpc/README.md) | medium | seed | Plan and build Apptainer-compatible images for shared HPC systems. |

### Data

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`checksum-manifest-create`](../skills/checksum-manifest-create/README.md) | low | seed | Create checksum manifests for transfer validation and reproducibility. |
| [`globus-transfer-dataset`](../skills/globus-transfer-dataset/README.md) | medium | seed | Stage large datasets with Globus transfer and verification steps. |
| [`quota-and-filesystem-triage`](../skills/quota-and-filesystem-triage/README.md) | low | seed | Diagnose quota, inode, and filesystem-space failures from user-visible evidence. |
| [`scratch-storage-management`](../skills/scratch-storage-management/README.md) | low | seed | Inspect scratch, project, and working-directory usage before HPC jobs. |

### Debugging

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`checkpoint-restart-workflow`](../skills/checkpoint-restart-workflow/README.md) | medium | seed | Structure long HPC jobs so they can resume after time limits or preemption. |
| [`compiler-mpi-matrix`](../skills/compiler-mpi-matrix/README.md) | low | seed | Check compiler, MPI wrapper, and module compatibility before building HPC codes. |
| [`gpu-sanity-check`](../skills/gpu-sanity-check/README.md) | medium | seed | Verify GPU allocation, runtime visibility, and basic framework access. |
| [`job-failure-triage`](../skills/job-failure-triage/README.md) | low | seed | Diagnose common HPC job failures from scheduler and log evidence. |
| [`module-environment-debug`](../skills/module-environment-debug/README.md) | low | seed | Diagnose module, compiler, MPI, and library path conflicts. |
| [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md) | medium | seed | Compile and run MPI sanity checks across allocated nodes. |
| [`performance-profile-basic`](../skills/performance-profile-basic/README.md) | low | seed | Collect first-pass performance evidence for an HPC workload. |
| [`quota-and-filesystem-triage`](../skills/quota-and-filesystem-triage/README.md) | low | seed | Diagnose quota, inode, and filesystem-space failures from user-visible evidence. |
| [`reproducible-run-capture`](../skills/reproducible-run-capture/README.md) | low | seed | Capture command, environment, provenance, and logs for reproducible HPC runs. |
| [`scratch-storage-management`](../skills/scratch-storage-management/README.md) | low | seed | Inspect scratch, project, and working-directory usage before HPC jobs. |
| [`slurm-monitor-job`](../skills/slurm-monitor-job/README.md) | low | seed | Inspect Slurm job state, accounting records, and output paths. |

### GPU

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`gpu-sanity-check`](../skills/gpu-sanity-check/README.md) | medium | seed | Verify GPU allocation, runtime visibility, and basic framework access. |

### Interactive

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`interactive-session`](../skills/interactive-session/README.md) | medium | seed | Start short interactive compute sessions for debugging and notebooks. |
| [`jupyter-on-slurm`](../skills/jupyter-on-slurm/README.md) | medium | seed | Launch Jupyter notebooks inside short Slurm compute allocations. |

### MPI

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`compiler-mpi-matrix`](../skills/compiler-mpi-matrix/README.md) | low | seed | Check compiler, MPI wrapper, and module compatibility before building HPC codes. |
| [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md) | medium | seed | Compile and run MPI sanity checks across allocated nodes. |

### Performance

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`openmp-thread-affinity`](../skills/openmp-thread-affinity/README.md) | medium | seed | Align OpenMP threads with Slurm CPU allocations and affinity settings. |
| [`performance-profile-basic`](../skills/performance-profile-basic/README.md) | low | seed | Collect first-pass performance evidence for an HPC workload. |
| [`slurm-resource-estimator`](../skills/slurm-resource-estimator/README.md) | low | seed | Estimate future Slurm resource requests from accounting history. |

### Scheduler

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`apptainer-run-container`](../skills/apptainer-run-container/README.md) | medium | seed | Run Apptainer containers safely on shared HPC systems. |
| [`checkpoint-restart-workflow`](../skills/checkpoint-restart-workflow/README.md) | medium | seed | Structure long HPC jobs so they can resume after time limits or preemption. |
| [`gpu-sanity-check`](../skills/gpu-sanity-check/README.md) | medium | seed | Verify GPU allocation, runtime visibility, and basic framework access. |
| [`interactive-session`](../skills/interactive-session/README.md) | medium | seed | Start short interactive compute sessions for debugging and notebooks. |
| [`job-failure-triage`](../skills/job-failure-triage/README.md) | low | seed | Diagnose common HPC job failures from scheduler and log evidence. |
| [`jupyter-on-slurm`](../skills/jupyter-on-slurm/README.md) | medium | seed | Launch Jupyter notebooks inside short Slurm compute allocations. |
| [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md) | medium | seed | Compile and run MPI sanity checks across allocated nodes. |
| [`nextflow-on-slurm`](../skills/nextflow-on-slurm/README.md) | medium | seed | Configure Nextflow pipelines to run through the Slurm executor. |
| [`openmp-thread-affinity`](../skills/openmp-thread-affinity/README.md) | medium | seed | Align OpenMP threads with Slurm CPU allocations and affinity settings. |
| [`slurm-job-array-patterns`](../skills/slurm-job-array-patterns/README.md) | medium | seed | Run parameter sweeps and many independent tasks with Slurm job arrays. |
| [`slurm-monitor-job`](../skills/slurm-monitor-job/README.md) | low | seed | Inspect Slurm job state, accounting records, and output paths. |
| [`slurm-resource-estimator`](../skills/slurm-resource-estimator/README.md) | low | seed | Estimate future Slurm resource requests from accounting history. |
| [`slurm-submit-job`](../skills/slurm-submit-job/README.md) | medium | seed | Generate safe Slurm batch scripts for common HPC job shapes. |
| [`snakemake-on-slurm`](../skills/snakemake-on-slurm/README.md) | medium | seed | Configure Snakemake workflows to submit jobs through Slurm. |

### Software

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`compiler-mpi-matrix`](../skills/compiler-mpi-matrix/README.md) | low | seed | Check compiler, MPI wrapper, and module compatibility before building HPC codes. |
| [`conda-mamba-on-hpc`](../skills/conda-mamba-on-hpc/README.md) | medium | seed | Create Conda or Mamba environments while protecting shared HPC filesystems. |
| [`container-build-for-hpc`](../skills/container-build-for-hpc/README.md) | medium | seed | Plan and build Apptainer-compatible images for shared HPC systems. |
| [`easybuild-install-software`](../skills/easybuild-install-software/README.md) | medium | seed | Install scientific software with EasyBuild and generated modules. |
| [`module-environment-debug`](../skills/module-environment-debug/README.md) | low | seed | Diagnose module, compiler, MPI, and library path conflicts. |
| [`python-virtualenv-on-hpc`](../skills/python-virtualenv-on-hpc/README.md) | low | seed | Create lightweight Python virtual environments with explicit HPC module assumptions. |
| [`reproducible-run-capture`](../skills/reproducible-run-capture/README.md) | low | seed | Capture command, environment, provenance, and logs for reproducible HPC runs. |
| [`spack-environment-create`](../skills/spack-environment-create/README.md) | medium | seed | Create reproducible Spack environments for HPC software stacks. |

### Workflow

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`nextflow-on-slurm`](../skills/nextflow-on-slurm/README.md) | medium | seed | Configure Nextflow pipelines to run through the Slurm executor. |
| [`snakemake-on-slurm`](../skills/snakemake-on-slurm/README.md) | medium | seed | Configure Snakemake workflows to submit jobs through Slurm. |

## Collections

| Collection | Status | Skills | Audience | Description |
| --- | --- | ---: | --- | --- |
| [`core-hpc`](../collections/core-hpc.json) | draft | 11 | new HPC users, research software engineers, support teams | Starter skills for Slurm jobs, arrays, restartable workflows, notebooks, OpenMP placement, debugging, and storage triage. |
| [`data-movement`](../collections/data-movement.json) | draft | 4 | data stewards, research groups, facility support teams | Skills for staging, transferring, validating, and managing research data on HPC storage. |
| [`gpu-mpi-performance`](../collections/gpu-mpi-performance.json) | draft | 5 | AI/HPC users, simulation teams, performance engineers | Skills for validating GPU allocations, compiler/MPI compatibility, MPI launches, OpenMP placement, and first-pass performance evidence. |
| [`software-stacks`](../collections/software-stacks.json) | draft | 9 | research software engineers, HPC support teams, tool maintainers | Skills for debugging modules, compiler/MPI compatibility, Python and Conda environments, containers, and reproducible HPC software stacks. |
| [`workflow-engines`](../collections/workflow-engines.json) | draft | 2 | pipeline authors, bioinformatics teams, workflow platform maintainers | Skills for launching portable workflow engines on Slurm-backed HPC clusters. |

## Site Adapters

| Adapter | Status | Scheduler | Description |
| --- | --- | --- | --- |
| [`example-campus-cluster`](../site-adapters/example-campus-cluster/README.md) | example | slurm | A non-production adapter showing how a site can map generic skills to local HPC policy. |

## Next Candidates

- Open OnDemand app templates.
- PyTorch distributed training on Slurm.
- NCCL multi-node diagnostics.
- Rsync data transfer patterns.
- Dataset staging to scratch workflows.
- WRF, GROMACS, LAMMPS, OpenFOAM, and Quantum ESPRESSO starter skills.
- Bioinformatics workflows for nf-core, GATK, BLAST, and AlphaFold.
- Facility read-only reports for fairshare, partitions, and node health.
