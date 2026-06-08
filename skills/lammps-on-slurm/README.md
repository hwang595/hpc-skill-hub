# LAMMPS On Slurm

Use this skill when a molecular dynamics simulation needs a conservative
LAMMPS launch pattern on a Slurm cluster.

## Example

Create a launch plan:

```bash
bash examples/lammps-smoke.sbatch
```

After loading a site-approved LAMMPS module or container, run the tiny smoke
test explicitly:

```bash
RUN_LAMMPS=1 LAMMPS_EXE=lmp bash examples/lammps-smoke.sbatch
```

## Pattern

- Start with a tiny Lennard-Jones input or a reduced production system.
- Record Slurm nodes, tasks, CPU layout, executable name, input script, log
  path, and restart directory before scaling.
- Use `srun` or the launcher recommended by the site MPI stack.
- Keep restart files and logs on durable project storage.
- Treat GPU/KOKKOS flags as build-specific and confirm the LAMMPS executable
  was compiled for the requested accelerator path.

## Safety Notes

This skill is `medium` risk because simulations can consume many CPU/GPU hours
and produce large dump or restart files. The example defaults to plan-only mode
and only runs LAMMPS when `RUN_LAMMPS=1` is set.

## Success Criteria

- The plan records executable, input script, Slurm layout, log path, and restart
  path.
- A tiny smoke test runs before production input is submitted.
- Restart cadence and output volume are reviewed before long jobs.
- Scaling changes are paired with performance evidence and reproducible run
  capture.
