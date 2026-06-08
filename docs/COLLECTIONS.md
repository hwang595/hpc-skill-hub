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
- `software-stacks`: modules, containers, Spack, and EasyBuild.
- `workflow-engines`: Nextflow and Snakemake on Slurm.
- `data-movement`: Globus dataset transfer, scratch inventory, and filesystem
  quota triage.
- `gpu-mpi-performance`: MPI, GPU sanity checks, OpenMP placement, and basic
  profiling.

## Contribution Guidance

- Collections must reference existing skill ids.
- Keep the audience specific enough to guide discovery.
- Avoid duplicating skill documentation inside collection manifests.
- Use collections to tell users where to start, not to replace categories or
  tags.
