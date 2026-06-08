# NAMD On Slurm

Use this skill when a molecular dynamics workload needs a conservative NAMD
launch pattern on a Slurm cluster.

## Example

Create a launch plan:

```bash
bash examples/namd-smoke.sbatch
```

After loading a site-approved NAMD module or container, run a tiny reviewed
configuration explicitly:

```bash
RUN_NAMD=1 NAMD_EXE=namd2 bash examples/namd-smoke.sbatch
```

## Pattern

- Start with plan-only mode and a tiny or reduced configuration.
- Record Slurm nodes, tasks, CPUs, GPUs, NAMD executable, launcher choice,
  configuration file, output directory, and restart prefix before scaling.
- Use the launcher recommended by the local NAMD build. Some sites use `srun`,
  some use `charmrun`, and some provide wrapper commands or containers.
- Keep logs and restart files on durable project storage, not node-local
  temporary storage.
- Treat `+p`, `+ppn`, `+devices`, `+setcpuaffinity`, and related flags as
  build-specific. Review them with site documentation before long runs.

## Safety Notes

This skill is `medium` risk because molecular dynamics jobs can consume many
CPU/GPU hours and produce large trajectory or restart files. The example
defaults to plan-only mode and only runs NAMD when `RUN_NAMD=1` is set.

## Success Criteria

- The launch plan records executable, launcher, Slurm layout, configuration,
  output path, and restart path.
- A tiny smoke test or reduced system is reviewed before production input is
  submitted.
- Restart cadence and trajectory output volume are reviewed before long jobs.
- Scaling changes are paired with performance evidence and reproducible run
  capture.
