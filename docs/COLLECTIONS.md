# Collections

Collections group individual skills into practical adoption paths.

Use collections when a user asks for a workflow-oriented entry point instead of
a single skill. For example, a new user may start with `core-hpc`, while a
research software engineer building software stacks may start with
`software-stacks`.

## Seed Collections

- `core-hpc`: Slurm submission, arrays, dependency chains, pending reason
  triage, monitoring, resource estimation, efficiency review,
  license-aware jobs, checkpoint/restart, failure triage, storage triage,
  OpenMP placement, notebooks, RStudio, IDE tunnels, and interactive sessions.
- `scheduler-basics`: Slurm, PBS/OpenPBS, LSF, HTCondor, and Grid Engine
  starter submission patterns plus failure triage and reproducible run capture
  for sites comparing or teaching scheduler basics.
- `software-stacks`: modules, module tree health, compiler/MPI compatibility,
  license-aware jobs, reproducible run capture, Python virtual environments, Open OnDemand
  templates, TensorBoard monitors, Streamlit apps, Ray clusters, Dask Jobqueue,
  Parsl worker blocks, JAX distributed smoke tests, Hugging Face Accelerate
  launches, TensorFlow multi-worker smoke tests, mpi4py jobs, Rscript jobs,
  RStudio sessions, Julia jobs, MATLAB batch jobs, IDE tunnels, Conda/Mamba,
  container builds and runtime, Spack, and EasyBuild.
- `containers`: Apptainer-compatible image build planning, container runtime
  execution, containerized MPI launch patterns, GPU visibility checks, scratch
  staging, checksum manifests, and reproducible run capture for containerized
  HPC workloads.
- `workflow-engines`: lightweight Slurm dependency chains, CWL and WDL runs
  inside Slurm allocations, Dask worker clusters, Parsl worker blocks, Nextflow,
  Snakemake, and nf-core on Slurm.
- `training-onboarding`: workshop preflight, Slurm basics, interactive
  sessions, Open OnDemand templates, notebooks, TensorBoard monitors, Streamlit
  apps, RStudio, IDE tunnels, Python/Conda environments, Rscript batch jobs,
  Julia batch jobs, MATLAB batch jobs, license-aware software use, module
  debugging, data staging, and failure triage for new users.
- `data-movement`: Globus, rsync, and object-storage transfers, checksum
  manifests, scratch staging, archive preparation, IOR/MDTest storage smoke
  benchmarks, scratch inventory, and filesystem quota triage.
- `ai-hpc`: GPU allocation checks, Ray clusters, Dask workers, JAX distributed
  smoke tests, Hugging Face Accelerate launches, TensorFlow multi-worker smoke
  tests, PyTorch DDP, DeepSpeed, NCCL diagnostics, GPU memory triage, TensorBoard monitors,
  Streamlit demos, container runtime execution, data staging, checkpoint/restart
  planning, reproducible run capture, and Slurm efficiency review for
  distributed AI workloads.
- `gpu-mpi-performance`: MPI launch checks, containerized MPI checks, mpi4py
  launch checks, MPI rank binding diagnostics, hybrid MPI/OpenMP layout checks,
  compiler/MPI compatibility, GPU sanity checks, Ray cluster smoke tests, JAX distributed smoke tests,
  Hugging Face Accelerate launches, TensorFlow multi-worker smoke tests,
  GPU memory triage, TensorBoard monitors, PyTorch DDP smoke tests, NCCL
  diagnostics, DeepSpeed launch checks, OpenMP placement, Slurm efficiency
  review, storage smoke benchmarks, and basic profiling.
- `bioinformatics-workflows`: nf-core, GATK, BLAST, Nextflow, Snakemake, data
  staging, and checksum practices for genomics and core-facility workflows.
- `simulation-workflows`: GROMACS, LAMMPS, NAMD, Quantum ESPRESSO, CP2K,
  OpenFOAM, WRF, MPI launch checks, rank binding diagnostics, hybrid
  MPI/OpenMP layouts, OpenMP placement, profiling, restart planning, storage
  smoke evidence, and reproducible run capture for simulation teams.
- `facility-ops`: read-only usage reporting, pending reason triage, node
  triage, and module tree health checks for HPC support teams and facility
  maintainers.

## Contribution Guidance

- Collections must reference existing skill ids.
- Keep the audience specific enough to guide discovery.
- Avoid duplicating skill documentation inside collection manifests.
- Use collections to tell users where to start, not to replace categories or
  tags.
