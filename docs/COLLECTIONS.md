# Collections

Collections group individual skills into practical adoption paths.

Use collections when a user asks for a workflow-oriented entry point instead of
a single skill. For example, a new user may start with `core-hpc`, while a
research software engineer building software stacks may start with
`software-stacks`.

## Seed Collections

- `core-hpc`: Slurm submission, arrays, monitoring, resource estimation,
  checkpoint/restart, failure triage, storage triage, OpenMP placement,
  notebooks, and interactive sessions.
- `software-stacks`: modules, compiler/MPI compatibility, reproducible run
  capture, Python virtual environments, Conda/Mamba, container builds and
  runtime, Spack, and EasyBuild.
- `workflow-engines`: Nextflow, Snakemake, and nf-core on Slurm.
- `data-movement`: Globus and rsync transfers, checksum manifests, scratch
  staging, archive preparation, scratch inventory, and filesystem quota triage.
- `gpu-mpi-performance`: MPI launch checks, compiler/MPI compatibility, GPU
  sanity checks, GPU memory triage, PyTorch DDP smoke tests, NCCL diagnostics,
  DeepSpeed launch checks, OpenMP placement, and basic profiling.
- `bioinformatics-workflows`: nf-core, GATK, Nextflow, Snakemake, data staging,
  and checksum practices for genomics and core-facility workflows.
- `simulation-workflows`: LAMMPS, MPI launch checks, OpenMP placement,
  profiling, restart planning, and reproducible run capture for simulation
  teams.

## Contribution Guidance

- Collections must reference existing skill ids.
- Keep the audience specific enough to guide discovery.
- Avoid duplicating skill documentation inside collection manifests.
- Use collections to tell users where to start, not to replace categories or
  tags.
