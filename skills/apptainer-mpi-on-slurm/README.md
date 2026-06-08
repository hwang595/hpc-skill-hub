# Apptainer MPI On Slurm

Use this skill when an MPI application is packaged in an Apptainer or
Singularity image and must run inside a Slurm allocation.

MPI containers are more site-sensitive than single-process containers. Confirm
the launch model with local support before scaling beyond a smoke test.

## Examples

```bash
bash examples/mpi-preflight.sh /path/to/image.sif /path/in/container/app
sbatch examples/hybrid-mpi.sbatch
sbatch examples/bind-host-mpi.sbatch
```

## Adaptation Points

- Replace `<account>`, `<partition>`, `<image.sif>`, and `<container-app>`.
- Use the launch command recommended by the site: often `srun` on Slurm-native
  systems, or host `mpirun` for a documented bind-model workflow.
- Keep host MPI and container MPI compatible when using the hybrid model.
- Bind only required data, scratch, license, and MPI paths.
- Start with one node or a tiny two-node job before running production scale.

## Preflight Checklist

- Host `mpirun`, `srun`, and MPI wrapper versions are recorded.
- Container has the expected application binary and MPI runtime.
- Required input and output directories are explicitly bound.
- Rank count equals `SLURM_NTASKS` or the requested host launcher size.
- The output captures hostname, rank mapping, and relevant MPI variables.

## Safety Notes

This skill is `medium` risk because examples allocate compute nodes, launch MPI
ranks, and write through bound host directories. Treat bind paths as writeable
unless they are explicitly mounted read-only.
