# Skill Catalog

This catalog is generated from `skills/*/skill.json` by `tools/build_index.py`.

Current registry size: 68 skills.

## Categories

| Category | Skills |
| --- | ---: |
| `admin` | 4 |
| `containers` | 3 |
| `data` | 12 |
| `debugging` | 18 |
| `education` | 1 |
| `gpu` | 9 |
| `interactive` | 6 |
| `mpi` | 11 |
| `performance` | 12 |
| `scheduler` | 51 |
| `software` | 19 |
| `workflow` | 10 |

## Skills By Category

### Admin

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`cluster-usage-report-readonly`](../skills/cluster-usage-report-readonly/README.md) | low | seed | Collect read-only Slurm usage evidence for facility support reports. |
| [`module-tree-health-check`](../skills/module-tree-health-check/README.md) | low | seed | Collect read-only evidence about visible HPC module tree health. |
| [`node-health-readonly-triage`](../skills/node-health-readonly-triage/README.md) | low | seed | Collect read-only Slurm node evidence for support triage. |
| [`training-cluster-reset-checklist`](../skills/training-cluster-reset-checklist/README.md) | medium | seed | Prepare and review HPC training environments before and after workshops. |

### Containers

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`apptainer-mpi-on-slurm`](../skills/apptainer-mpi-on-slurm/README.md) | medium | seed | Run MPI applications from Apptainer containers inside Slurm allocations. |
| [`apptainer-run-container`](../skills/apptainer-run-container/README.md) | medium | seed | Run Apptainer containers safely on shared HPC systems. |
| [`container-build-for-hpc`](../skills/container-build-for-hpc/README.md) | medium | seed | Plan and build Apptainer-compatible images for shared HPC systems. |

### Data

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`blast-on-slurm`](../skills/blast-on-slurm/README.md) | medium | seed | Run local BLAST+ searches on Slurm with bounded smoke-test defaults. |
| [`checksum-manifest-create`](../skills/checksum-manifest-create/README.md) | low | seed | Create checksum manifests for transfer validation and reproducibility. |
| [`cwl-on-slurm`](../skills/cwl-on-slurm/README.md) | medium | seed | Run small CWL workflows inside Slurm allocations with cwltool. |
| [`dataset-staging-to-scratch`](../skills/dataset-staging-to-scratch/README.md) | medium | seed | Stage inputs to scratch, run work, and collect outputs from Slurm jobs. |
| [`gatk-workflow-on-hpc`](../skills/gatk-workflow-on-hpc/README.md) | medium | seed | Plan and run GATK variant-calling workflows on shared HPC systems. |
| [`globus-transfer-dataset`](../skills/globus-transfer-dataset/README.md) | medium | seed | Stage large datasets with Globus transfer and verification steps. |
| [`large-file-archive-prepare`](../skills/large-file-archive-prepare/README.md) | medium | seed | Prepare large HPC datasets for archival, publication, or handoff. |
| [`nf-core-on-slurm`](../skills/nf-core-on-slurm/README.md) | medium | seed | Run nf-core Nextflow pipelines on Slurm with conservative HPC defaults. |
| [`quota-and-filesystem-triage`](../skills/quota-and-filesystem-triage/README.md) | low | seed | Diagnose quota, inode, and filesystem-space failures from user-visible evidence. |
| [`rsync-data-transfer`](../skills/rsync-data-transfer/README.md) | medium | seed | Transfer datasets with rsync dry-runs, resumable options, and validation hooks. |
| [`scratch-storage-management`](../skills/scratch-storage-management/README.md) | low | seed | Inspect scratch, project, and working-directory usage before HPC jobs. |
| [`wdl-on-slurm`](../skills/wdl-on-slurm/README.md) | medium | seed | Run small WDL workflows inside Slurm allocations with miniwdl. |

### Debugging

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`checkpoint-restart-workflow`](../skills/checkpoint-restart-workflow/README.md) | medium | seed | Structure long HPC jobs so they can resume after time limits or preemption. |
| [`compiler-mpi-matrix`](../skills/compiler-mpi-matrix/README.md) | low | seed | Check compiler, MPI wrapper, and module compatibility before building HPC codes. |
| [`gpu-memory-triage`](../skills/gpu-memory-triage/README.md) | low | seed | Distinguish GPU allocation, framework, and model memory failures. |
| [`gpu-sanity-check`](../skills/gpu-sanity-check/README.md) | medium | seed | Verify GPU allocation, runtime visibility, and basic framework access. |
| [`job-failure-triage`](../skills/job-failure-triage/README.md) | low | seed | Diagnose common HPC job failures from scheduler and log evidence. |
| [`module-environment-debug`](../skills/module-environment-debug/README.md) | low | seed | Diagnose module, compiler, MPI, and library path conflicts. |
| [`module-tree-health-check`](../skills/module-tree-health-check/README.md) | low | seed | Collect read-only evidence about visible HPC module tree health. |
| [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md) | medium | seed | Compile and run MPI sanity checks across allocated nodes. |
| [`nccl-diagnostics`](../skills/nccl-diagnostics/README.md) | medium | seed | Collect NCCL communication evidence for multi-GPU and multi-node jobs. |
| [`node-health-readonly-triage`](../skills/node-health-readonly-triage/README.md) | low | seed | Collect read-only Slurm node evidence for support triage. |
| [`performance-profile-basic`](../skills/performance-profile-basic/README.md) | low | seed | Collect first-pass performance evidence for an HPC workload. |
| [`quota-and-filesystem-triage`](../skills/quota-and-filesystem-triage/README.md) | low | seed | Diagnose quota, inode, and filesystem-space failures from user-visible evidence. |
| [`reproducible-run-capture`](../skills/reproducible-run-capture/README.md) | low | seed | Capture command, environment, provenance, and logs for reproducible HPC runs. |
| [`scratch-storage-management`](../skills/scratch-storage-management/README.md) | low | seed | Inspect scratch, project, and working-directory usage before HPC jobs. |
| [`slurm-efficiency-report`](../skills/slurm-efficiency-report/README.md) | low | seed | Summarize completed Slurm job efficiency from accounting data. |
| [`slurm-monitor-job`](../skills/slurm-monitor-job/README.md) | low | seed | Inspect Slurm job state, accounting records, and output paths. |
| [`slurm-pending-reason-triage`](../skills/slurm-pending-reason-triage/README.md) | low | seed | Explain why Slurm jobs are pending using read-only scheduler signals. |
| [`tensorboard-on-slurm`](../skills/tensorboard-on-slurm/README.md) | medium | seed | Run policy-aware TensorBoard monitors from short Slurm allocations. |

### Education

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`training-cluster-reset-checklist`](../skills/training-cluster-reset-checklist/README.md) | medium | seed | Prepare and review HPC training environments before and after workshops. |

### GPU

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`cp2k-on-slurm`](../skills/cp2k-on-slurm/README.md) | medium | seed | Run CP2K calculations on Slurm with MPI/OpenMP layout and restart planning. |
| [`deepspeed-on-slurm`](../skills/deepspeed-on-slurm/README.md) | medium | seed | Plan and smoke test DeepSpeed launches on Slurm GPU allocations. |
| [`gpu-memory-triage`](../skills/gpu-memory-triage/README.md) | low | seed | Distinguish GPU allocation, framework, and model memory failures. |
| [`gpu-sanity-check`](../skills/gpu-sanity-check/README.md) | medium | seed | Verify GPU allocation, runtime visibility, and basic framework access. |
| [`gromacs-on-slurm`](../skills/gromacs-on-slurm/README.md) | medium | seed | Run GROMACS jobs on Slurm with MPI, OpenMP, GPU, and checkpoint planning. |
| [`namd-on-slurm`](../skills/namd-on-slurm/README.md) | medium | seed | Run NAMD molecular dynamics jobs on Slurm with CPU/GPU and restart planning. |
| [`nccl-diagnostics`](../skills/nccl-diagnostics/README.md) | medium | seed | Collect NCCL communication evidence for multi-GPU and multi-node jobs. |
| [`pytorch-ddp-on-slurm`](../skills/pytorch-ddp-on-slurm/README.md) | medium | seed | Launch and verify PyTorch distributed data parallel jobs on Slurm. |
| [`ray-on-slurm`](../skills/ray-on-slurm/README.md) | medium | seed | Launch resource-bounded Ray clusters inside Slurm allocations. |

### Interactive

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`interactive-session`](../skills/interactive-session/README.md) | medium | seed | Start short interactive compute sessions for debugging and notebooks. |
| [`jupyter-on-slurm`](../skills/jupyter-on-slurm/README.md) | medium | seed | Launch Jupyter notebooks inside short Slurm compute allocations. |
| [`rstudio-on-slurm`](../skills/rstudio-on-slurm/README.md) | medium | seed | Launch policy-aware RStudio or Posit sessions from Slurm allocations. |
| [`streamlit-on-slurm`](../skills/streamlit-on-slurm/README.md) | medium | seed | Run policy-aware Streamlit apps from short Slurm compute allocations. |
| [`tensorboard-on-slurm`](../skills/tensorboard-on-slurm/README.md) | medium | seed | Run policy-aware TensorBoard monitors from short Slurm allocations. |
| [`vscode-tunnel-on-slurm`](../skills/vscode-tunnel-on-slurm/README.md) | medium | seed | Run VS Code Remote Tunnels from short Slurm compute allocations. |

### MPI

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`apptainer-mpi-on-slurm`](../skills/apptainer-mpi-on-slurm/README.md) | medium | seed | Run MPI applications from Apptainer containers inside Slurm allocations. |
| [`compiler-mpi-matrix`](../skills/compiler-mpi-matrix/README.md) | low | seed | Check compiler, MPI wrapper, and module compatibility before building HPC codes. |
| [`cp2k-on-slurm`](../skills/cp2k-on-slurm/README.md) | medium | seed | Run CP2K calculations on Slurm with MPI/OpenMP layout and restart planning. |
| [`gromacs-on-slurm`](../skills/gromacs-on-slurm/README.md) | medium | seed | Run GROMACS jobs on Slurm with MPI, OpenMP, GPU, and checkpoint planning. |
| [`lammps-on-slurm`](../skills/lammps-on-slurm/README.md) | medium | seed | Run LAMMPS molecular dynamics jobs on Slurm with MPI, GPU, and restart planning. |
| [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md) | medium | seed | Compile and run MPI sanity checks across allocated nodes. |
| [`mpi4py-on-slurm`](../skills/mpi4py-on-slurm/README.md) | medium | seed | Run mpi4py Python programs on Slurm with matching MPI and Python environments. |
| [`namd-on-slurm`](../skills/namd-on-slurm/README.md) | medium | seed | Run NAMD molecular dynamics jobs on Slurm with CPU/GPU and restart planning. |
| [`openfoam-on-slurm`](../skills/openfoam-on-slurm/README.md) | medium | seed | Run OpenFOAM CFD cases on Slurm with decomposition, MPI launch, and reconstruction planning. |
| [`quantum-espresso-on-slurm`](../skills/quantum-espresso-on-slurm/README.md) | medium | seed | Run Quantum ESPRESSO PWscf jobs on Slurm with MPI sizing and restart planning. |
| [`wrf-on-slurm`](../skills/wrf-on-slurm/README.md) | medium | seed | Run WRF real-data jobs on Slurm with MPI sizing, real.exe staging, restart, and I/O planning. |

### Performance

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`apptainer-mpi-on-slurm`](../skills/apptainer-mpi-on-slurm/README.md) | medium | seed | Run MPI applications from Apptainer containers inside Slurm allocations. |
| [`cp2k-on-slurm`](../skills/cp2k-on-slurm/README.md) | medium | seed | Run CP2K calculations on Slurm with MPI/OpenMP layout and restart planning. |
| [`gromacs-on-slurm`](../skills/gromacs-on-slurm/README.md) | medium | seed | Run GROMACS jobs on Slurm with MPI, OpenMP, GPU, and checkpoint planning. |
| [`lammps-on-slurm`](../skills/lammps-on-slurm/README.md) | medium | seed | Run LAMMPS molecular dynamics jobs on Slurm with MPI, GPU, and restart planning. |
| [`namd-on-slurm`](../skills/namd-on-slurm/README.md) | medium | seed | Run NAMD molecular dynamics jobs on Slurm with CPU/GPU and restart planning. |
| [`openfoam-on-slurm`](../skills/openfoam-on-slurm/README.md) | medium | seed | Run OpenFOAM CFD cases on Slurm with decomposition, MPI launch, and reconstruction planning. |
| [`openmp-thread-affinity`](../skills/openmp-thread-affinity/README.md) | medium | seed | Align OpenMP threads with Slurm CPU allocations and affinity settings. |
| [`performance-profile-basic`](../skills/performance-profile-basic/README.md) | low | seed | Collect first-pass performance evidence for an HPC workload. |
| [`quantum-espresso-on-slurm`](../skills/quantum-espresso-on-slurm/README.md) | medium | seed | Run Quantum ESPRESSO PWscf jobs on Slurm with MPI sizing and restart planning. |
| [`slurm-efficiency-report`](../skills/slurm-efficiency-report/README.md) | low | seed | Summarize completed Slurm job efficiency from accounting data. |
| [`slurm-resource-estimator`](../skills/slurm-resource-estimator/README.md) | low | seed | Estimate future Slurm resource requests from accounting history. |
| [`wrf-on-slurm`](../skills/wrf-on-slurm/README.md) | medium | seed | Run WRF real-data jobs on Slurm with MPI sizing, real.exe staging, restart, and I/O planning. |

### Scheduler

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`apptainer-mpi-on-slurm`](../skills/apptainer-mpi-on-slurm/README.md) | medium | seed | Run MPI applications from Apptainer containers inside Slurm allocations. |
| [`apptainer-run-container`](../skills/apptainer-run-container/README.md) | medium | seed | Run Apptainer containers safely on shared HPC systems. |
| [`blast-on-slurm`](../skills/blast-on-slurm/README.md) | medium | seed | Run local BLAST+ searches on Slurm with bounded smoke-test defaults. |
| [`checkpoint-restart-workflow`](../skills/checkpoint-restart-workflow/README.md) | medium | seed | Structure long HPC jobs so they can resume after time limits or preemption. |
| [`cluster-usage-report-readonly`](../skills/cluster-usage-report-readonly/README.md) | low | seed | Collect read-only Slurm usage evidence for facility support reports. |
| [`cp2k-on-slurm`](../skills/cp2k-on-slurm/README.md) | medium | seed | Run CP2K calculations on Slurm with MPI/OpenMP layout and restart planning. |
| [`cwl-on-slurm`](../skills/cwl-on-slurm/README.md) | medium | seed | Run small CWL workflows inside Slurm allocations with cwltool. |
| [`dask-jobqueue-on-slurm`](../skills/dask-jobqueue-on-slurm/README.md) | medium | seed | Launch Dask workers through Slurm with dask-jobqueue and bounded dry-run defaults. |
| [`dataset-staging-to-scratch`](../skills/dataset-staging-to-scratch/README.md) | medium | seed | Stage inputs to scratch, run work, and collect outputs from Slurm jobs. |
| [`deepspeed-on-slurm`](../skills/deepspeed-on-slurm/README.md) | medium | seed | Plan and smoke test DeepSpeed launches on Slurm GPU allocations. |
| [`gatk-workflow-on-hpc`](../skills/gatk-workflow-on-hpc/README.md) | medium | seed | Plan and run GATK variant-calling workflows on shared HPC systems. |
| [`gpu-sanity-check`](../skills/gpu-sanity-check/README.md) | medium | seed | Verify GPU allocation, runtime visibility, and basic framework access. |
| [`grid-engine-submit-job`](../skills/grid-engine-submit-job/README.md) | medium | seed | Generate safe Grid Engine qsub scripts for common HPC job shapes. |
| [`gromacs-on-slurm`](../skills/gromacs-on-slurm/README.md) | medium | seed | Run GROMACS jobs on Slurm with MPI, OpenMP, GPU, and checkpoint planning. |
| [`htcondor-submit-job`](../skills/htcondor-submit-job/README.md) | medium | seed | Generate safe HTCondor submit descriptions for common high-throughput job shapes. |
| [`interactive-session`](../skills/interactive-session/README.md) | medium | seed | Start short interactive compute sessions for debugging and notebooks. |
| [`job-failure-triage`](../skills/job-failure-triage/README.md) | low | seed | Diagnose common HPC job failures from scheduler and log evidence. |
| [`julia-on-slurm`](../skills/julia-on-slurm/README.md) | medium | seed | Run Julia scripts on Slurm with explicit depot, project, and thread settings. |
| [`jupyter-on-slurm`](../skills/jupyter-on-slurm/README.md) | medium | seed | Launch Jupyter notebooks inside short Slurm compute allocations. |
| [`lammps-on-slurm`](../skills/lammps-on-slurm/README.md) | medium | seed | Run LAMMPS molecular dynamics jobs on Slurm with MPI, GPU, and restart planning. |
| [`lsf-submit-job`](../skills/lsf-submit-job/README.md) | medium | seed | Generate safe IBM LSF bsub scripts for common HPC job shapes. |
| [`matlab-batch-on-slurm`](../skills/matlab-batch-on-slurm/README.md) | medium | seed | Run non-interactive MATLAB workloads on Slurm with explicit logs and license notes. |
| [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md) | medium | seed | Compile and run MPI sanity checks across allocated nodes. |
| [`mpi4py-on-slurm`](../skills/mpi4py-on-slurm/README.md) | medium | seed | Run mpi4py Python programs on Slurm with matching MPI and Python environments. |
| [`namd-on-slurm`](../skills/namd-on-slurm/README.md) | medium | seed | Run NAMD molecular dynamics jobs on Slurm with CPU/GPU and restart planning. |
| [`nccl-diagnostics`](../skills/nccl-diagnostics/README.md) | medium | seed | Collect NCCL communication evidence for multi-GPU and multi-node jobs. |
| [`nextflow-on-slurm`](../skills/nextflow-on-slurm/README.md) | medium | seed | Configure Nextflow pipelines to run through the Slurm executor. |
| [`nf-core-on-slurm`](../skills/nf-core-on-slurm/README.md) | medium | seed | Run nf-core Nextflow pipelines on Slurm with conservative HPC defaults. |
| [`node-health-readonly-triage`](../skills/node-health-readonly-triage/README.md) | low | seed | Collect read-only Slurm node evidence for support triage. |
| [`openfoam-on-slurm`](../skills/openfoam-on-slurm/README.md) | medium | seed | Run OpenFOAM CFD cases on Slurm with decomposition, MPI launch, and reconstruction planning. |
| [`openmp-thread-affinity`](../skills/openmp-thread-affinity/README.md) | medium | seed | Align OpenMP threads with Slurm CPU allocations and affinity settings. |
| [`pbs-submit-job`](../skills/pbs-submit-job/README.md) | medium | seed | Generate safe PBS or OpenPBS batch scripts for common HPC job shapes. |
| [`pytorch-ddp-on-slurm`](../skills/pytorch-ddp-on-slurm/README.md) | medium | seed | Launch and verify PyTorch distributed data parallel jobs on Slurm. |
| [`quantum-espresso-on-slurm`](../skills/quantum-espresso-on-slurm/README.md) | medium | seed | Run Quantum ESPRESSO PWscf jobs on Slurm with MPI sizing and restart planning. |
| [`ray-on-slurm`](../skills/ray-on-slurm/README.md) | medium | seed | Launch resource-bounded Ray clusters inside Slurm allocations. |
| [`rscript-on-slurm`](../skills/rscript-on-slurm/README.md) | medium | seed | Run R scripts on Slurm with explicit package-library and output controls. |
| [`rstudio-on-slurm`](../skills/rstudio-on-slurm/README.md) | medium | seed | Launch policy-aware RStudio or Posit sessions from Slurm allocations. |
| [`slurm-efficiency-report`](../skills/slurm-efficiency-report/README.md) | low | seed | Summarize completed Slurm job efficiency from accounting data. |
| [`slurm-job-array-patterns`](../skills/slurm-job-array-patterns/README.md) | medium | seed | Run parameter sweeps and many independent tasks with Slurm job arrays. |
| [`slurm-job-dependency-chain`](../skills/slurm-job-dependency-chain/README.md) | medium | seed | Chain multi-stage Slurm jobs with explicit dependencies. |
| [`slurm-monitor-job`](../skills/slurm-monitor-job/README.md) | low | seed | Inspect Slurm job state, accounting records, and output paths. |
| [`slurm-pending-reason-triage`](../skills/slurm-pending-reason-triage/README.md) | low | seed | Explain why Slurm jobs are pending using read-only scheduler signals. |
| [`slurm-resource-estimator`](../skills/slurm-resource-estimator/README.md) | low | seed | Estimate future Slurm resource requests from accounting history. |
| [`slurm-submit-job`](../skills/slurm-submit-job/README.md) | medium | seed | Generate safe Slurm batch scripts for common HPC job shapes. |
| [`snakemake-on-slurm`](../skills/snakemake-on-slurm/README.md) | medium | seed | Configure Snakemake workflows to submit jobs through Slurm. |
| [`streamlit-on-slurm`](../skills/streamlit-on-slurm/README.md) | medium | seed | Run policy-aware Streamlit apps from short Slurm compute allocations. |
| [`tensorboard-on-slurm`](../skills/tensorboard-on-slurm/README.md) | medium | seed | Run policy-aware TensorBoard monitors from short Slurm allocations. |
| [`training-cluster-reset-checklist`](../skills/training-cluster-reset-checklist/README.md) | medium | seed | Prepare and review HPC training environments before and after workshops. |
| [`vscode-tunnel-on-slurm`](../skills/vscode-tunnel-on-slurm/README.md) | medium | seed | Run VS Code Remote Tunnels from short Slurm compute allocations. |
| [`wdl-on-slurm`](../skills/wdl-on-slurm/README.md) | medium | seed | Run small WDL workflows inside Slurm allocations with miniwdl. |
| [`wrf-on-slurm`](../skills/wrf-on-slurm/README.md) | medium | seed | Run WRF real-data jobs on Slurm with MPI sizing, real.exe staging, restart, and I/O planning. |

### Software

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`compiler-mpi-matrix`](../skills/compiler-mpi-matrix/README.md) | low | seed | Check compiler, MPI wrapper, and module compatibility before building HPC codes. |
| [`conda-mamba-on-hpc`](../skills/conda-mamba-on-hpc/README.md) | medium | seed | Create Conda or Mamba environments while protecting shared HPC filesystems. |
| [`container-build-for-hpc`](../skills/container-build-for-hpc/README.md) | medium | seed | Plan and build Apptainer-compatible images for shared HPC systems. |
| [`dask-jobqueue-on-slurm`](../skills/dask-jobqueue-on-slurm/README.md) | medium | seed | Launch Dask workers through Slurm with dask-jobqueue and bounded dry-run defaults. |
| [`easybuild-install-software`](../skills/easybuild-install-software/README.md) | medium | seed | Install scientific software with EasyBuild and generated modules. |
| [`julia-on-slurm`](../skills/julia-on-slurm/README.md) | medium | seed | Run Julia scripts on Slurm with explicit depot, project, and thread settings. |
| [`matlab-batch-on-slurm`](../skills/matlab-batch-on-slurm/README.md) | medium | seed | Run non-interactive MATLAB workloads on Slurm with explicit logs and license notes. |
| [`module-environment-debug`](../skills/module-environment-debug/README.md) | low | seed | Diagnose module, compiler, MPI, and library path conflicts. |
| [`module-tree-health-check`](../skills/module-tree-health-check/README.md) | low | seed | Collect read-only evidence about visible HPC module tree health. |
| [`mpi4py-on-slurm`](../skills/mpi4py-on-slurm/README.md) | medium | seed | Run mpi4py Python programs on Slurm with matching MPI and Python environments. |
| [`python-virtualenv-on-hpc`](../skills/python-virtualenv-on-hpc/README.md) | low | seed | Create lightweight Python virtual environments with explicit HPC module assumptions. |
| [`ray-on-slurm`](../skills/ray-on-slurm/README.md) | medium | seed | Launch resource-bounded Ray clusters inside Slurm allocations. |
| [`reproducible-run-capture`](../skills/reproducible-run-capture/README.md) | low | seed | Capture command, environment, provenance, and logs for reproducible HPC runs. |
| [`rscript-on-slurm`](../skills/rscript-on-slurm/README.md) | medium | seed | Run R scripts on Slurm with explicit package-library and output controls. |
| [`rstudio-on-slurm`](../skills/rstudio-on-slurm/README.md) | medium | seed | Launch policy-aware RStudio or Posit sessions from Slurm allocations. |
| [`spack-environment-create`](../skills/spack-environment-create/README.md) | medium | seed | Create reproducible Spack environments for HPC software stacks. |
| [`streamlit-on-slurm`](../skills/streamlit-on-slurm/README.md) | medium | seed | Run policy-aware Streamlit apps from short Slurm compute allocations. |
| [`tensorboard-on-slurm`](../skills/tensorboard-on-slurm/README.md) | medium | seed | Run policy-aware TensorBoard monitors from short Slurm allocations. |
| [`vscode-tunnel-on-slurm`](../skills/vscode-tunnel-on-slurm/README.md) | medium | seed | Run VS Code Remote Tunnels from short Slurm compute allocations. |

### Workflow

| Skill | Risk | Maturity | Description |
| --- | --- | --- | --- |
| [`blast-on-slurm`](../skills/blast-on-slurm/README.md) | medium | seed | Run local BLAST+ searches on Slurm with bounded smoke-test defaults. |
| [`cwl-on-slurm`](../skills/cwl-on-slurm/README.md) | medium | seed | Run small CWL workflows inside Slurm allocations with cwltool. |
| [`dask-jobqueue-on-slurm`](../skills/dask-jobqueue-on-slurm/README.md) | medium | seed | Launch Dask workers through Slurm with dask-jobqueue and bounded dry-run defaults. |
| [`gatk-workflow-on-hpc`](../skills/gatk-workflow-on-hpc/README.md) | medium | seed | Plan and run GATK variant-calling workflows on shared HPC systems. |
| [`htcondor-submit-job`](../skills/htcondor-submit-job/README.md) | medium | seed | Generate safe HTCondor submit descriptions for common high-throughput job shapes. |
| [`nextflow-on-slurm`](../skills/nextflow-on-slurm/README.md) | medium | seed | Configure Nextflow pipelines to run through the Slurm executor. |
| [`nf-core-on-slurm`](../skills/nf-core-on-slurm/README.md) | medium | seed | Run nf-core Nextflow pipelines on Slurm with conservative HPC defaults. |
| [`slurm-job-dependency-chain`](../skills/slurm-job-dependency-chain/README.md) | medium | seed | Chain multi-stage Slurm jobs with explicit dependencies. |
| [`snakemake-on-slurm`](../skills/snakemake-on-slurm/README.md) | medium | seed | Configure Snakemake workflows to submit jobs through Slurm. |
| [`wdl-on-slurm`](../skills/wdl-on-slurm/README.md) | medium | seed | Run small WDL workflows inside Slurm allocations with miniwdl. |

## Collections

| Collection | Status | Skills | Audience | Description |
| --- | --- | ---: | --- | --- |
| [`ai-hpc`](../collections/ai-hpc.json) | draft | 14 | AI/HPC users, machine learning researchers, research software engineers, HPC support teams | Skills for launching, validating, monitoring, demoing, and troubleshooting distributed AI workloads on Slurm-backed HPC systems. |
| [`bioinformatics-workflows`](../collections/bioinformatics-workflows.json) | draft | 7 | bioinformatics teams, core facilities, genomics platform engineers | Domain skills for running reviewed nf-core, GATK, and BLAST bioinformatics workflows on Slurm-backed HPC systems. |
| [`containers`](../collections/containers.json) | draft | 7 | research software engineers, container users, HPC support teams | Skills for building, validating, running MPI containers, and staging data for containerized HPC workloads. |
| [`core-hpc`](../collections/core-hpc.json) | draft | 16 | new HPC users, research software engineers, support teams | Starter skills for Slurm jobs, arrays, dependency chains, pending reason triage, efficiency review, restartable workflows, notebooks, RStudio, IDE tunnels, OpenMP placement, debugging, and storage triage. |
| [`data-movement`](../collections/data-movement.json) | draft | 7 | data stewards, research groups, facility support teams | Skills for staging, transferring, validating, and managing research data on HPC storage. |
| [`facility-ops`](../collections/facility-ops.json) | draft | 4 | HPC support teams, facility maintainers, research computing operators | Read-only operational skills for usage reporting, pending reason triage, node triage, and module tree health. |
| [`gpu-mpi-performance`](../collections/gpu-mpi-performance.json) | draft | 14 | AI/HPC users, simulation teams, performance engineers | Skills for validating GPU allocations, GPU memory failures, TensorBoard training monitors, Ray, NCCL communication, DeepSpeed and PyTorch DDP launches, MPI, containerized MPI, and mpi4py launches, OpenMP placement, Slurm efficiency review, and first-pass performance evidence. |
| [`scheduler-basics`](../collections/scheduler-basics.json) | draft | 7 | new HPC users, training instructors, support teams, sites with mixed schedulers | Starter skills for submitting and comparing basic jobs across Slurm, PBS-style, LSF, HTCondor, and Grid Engine schedulers. |
| [`simulation-workflows`](../collections/simulation-workflows.json) | draft | 12 | simulation teams, computational scientists, performance engineers | Domain skills for MPI/GPU-heavy simulation, electronic-structure, CFD, and weather workloads on Slurm-backed HPC systems. |
| [`software-stacks`](../collections/software-stacks.json) | draft | 21 | research software engineers, HPC support teams, tool maintainers | Skills for debugging modules, checking module tree health, compiler/MPI compatibility, Python, TensorBoard, Streamlit, Ray, Dask, mpi4py, R, RStudio, Julia, MATLAB, Conda environments, IDE tunnels, containers, containerized MPI, and reproducible HPC software stacks. |
| [`training-onboarding`](../collections/training-onboarding.json) | draft | 16 | instructors, new HPC users, training cluster maintainers | Skills for teaching new HPC users, including Slurm jobs, notebooks, TensorBoard monitors, Streamlit apps, RStudio, IDE tunnels, Python, R, Julia, and MATLAB workloads, and workshop environments. |
| [`workflow-engines`](../collections/workflow-engines.json) | draft | 7 | pipeline authors, bioinformatics teams, workflow platform maintainers | Skills for launching portable workflow engines, CWL/WDL runs, Dask worker clusters, and lightweight Slurm dependency chains. |

## Site Adapters

| Adapter | Status | Scheduler | Description |
| --- | --- | --- | --- |
| [`example-campus-cluster`](../site-adapters/example-campus-cluster/README.md) | example | slurm | A non-production adapter showing how a site can map generic skills to local HPC policy. |

## Next Candidates

- Open OnDemand app templates.
- Transfer verification across storage tiers.
- Bioinformatics workflows for AlphaFold and single-cell analysis.
- Facility read-only reports for fairshare, partitions, and node health.
