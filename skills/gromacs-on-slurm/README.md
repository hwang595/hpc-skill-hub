# GROMACS On Slurm

Use this skill when a molecular dynamics simulation needs a conservative
GROMACS launch pattern on a Slurm cluster, especially when choosing MPI ranks,
OpenMP threads, and GPU offload settings.

## Example

Create a launch plan:

```bash
bash examples/gromacs-smoke.sbatch
```

After loading a site-approved GROMACS module or container, run the tiny smoke
test explicitly:

```bash
RUN_GROMACS=1 GMX_CMD=gmx_mpi bash examples/gromacs-smoke.sbatch
```

## Pattern

- Start with a tiny input or reduced production system.
- Record Slurm layout, `GMX_CMD`, MPI ranks, OpenMP threads, GPU flags,
  checkpoint cadence, and output paths before scaling.
- Use `gmx_mpi` with `srun` for MPI-enabled builds, or a site-supported wrapper
  for thread-MPI builds.
- Add reviewed GPU offload settings with structured variables such as
  `GMX_NB=gpu`, `GMX_PME=gpu`, and `GMX_GPU_ID=0`.
- Keep `.cpt`, `.log`, `.edr`, `.xtc`, and run records on durable storage.
- Treat GPU flags as build- and system-specific; compare CPU/GPU and rank/thread
  layouts with timing evidence.

## Safety Notes

This skill is `medium` risk because GROMACS jobs can consume many CPU/GPU hours
and produce large trajectories. The example defaults to plan-only mode and only
runs `grompp` and `mdrun` when `RUN_GROMACS=1` is set.

## Success Criteria

- The plan records executable, input files, Slurm layout, OpenMP threads, GPU
  flags, TPR path, checkpoint path, and mdrun command.
- A small smoke test runs before production input is submitted.
- Checkpoint cadence and output volume are reviewed before long jobs.
- Scaling decisions are paired with performance evidence and reproducible run
  capture.
