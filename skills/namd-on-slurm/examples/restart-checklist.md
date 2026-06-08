# NAMD Restart Checklist

- Confirm restart output uses a durable path, not node-local temporary storage.
- Confirm `restartfreq` is frequent enough for the wall-time limit and queue
  policy.
- Keep coordinate, velocity, and extended-system restart files together.
- Record the exact NAMD executable, module or container, launcher, Slurm job id,
  configuration file, and restart prefix.
- Before a production restart, run a short continuation test from the latest
  restart files.
- Review trajectory, log, and restart output volume before scaling to longer
  jobs.
