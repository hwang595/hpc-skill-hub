# LAMMPS Restart Checklist

- Confirm the input script writes restart files at a useful cadence.
- Keep restart files on durable storage or stage them out before job cleanup.
- Record the LAMMPS executable, module stack, accelerator package, and version.
- Confirm restart files are compatible with the executable and platform used for reruns.
- Limit dump and thermo output volume before scaling to long production runs.
- Pair scaling changes with MPI rank, OpenMP thread, GPU, and timing evidence.
