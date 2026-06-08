# Hybrid MPI/OpenMP On Slurm

Use this skill when an application launches multiple MPI ranks and each rank
uses OpenMP threads. It helps align `--ntasks-per-node`, `--cpus-per-task`,
`OMP_NUM_THREADS`, `OMP_PLACES`, `OMP_PROC_BIND`, and `srun --cpu-bind` before
running a larger simulation or benchmark.

## Example

Replace `<account>` and `<partition>`, then submit in dry-run mode first:

```bash
sbatch examples/hybrid-mpi-openmp.sbatch
```

Dry-run mode writes topology evidence and prints the compile and launch plan.
To run the tiny hybrid probe:

```bash
RUN_HYBRID_PROBE=1 \
MPI_MODULE=<mpi-module> \
MPI_TASKS=4 \
OMP_THREADS=2 \
CPU_BIND=verbose,cores \
  sbatch examples/hybrid-mpi-openmp.sbatch
```

Keep the first run small and representative. Use the same node type, MPI stack,
compiler wrapper, and binding policy you plan to use for the real workload.

## Pattern

- Choose MPI ranks per node from the application decomposition.
- Set `--cpus-per-task` to the intended thread count per MPI rank.
- Export `OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK}"` or a reviewed thread count
  that matches the Slurm allocation.
- Start with `OMP_PLACES=cores` and `OMP_PROC_BIND=close` unless the
  application or site has a better documented policy.
- Launch with `srun --ntasks=<ranks> --cpu-bind=<policy>`.
- Record rank, thread, host, CPU, affinity, and OpenMP environment evidence.
- Change one layout variable at a time before comparing timing results.

## Safety Notes

This skill is `medium` risk because it submits a Slurm job and can launch MPI
ranks with multiple OpenMP threads. The default job is intentionally tiny and
`RUN_HYBRID_PROBE` defaults to `0`. Avoid large node counts, production inputs,
or long walltimes until the rank/thread report shows the expected placement.

## Success Criteria

- Dry-run mode prints compile and launch commands with the expected MPI task
  count, OpenMP thread count, and binding policy.
- `topology.txt` records Slurm variables and visible CPU topology.
- `rank-thread-affinity.tsv` contains one row for every MPI rank and OpenMP
  thread in the probe.
- `OMP_NUM_THREADS` matches the intended `--cpus-per-task` value.
- Rank and thread placement matches the intended decomposition before scaling.
