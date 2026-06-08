# Collections

Collections group individual skills into practical adoption paths.

Use collections when a user asks for a workflow-oriented entry point instead of
a single skill. For example, a new user may start with `core-hpc`, while a
research software engineer building software stacks may start with
`software-stacks`.

## Seed Collections

- `core-hpc`: Slurm submission, arrays, failed-array retry planning,
  dependency chains, pending reason and maintenance reservation triage,
  QOS/account limit evidence, monitoring, resource estimation, OOM memory,
  time-limit, and node-failure triage,
  efficiency review,
  file descriptor triage, license-aware jobs, checkpoint/restart,
  preemption/requeue handling, failure triage, node-local scratch staging,
  shared project permissions, storage triage, OpenMP placement,
  notebooks, RStudio, IDE tunnels, and interactive sessions.
- `scheduler-basics`: Slurm, PBS/OpenPBS, LSF, HTCondor, and Grid Engine
  starter submission patterns plus array retry planning, failure triage, OOM
  memory triage, time-limit triage, node-failure triage, and reproducible run
  capture for sites comparing or teaching scheduler basics.
- `software-stacks`: modules, module tree health, compiler/MPI compatibility,
  CMake build preflight, parallel HDF5/NetCDF preflight, BLAS/OpenMP thread
  pools, license-aware jobs, reproducible run capture, Python virtual environments, Open OnDemand
  templates, TensorBoard monitors,
  Streamlit apps, Ray clusters, Dask Jobqueue,
  Parsl worker blocks, JAX distributed smoke tests, Hugging Face Accelerate
  launches, TensorFlow multi-worker smoke tests, mpi4py jobs, Rscript jobs,
  RStudio sessions, Julia jobs, MATLAB batch jobs, IDE tunnels, Conda/Mamba,
  container builds and runtime, Spack, and EasyBuild.
- `containers`: Apptainer-compatible image build planning, container runtime
  execution, containerized MPI launch patterns, GPU visibility checks, scratch
  staging, checksum manifests, and reproducible run capture for containerized
  HPC workloads.
- `workflow-engines`: lightweight Slurm dependency chains, array retry
  planning, CWL and WDL runs inside Slurm allocations, Dask worker clusters,
  Parsl worker blocks, file descriptor and time-limit triage, Nextflow,
  Snakemake, and nf-core on Slurm.
- `training-onboarding`: workshop preflight, Slurm basics, maintenance and
  reservation triage, array retry planning, time-limit and node-failure triage, file descriptor limits,
  BLAS/OpenMP thread pools, interactive sessions, Open OnDemand templates, notebooks,
  TensorBoard monitors, Streamlit apps, RStudio, IDE tunnels, Python/Conda
  environments, Rscript batch jobs, Julia batch jobs, MATLAB batch jobs,
  license-aware software use, module debugging, requeue-safe restart behavior,
  data staging, node-local scratch staging, shared project permissions, OOM
  memory triage, and failure triage for new users.
- `data-movement`: Globus, rsync, and object-storage transfers, checksum
  manifests, scratch staging, node-local scratch staging, archive preparation,
  Darshan I/O profile analysis, Lustre striping layout planning, IOR/MDTest
  storage smoke benchmarks, scratch inventory, filesystem quota triage, file
  descriptor triage, and shared project permissions triage.
- `ai-hpc`: GPU allocation checks, GPU binding diagnostics, CPU thread-pool
  control, file descriptor pressure, Ray clusters, Dask workers, JAX distributed
  smoke tests, Hugging Face Accelerate launches, TensorFlow multi-worker smoke
  tests, PyTorch DDP, DeepSpeed, NCCL diagnostics, GPU memory triage, TensorBoard monitors,
  Streamlit demos, container runtime execution, data staging, checkpoint/restart
  planning, reproducible run capture, and Slurm efficiency review for
  distributed AI workloads.
- `gpu-mpi-performance`: MPI launch checks, containerized MPI checks, mpi4py
  launch checks, MPI fabric diagnostics, MPI rank binding diagnostics, hybrid
  MPI/OpenMP layout checks, BLAS/OpenMP thread-pool control, CMake build preflight, parallel HDF5/NetCDF
  preflight, Darshan I/O profile analysis, Lustre striping layout planning,
  GPU binding diagnostics,
  compiler/MPI
  compatibility, GPU sanity checks, Ray cluster smoke tests, JAX distributed smoke tests,
  Hugging Face Accelerate launches, TensorFlow multi-worker smoke tests,
  GPU memory triage, TensorBoard monitors, PyTorch DDP smoke tests, NCCL
  diagnostics, DeepSpeed launch checks, OpenMP placement, Slurm efficiency
  review, storage smoke benchmarks, and basic profiling.
- `bioinformatics-workflows`: nf-core, GATK, BLAST, Nextflow, Snakemake, data
  staging, and checksum practices for genomics and core-facility workflows.
- `simulation-workflows`: GROMACS, LAMMPS, NAMD, Quantum ESPRESSO, CP2K,
  OpenFOAM, WRF, MPI launch checks, MPI fabric diagnostics, rank binding
  diagnostics, hybrid MPI/OpenMP layouts, CMake build preflight,
  parallel HDF5/NetCDF preflight, Darshan I/O profile analysis, Lustre
  striping layout planning, OpenMP placement, profiling, restart planning,
  storage smoke evidence, and
  reproducible run capture for simulation teams.
- `facility-ops`: read-only usage reporting, pending reason and maintenance
  triage, node triage, QOS/account limit evidence, OOM memory and time-limit
  triage, node-failure triage, file descriptor pressure, shared project
  permissions, and module tree health checks for HPC support teams and facility
  maintainers.

## Contribution Guidance

- Collections must reference existing skill ids.
- Keep the audience specific enough to guide discovery.
- Avoid duplicating skill documentation inside collection manifests.
- Use collections to tell users where to start, not to replace categories or
  tags.
