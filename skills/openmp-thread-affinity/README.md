# OpenMP Thread Affinity

Use this skill when a threaded application is slower than expected, uses more
threads than requested, or shows noisy performance across runs.

## Example

Replace `<account>` and `<partition>`, then submit a short smoke job:

```bash
sbatch examples/openmp-affinity.sbatch
```

For a real application, replace the final `bash examples/inspect-thread-env.sh`
line with the threaded command.

## Pattern

- Request one Slurm task for a shared-memory threaded program.
- Set `--cpus-per-task` to the intended thread count.
- Export `OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"`.
- Set `OMP_PLACES=cores` and `OMP_PROC_BIND=close` as a conservative starting
  point.
- Inspect CPU topology and runtime environment before benchmarking.

## Safety Notes

This skill is `medium` risk because it submits jobs and consumes allocated CPU
resources. Start with a short wall time and one node. Do not scale thread counts
until a small run shows stable placement and expected performance.

## Success Criteria

- `OMP_NUM_THREADS` matches `SLURM_CPUS_PER_TASK`.
- The job log records CPU topology or available CPU count.
- The threaded command does not oversubscribe the allocation.
- Performance comparisons use the same partition, node type, and input size.
