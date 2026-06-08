# GROMACS Checkpoint Checklist

- Confirm the job writes checkpoints with `mdrun -cpt` at a useful cadence.
- Preserve `.cpt`, `.log`, `.edr`, `.tpr`, and trajectory files on durable storage.
- Use `-cpi` only when intentionally resuming from a compatible checkpoint.
- Record `GMX_CMD`, module stack, GPU flags, MPI ranks, and OpenMP threads.
- Review trajectory and energy output cadence before scaling long runs.
- Compare GPU/MPI/OpenMP layouts with timing evidence before changing production settings.
