# BLAS OpenMP Thread Control

Use this skill when a CPU job, Python/R/Julia analysis, NumPy/SciPy workflow,
MPI rank, Dask/Ray worker, MATLAB job, or simulation helper unexpectedly uses
too many CPU threads or runs slower after requesting more cores.

This skill complements `openmp-thread-affinity`: that skill focuses on Slurm
task shape and OpenMP placement, while this one focuses on implicit thread pools
inside math libraries and language runtimes.

## Example

Generate a read-only report and recommended export block:

```bash
bash examples/threadpool-env-report.sh 4
```

Inside a Slurm job, the script can infer the target from
`SLURM_CPUS_PER_TASK`:

```bash
bash examples/threadpool-env-report.sh
```

## What It Checks

- Scheduler CPU variables such as `SLURM_CPUS_PER_TASK`, `SLURM_NTASKS`,
  `PBS_NP`, `NSLOTS`, and `LSB_DJOB_NUMPROC`.
- Existing thread variables including `OMP_NUM_THREADS`, `MKL_NUM_THREADS`,
  `OPENBLAS_NUM_THREADS`, `BLIS_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`,
  `NUMEXPR_NUM_THREADS`, `R_DATATABLE_NUM_THREADS`, and `JULIA_NUM_THREADS`.
- Optional Python runtime details from `threadpoolctl`, NumPy, and NumExpr when
  those packages are installed.
- A conservative export block that can be copied into a reviewed batch script.

## Common Patterns

- One threaded process per Slurm task: set thread pools to
  `SLURM_CPUS_PER_TASK`.
- Many MPI ranks, each with one core: set thread pools to `1` unless each rank
  is intentionally hybrid MPI/OpenMP.
- Python multiprocessing, Dask, Ray, or data-loader workers: avoid multiplying
  worker count by full BLAS/OpenMP thread count.
- GPU training with CPU preprocessing: keep CPU thread pools bounded so data
  loading does not oversubscribe the allocation.

## Safety Notes

This skill is low risk because the example script is read-only and only prints
recommendations. Applying the export block changes performance behavior, so
benchmark with the same input, partition, node type, and process count before
treating a setting as final.
