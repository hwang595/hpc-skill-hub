# Collections

Collections group individual skills into practical adoption paths.

Use collections when a user asks for a workflow-oriented entry point instead of
a single skill. For example, a new user may start with `core-hpc`, while a
research software engineer building software stacks may start with
`software-stacks`.

## Seed Collections

- `core-hpc`: Slurm submission, arrays, dependency chains, pending reason
  triage, monitoring, resource estimation, efficiency review,
  checkpoint/restart, failure triage, storage triage, OpenMP placement,
  notebooks, and interactive sessions.
- `scheduler-basics`: Slurm, PBS/OpenPBS, LSF, HTCondor, and Grid Engine
  starter submission patterns plus failure triage and reproducible run capture
  for sites comparing or teaching scheduler basics.
- `software-stacks`: modules, module tree health, compiler/MPI compatibility,
  reproducible run capture, Python virtual environments, Ray clusters, Dask
  Jobqueue, mpi4py jobs, Rscript jobs, Julia jobs, MATLAB batch jobs, Conda/Mamba,
  container builds and runtime, Spack, and EasyBuild.
- `containers`: Apptainer-compatible image build planning, container runtime
  execution, containerized MPI launch patterns, GPU visibility checks, scratch
  staging, checksum manifests, and reproducible run capture for containerized
  HPC workloads.
- `workflow-engines`: lightweight Slurm dependency chains, CWL and WDL runs
  inside Slurm allocations, Dask worker clusters, Nextflow, Snakemake, and
  nf-core on Slurm.
- `training-onboarding`: workshop preflight, Slurm basics, interactive
  sessions, notebooks, Python/Conda environments, Rscript batch jobs, Julia
  batch jobs, MATLAB batch jobs, module debugging, data staging, and failure
  triage for new users.
- `data-movement`: Globus and rsync transfers, checksum manifests, scratch
  staging, archive preparation, scratch inventory, and filesystem quota triage.
- `ai-hpc`: GPU allocation checks, Ray clusters, Dask workers, PyTorch DDP,
  DeepSpeed, NCCL diagnostics, GPU memory triage, container runtime execution,
  data staging, checkpoint/restart planning, reproducible run capture, and
  Slurm efficiency review for distributed AI workloads.
- `gpu-mpi-performance`: MPI launch checks, containerized MPI checks, mpi4py
  launch checks, compiler/MPI compatibility, GPU sanity checks, Ray cluster
  smoke tests, GPU memory triage, PyTorch DDP smoke tests, NCCL diagnostics,
  DeepSpeed launch checks, OpenMP placement, Slurm efficiency review, and basic
  profiling.
- `bioinformatics-workflows`: nf-core, GATK, BLAST, Nextflow, Snakemake, data
  staging, and checksum practices for genomics and core-facility workflows.
- `simulation-workflows`: GROMACS, LAMMPS, NAMD, Quantum ESPRESSO, CP2K,
  OpenFOAM, WRF, MPI launch checks, OpenMP placement, profiling, restart
  planning, and reproducible run capture for simulation teams.
- `facility-ops`: read-only usage reporting, pending reason triage, node
  triage, and module tree health checks for HPC support teams and facility
  maintainers.

## Contribution Guidance

- Collections must reference existing skill ids.
- Keep the audience specific enough to guide discovery.
- Avoid duplicating skill documentation inside collection manifests.
- Use collections to tell users where to start, not to replace categories or
  tags.
