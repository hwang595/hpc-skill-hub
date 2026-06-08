# Compatibility Tables

This document is generated from `registry/index.json` by
`tools/build_compatibility.py`. Do not edit it by hand.

## Summary

| Signal | Count |
| --- | ---: |
| Skills | 91 |
| Collections | 12 |
| Site adapters | 2 |
| Schedulers | 9 |
| Categories | 12 |
| Tools | 157 |

## Scheduler Coverage

| Scheduler | Skills | Categories | Collections |
| --- | ---: | --- | --- |
| `grid-engine` | 1 | `scheduler` | `scheduler-basics` |
| `htcondor` | 1 | `scheduler`, `workflow` | `scheduler-basics` |
| `lsf` | 1 | `scheduler` | `scheduler-basics` |
| `openpbs` | 1 | `scheduler` | `scheduler-basics` |
| `pbs` | 1 | `scheduler` | `scheduler-basics` |
| `pbs-pro` | 1 | `scheduler` | `scheduler-basics` |
| `scheduler-agnostic` | 21 | `admin`, `containers`, `data`, `debugging`, `mpi`, `performance`, `software` | `ai-hpc`, `bioinformatics-workflows`, `containers`, `core-hpc`, `data-movement`, `facility-ops`, `gpu-mpi-performance`, `scheduler-basics`, `simulation-workflows`, `software-stacks`, `training-onboarding` |
| `sge` | 1 | `scheduler` | `scheduler-basics` |
| `slurm` | 66 | `admin`, `containers`, `data`, `debugging`, `education`, `gpu`, `interactive`, `mpi`, `performance`, `scheduler`, `software`, `workflow` | `ai-hpc`, `bioinformatics-workflows`, `containers`, `core-hpc`, `data-movement`, `facility-ops`, `gpu-mpi-performance`, `scheduler-basics`, `simulation-workflows`, `software-stacks`, `training-onboarding`, `workflow-engines` |
| `uge` | 1 | `scheduler` | `scheduler-basics` |

## Collection And Category Matrix

Counts show how many skills in each collection include each category.

| Collection | Skills | `admin` | `containers` | `data` | `debugging` | `education` | `gpu` | `interactive` | `mpi` | `performance` | `scheduler` | `software` | `workflow` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [`ai-hpc`](../collections/ai-hpc.json) | 18 | 0 | 1 | 1 | 8 | 0 | 10 | 2 | 0 | 2 | 16 | 8 | 1 |
| [`bioinformatics-workflows`](../collections/bioinformatics-workflows.json) | 7 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 5 |
| [`containers`](../collections/containers.json) | 7 | 0 | 3 | 2 | 2 | 0 | 1 | 0 | 1 | 1 | 4 | 2 | 0 |
| [`core-hpc`](../collections/core-hpc.json) | 24 | 3 | 0 | 4 | 15 | 0 | 0 | 4 | 0 | 4 | 21 | 3 | 2 |
| [`data-movement`](../collections/data-movement.json) | 13 | 1 | 0 | 13 | 6 | 0 | 0 | 0 | 2 | 3 | 3 | 0 | 0 |
| [`facility-ops`](../collections/facility-ops.json) | 8 | 6 | 0 | 1 | 7 | 0 | 0 | 0 | 0 | 1 | 6 | 1 | 0 |
| [`gpu-mpi-performance`](../collections/gpu-mpi-performance.json) | 26 | 0 | 1 | 4 | 15 | 0 | 10 | 1 | 11 | 12 | 19 | 9 | 0 |
| [`scheduler-basics`](../collections/scheduler-basics.json) | 9 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 1 | 8 | 1 | 2 |
| [`simulation-workflows`](../collections/simulation-workflows.json) | 20 | 0 | 0 | 4 | 10 | 0 | 3 | 0 | 15 | 16 | 14 | 3 | 0 |
| [`software-stacks`](../collections/software-stacks.json) | 29 | 1 | 3 | 1 | 7 | 1 | 4 | 5 | 5 | 2 | 18 | 27 | 2 |
| [`training-onboarding`](../collections/training-onboarding.json) | 24 | 3 | 0 | 3 | 10 | 2 | 0 | 7 | 0 | 1 | 20 | 12 | 1 |
| [`workflow-engines`](../collections/workflow-engines.json) | 9 | 0 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 9 | 2 | 9 |

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
| Python | [`dask-jobqueue-on-slurm`](../skills/dask-jobqueue-on-slurm/README.md), [`deepspeed-on-slurm`](../skills/deepspeed-on-slurm/README.md), [`gpu-memory-triage`](../skills/gpu-memory-triage/README.md), [`huggingface-accelerate-on-slurm`](../skills/huggingface-accelerate-on-slurm/README.md), [`ior-mdtest-storage-smoke`](../skills/ior-mdtest-storage-smoke/README.md), [`jax-distributed-on-slurm`](../skills/jax-distributed-on-slurm/README.md), [`jupyter-on-slurm`](../skills/jupyter-on-slurm/README.md), [`mpi4py-on-slurm`](../skills/mpi4py-on-slurm/README.md), [`parsl-on-slurm`](../skills/parsl-on-slurm/README.md), [`python-virtualenv-on-hpc`](../skills/python-virtualenv-on-hpc/README.md), [`pytorch-ddp-on-slurm`](../skills/pytorch-ddp-on-slurm/README.md), [`ray-on-slurm`](../skills/ray-on-slurm/README.md), [`slurm-gpu-binding-diagnostics`](../skills/slurm-gpu-binding-diagnostics/README.md), [`streamlit-on-slurm`](../skills/streamlit-on-slurm/README.md), [`tensorboard-on-slurm`](../skills/tensorboard-on-slurm/README.md), [`tensorflow-multiworker-on-slurm`](../skills/tensorflow-multiworker-on-slurm/README.md) |
| R, Julia, and MATLAB | [`julia-on-slurm`](../skills/julia-on-slurm/README.md), [`matlab-batch-on-slurm`](../skills/matlab-batch-on-slurm/README.md), [`rscript-on-slurm`](../skills/rscript-on-slurm/README.md) |
| Compiler and MPI stacks | [`apptainer-mpi-on-slurm`](../skills/apptainer-mpi-on-slurm/README.md), [`cmake-hpc-build-preflight`](../skills/cmake-hpc-build-preflight/README.md), [`compiler-mpi-matrix`](../skills/compiler-mpi-matrix/README.md), [`cp2k-on-slurm`](../skills/cp2k-on-slurm/README.md), [`darshan-io-profile-analysis`](../skills/darshan-io-profile-analysis/README.md), [`grid-engine-submit-job`](../skills/grid-engine-submit-job/README.md), [`gromacs-on-slurm`](../skills/gromacs-on-slurm/README.md), [`hybrid-mpi-openmp-slurm`](../skills/hybrid-mpi-openmp-slurm/README.md), [`ior-mdtest-storage-smoke`](../skills/ior-mdtest-storage-smoke/README.md), [`lammps-on-slurm`](../skills/lammps-on-slurm/README.md), [`lsf-submit-job`](../skills/lsf-submit-job/README.md), [`module-environment-debug`](../skills/module-environment-debug/README.md), [`module-tree-health-check`](../skills/module-tree-health-check/README.md), [`mpi-fabric-diagnostics`](../skills/mpi-fabric-diagnostics/README.md), [`mpi-hello-and-benchmark`](../skills/mpi-hello-and-benchmark/README.md), [`mpi-rank-binding-diagnostics`](../skills/mpi-rank-binding-diagnostics/README.md), [`mpi4py-on-slurm`](../skills/mpi4py-on-slurm/README.md), [`namd-on-slurm`](../skills/namd-on-slurm/README.md), [`openfoam-on-slurm`](../skills/openfoam-on-slurm/README.md), [`parallel-hdf5-netcdf-preflight`](../skills/parallel-hdf5-netcdf-preflight/README.md), [`pbs-submit-job`](../skills/pbs-submit-job/README.md), [`quantum-espresso-on-slurm`](../skills/quantum-espresso-on-slurm/README.md), [`slurm-submit-job`](../skills/slurm-submit-job/README.md), [`wrf-on-slurm`](../skills/wrf-on-slurm/README.md) |

## Domain And Adoption Collections

| Collection | Skills | Dominant categories | Audience |
| --- | ---: | --- | --- |
| [`ai-hpc`](../collections/ai-hpc.json) | 18 | `scheduler` (16), `gpu` (10), `debugging` (8), `software` (8) | AI/HPC users, machine learning researchers, research software engineers, HPC support teams |
| [`bioinformatics-workflows`](../collections/bioinformatics-workflows.json) | 7 | `scheduler` (6), `data` (5), `workflow` (5) | bioinformatics teams, core facilities, genomics platform engineers |
| [`simulation-workflows`](../collections/simulation-workflows.json) | 20 | `performance` (16), `mpi` (15), `scheduler` (14), `debugging` (10) | simulation teams, computational scientists, performance engineers |
| [`data-movement`](../collections/data-movement.json) | 13 | `data` (13), `debugging` (6), `performance` (3), `scheduler` (3) | data stewards, research groups, facility support teams |
| [`facility-ops`](../collections/facility-ops.json) | 8 | `debugging` (7), `admin` (6), `scheduler` (6), `data` (1) | HPC support teams, facility maintainers, research computing operators |
| [`training-onboarding`](../collections/training-onboarding.json) | 24 | `scheduler` (20), `software` (12), `debugging` (10), `interactive` (7) | instructors, new HPC users, training cluster maintainers |

## Tool Signals

Tools are declared by skill manifests. Counts are not installation checks;
they show where examples and wrappers expect a command or library.

### Common Tools

| Tool | Skills |
| --- | ---: |
| `sbatch` | 49 |
| `mkdir` | 40 |
| `date` | 37 |
| `srun` | 26 |
| `hostname` | 25 |
| `module` | 25 |
| `tee` | 24 |
| `bash` | 17 |
| `scontrol` | 14 |
| `grep` | 12 |
| `python3` | 12 |
| `squeue` | 11 |
| `nvidia-smi` | 10 |
| `sort` | 10 |
| `sacct` | 9 |
| `test` | 9 |
| `find` | 7 |
| `mpicc` | 7 |
| `pwd` | 7 |
| `tail` | 7 |
| `df` | 6 |
| `env` | 6 |
| `head` | 5 |
| `ssh` | 5 |
| `awk` | 4 |
| `dirname` | 4 |
| `mpirun` | 4 |
| `python` | 4 |
| `sed` | 4 |
| `sinfo` | 4 |
| `apptainer` | 3 |
| `cat` | 3 |
| `cp` | 3 |
| `lscpu` | 3 |
| `rocm-smi` | 3 |
| `rsync` | 3 |
| `cksum` | 2 |
| `command` | 2 |
| `du` | 2 |
| `ldd` | 2 |
| `mpicxx` | 2 |
| `mpifort` | 2 |
| `ncdump` | 2 |
| `nextflow` | 2 |
| `qstat` | 2 |
| `qsub` | 2 |
| `rm` | 2 |
| `seff` | 2 |
| `sha256sum` | 2 |
| `shasum` | 2 |
| `sleep` | 2 |
| `sprio` | 2 |
| `stat` | 2 |
| `which` | 2 |

### Specialized Single-Skill Tools

`accelerate`, `all_reduce_perf`, `aws`, `basename`, `bjobs`, `blastn`, `blockMesh`, `bsub`, `charmrun`, `clang`, `cmake`, `code`, `conda`, `condor_q`, `condor_rm`, `condor_submit`, `cp2k.psmp`, `ctest`, `cwltool`, `darshan-config`, `darshan-dxt-parser`, `darshan-job-summary.pl`, `darshan-parser`, `darshan-summary-per-file.sh`, `dask`, `dask_jobqueue`, `decomposePar`, `deepspeed`, `distributed`, `eb`, `fi_info`, `gatk`, `gcc`, `getfacl`, `git`, `globus`, `gmx`, `gmx_mpi`, `h5cc`, `h5dump`, `h5pcc`, `hwloc-ls`, `ibv_devinfo`, `icoFoam`, `id`, `ior`, `julia`, `jupyter`, `lfs`, `lmp`, `lmutil`, `ln`, `ls`, `make`, `makeblastdb`, `mamba`, `matlab`, `mdtest`, `micromamba`, `miniwdl`, `mktemp`, `mpi4py`, `mpiexec`, `namd2`, `namei`, `nc-config`, `ninja`, `nproc`, `numactl`, `ompi_info`, `Open OnDemand`, `parsl`, `perf`, `pip`, `printenv`, `pw.x`, `qdel`, `quota`, `R`, `ray`, `rclone`, `real.exe`, `reconstructPar`, `Rscript`, `rserver`, `sacctmgr`, `salloc`, `scancel`, `singularity`, `snakemake`, `spack`, `sreport`, `sshare`, `streamlit`, `tar`, `tensorboard`, `time`, `touch`, `tr`, `ucx_info`, `uname`, `wc`, `wrf.exe`.
