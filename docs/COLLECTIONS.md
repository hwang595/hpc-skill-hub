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
- `software-stacks`: modules, module tree health, compiler/MPI compatibility,
  reproducible run capture, Python virtual environments, Conda/Mamba,
  container builds and runtime, Spack, and EasyBuild.
- `workflow-engines`: lightweight Slurm dependency chains, Nextflow,
  Snakemake, and nf-core on Slurm.
- `training-onboarding`: workshop preflight, Slurm basics, interactive
  sessions, notebooks, Python/Conda environments, module debugging, data
  staging, and failure triage for new users.
- `data-movement`: Globus and rsync transfers, checksum manifests, scratch
  staging, archive preparation, scratch inventory, and filesystem quota triage.
- `gpu-mpi-performance`: MPI launch checks, compiler/MPI compatibility, GPU
  sanity checks, GPU memory triage, PyTorch DDP smoke tests, NCCL diagnostics,
  DeepSpeed launch checks, OpenMP placement, Slurm efficiency review, and basic
  profiling.
- `bioinformatics-workflows`: nf-core, GATK, Nextflow, Snakemake, data staging,
  and checksum practices for genomics and core-facility workflows.
- `simulation-workflows`: GROMACS, LAMMPS, OpenFOAM, WRF, MPI launch checks,
  OpenMP placement, profiling, restart planning, and reproducible run capture
  for simulation teams.
- `facility-ops`: read-only usage reporting, pending reason triage, node
  triage, and module tree health checks for HPC support teams and facility
  maintainers.

## Contribution Guidance

- Collections must reference existing skill ids.
- Keep the audience specific enough to guide discovery.
- Avoid duplicating skill documentation inside collection manifests.
- Use collections to tell users where to start, not to replace categories or
  tags.
