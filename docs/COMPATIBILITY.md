# Compatibility Tables

This document is generated from `registry/index.json` by
`tools/build_compatibility.py`. Do not edit it by hand.

## Summary

| Signal | Count |
| --- | ---: |
| Skills | 64 |
| Collections | 12 |
| Site adapters | 1 |
| Schedulers | 9 |
| Categories | 12 |
| Tools | 113 |

## Scheduler Coverage

| Scheduler | Skills | Categories | Collections |
| --- | ---: | --- | --- |
| `grid-engine` | 1 | `scheduler` | `scheduler-basics` |
| `htcondor` | 1 | `scheduler`, `workflow` | `scheduler-basics` |
| `lsf` | 1 | `scheduler` | `scheduler-basics` |
| `openpbs` | 1 | `scheduler` | `scheduler-basics` |
| `pbs` | 1 | `scheduler` | `scheduler-basics` |
| `pbs-pro` | 1 | `scheduler` | `scheduler-basics` |
| `scheduler-agnostic` | 16 | `admin`, `containers`, `data`, `debugging`, `mpi`, `performance`, `software` | `ai-hpc`, `bioinformatics-workflows`, `containers`, `core-hpc`, `data-movement`, `facility-ops`, `gpu-mpi-performance`, `scheduler-basics`, `simulation-workflows`, `software-stacks`, `training-onboarding` |
| `sge` | 1 | `scheduler` | `scheduler-basics` |
| `slurm` | 44 | `admin`, `containers`, `data`, `debugging`, `education`, `gpu`, `interactive`, `mpi`, `performance`, `scheduler`, `software`, `workflow` | `ai-hpc`, `bioinformatics-workflows`, `containers`, `core-hpc`, `data-movement`, `facility-ops`, `gpu-mpi-performance`, `scheduler-basics`, `simulation-workflows`, `software-stacks`, `training-onboarding`, `workflow-engines` |
| `uge` | 1 | `scheduler` | `scheduler-basics` |

## Collection And Category Matrix

Counts show how many skills in each collection include each category.

| Collection | Skills | `admin` | `containers` | `data` | `debugging` | `education` | `gpu` | `interactive` | `mpi` | `performance` | `scheduler` | `software` | `workflow` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [`ai-hpc`](../collections/ai-hpc.json) | 12 | 0 | 1 | 1 | 6 | 0 | 6 | 0 | 0 | 1 | 10 | 3 | 1 |
| [`bioinformatics-workflows`](../collections/bioinformatics-workflows.json) | 7 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 5 |
| [`containers`](../collections/containers.json) | 7 | 0 | 3 | 2 | 2 | 0 | 1 | 0 | 1 | 1 | 4 | 2 | 0 |
| [`core-hpc`](../collections/core-hpc.json) | 14 | 0 | 0 | 2 | 7 | 0 | 0 | 2 | 0 | 3 | 12 | 0 | 1 |
| [`data-movement`](../collections/data-movement.json) | 7 | 0 | 0 | 7 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| [`facility-ops`](../collections/facility-ops.json) | 4 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 3 | 1 | 0 |
| [`gpu-mpi-performance`](../collections/gpu-mpi-performance.json) | 13 | 0 | 1 | 0 | 7 | 0 | 6 | 0 | 4 | 4 | 10 | 3 | 0 |
| [`scheduler-basics`](../collections/scheduler-basics.json) | 7 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 6 | 1 | 1 |
| [`simulation-workflows`](../collections/simulation-workflows.json) | 12 | 0 | 0 | 0 | 4 | 0 | 3 | 0 | 8 | 9 | 10 | 1 | 0 |
| [`software-stacks`](../collections/software-stacks.json) | 17 | 1 | 3 | 0 | 4 | 0 | 1 | 0 | 3 | 1 | 8 | 15 | 1 |
| [`training-onboarding`](../collections/training-onboarding.json) | 12 | 1 | 0 | 1 | 2 | 1 | 0 | 2 | 0 | 0 | 9 | 6 | 0 |
| [`workflow-engines`](../collections/workflow-engines.json) | 7 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 1 | 7 |

## Workflow Engine Coverage

| Area | Skills |
| --- | --- |
| Slurm dependencies | [`slurm-job-dependency-chain`](../skills/slurm-job-dependency-chain/README.md) |
| Dask | [`dask-jobqueue-on-slurm`](../skills/dask-jobqueue-on-slurm/README.md) |
| Ray | [`ray-on-slurm`](../skills/ray-on-slurm/README.md) |
| Nextflow and nf-core | [`nextflow-on-slurm`](../skills/nextflow-on-slurm/README.md), [`nf-core-on-slurm`](../skills/nf-core-on-slurm/README.md) |
| Snakemake | [`snakemake-on-slurm`](../skills/snakemake-on-slurm/README.md) |
| CWL | [`cwl-on-slurm`](../skills/cwl-on-slurm/README.md) |
| WDL | [`wdl-on-slurm`](../skills/wdl-on-slurm/README.md) |

## Software Stack And Container Coverage

| Area | Skills |
| --- | --- |
| Apptainer and Singularity | [`apptainer-mpi-on-slurm`](../skills/apptainer-mpi-on-slurm/README.md), [`apptainer-run-container`](../skills/apptainer-run-container/README.md), [`container-build-for-hpc`](../skills/container-build-for-hpc/README.md), [`nf-core-on-slurm`](../skills/nf-core-on-slurm/README.md) |
| Spack | [`spack-environment-create`](../skills/spack-environment-create/README.md) |
| EasyBuild | [`easybuild-install-software`](../skills/easybuild-install-software/README.md) |
| Conda and Mamba | [`conda-mamba-on-hpc`](../skills/conda-mamba-on-hpc/README.md) |
| Python | [`dask-jobqueue-on-slurm`](../skills/dask-jobqueue-on-slurm/README.md), [`deepspeed-on-slurm`](../skills/deepspeed-on-slurm/README.md), [`gpu-memory-triage`](../skills/gpu-memory-triage/README.md), [`jupyter-on-slurm`](../skills/jupyter-on-slurm/README.md), [`mpi4py-on-slurm`](../skills/mpi4py-on-slurm/README.md), [`python-virtualenv-on-hpc`](../skills/python-virtualenv-on-hpc/README.md), [`pytorch-ddp-on-slurm`](../skills/pytorch-ddp-on-slurm/README.md), [`ray-on-slurm`](../skills/ray-on-slurm/README.md) |
| R, Julia, and MATLAB | [`julia-on-slurm`](../skills/julia-on-slurm/README.md), [`matlab-batch-on-slurm`](../skills/matlab-batch-on-slurm/README.md), [`rscript-on-slurm`](../skills/rscript-on-slurm/README.md) |
| Compiler and MPI stacks | [`apptainer-mpi-on-slurm`](../skills/apptainer-mpi-on-slurm/README.md), [`compiler-mpi-matrix`](../skills/compiler-mpi-matrix/README.md), [`cp2k-on-slurm`](../skills/cp2k-on-slurm/README.md), [`grid-engine-submit-job`](../skills/grid-engine-submit-job/README.md), [`gromacs-on-slurm`](../skills/gromacs-on-slurm/README.md), [`lammps-on-slurm`](../skills/lammps-on-slurm/README.md), [`lsf-submit-job`](../skills/lsf-submit-job/README.md), [`module-environment-debug`](../skills/module-environment-debug/README.md), [`module-tree-health-check`](../skills/module-tree-health-check/README.md), [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md), [`mpi4py-on-slurm`](../skills/mpi4py-on-slurm/README.md), [`namd-on-slurm`](../skills/namd-on-slurm/README.md), [`openfoam-on-slurm`](../skills/openfoam-on-slurm/README.md), [`pbs-submit-job`](../skills/pbs-submit-job/README.md), [`quantum-espresso-on-slurm`](../skills/quantum-espresso-on-slurm/README.md), [`slurm-submit-job`](../skills/slurm-submit-job/README.md), [`wrf-on-slurm`](../skills/wrf-on-slurm/README.md) |

## Domain And Adoption Collections

| Collection | Skills | Dominant categories | Audience |
| --- | ---: | --- | --- |
| [`ai-hpc`](../collections/ai-hpc.json) | 12 | `scheduler` (10), `debugging` (6), `gpu` (6), `software` (3) | AI/HPC users, machine learning researchers, research software engineers, HPC support teams |
| [`bioinformatics-workflows`](../collections/bioinformatics-workflows.json) | 7 | `scheduler` (6), `data` (5), `workflow` (5) | bioinformatics teams, core facilities, genomics platform engineers |
| [`simulation-workflows`](../collections/simulation-workflows.json) | 12 | `scheduler` (10), `performance` (9), `mpi` (8), `debugging` (4) | simulation teams, computational scientists, performance engineers |
| [`data-movement`](../collections/data-movement.json) | 7 | `data` (7), `debugging` (2), `scheduler` (1) | data stewards, research groups, facility support teams |
| [`facility-ops`](../collections/facility-ops.json) | 4 | `admin` (3), `debugging` (3), `scheduler` (3), `software` (1) | HPC support teams, facility maintainers, research computing operators |
| [`training-onboarding`](../collections/training-onboarding.json) | 12 | `scheduler` (9), `software` (6), `debugging` (2), `interactive` (2) | instructors, new HPC users, training cluster maintainers |

## Tool Signals

Tools are declared by skill manifests. Counts are not installation checks;
they show where examples and wrappers expect a command or library.

### Common Tools

| Tool | Skills |
| --- | ---: |
| `sbatch` | 34 |
| `mkdir` | 29 |
| `date` | 24 |
| `hostname` | 21 |
| `module` | 19 |
| `srun` | 17 |
| `tee` | 17 |
| `grep` | 8 |
| `sort` | 8 |
| `test` | 8 |
| `pwd` | 7 |
| `sacct` | 7 |
| `env` | 6 |
| `nvidia-smi` | 6 |
| `scontrol` | 6 |
| `squeue` | 6 |
| `bash` | 5 |
| `python3` | 5 |
| `find` | 4 |
| `head` | 4 |
| `mpirun` | 4 |
| `tail` | 4 |
| `apptainer` | 3 |
| `awk` | 3 |
| `df` | 3 |
| `dirname` | 3 |
| `python` | 3 |
| `sed` | 3 |
| `sinfo` | 3 |
| `cat` | 2 |
| `cksum` | 2 |
| `command` | 2 |
| `cp` | 2 |
| `du` | 2 |
| `ldd` | 2 |
| `mpicc` | 2 |
| `nextflow` | 2 |
| `qstat` | 2 |
| `qsub` | 2 |
| `rocm-smi` | 2 |
| `rsync` | 2 |
| `sha256sum` | 2 |
| `shasum` | 2 |
| `ssh` | 2 |
| `which` | 2 |

### Specialized Single-Skill Tools

`all_reduce_perf`, `basename`, `bjobs`, `blastn`, `blockMesh`, `bsub`, `charmrun`, `clang`, `conda`, `condor_q`, `condor_rm`, `condor_submit`, `cp2k.psmp`, `cwltool`, `dask`, `dask_jobqueue`, `decomposePar`, `deepspeed`, `distributed`, `eb`, `gatk`, `gcc`, `git`, `globus`, `gmx`, `gmx_mpi`, `icoFoam`, `julia`, `jupyter`, `lmp`, `ln`, `lscpu`, `makeblastdb`, `mamba`, `matlab`, `micromamba`, `miniwdl`, `mpi4py`, `mpicxx`, `mpiexec`, `mpifort`, `namd2`, `ncdump`, `nproc`, `perf`, `pip`, `printenv`, `pw.x`, `qdel`, `quota`, `ray`, `real.exe`, `reconstructPar`, `Rscript`, `salloc`, `seff`, `singularity`, `sleep`, `snakemake`, `spack`, `sprio`, `sreport`, `tar`, `time`, `tr`, `uname`, `wc`, `wrf.exe`.
