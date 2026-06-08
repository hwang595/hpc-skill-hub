# BLAS And OpenMP Thread Review Checklist

Use this checklist before applying the export block from
`threadpool-env-report.sh` to a production job.

## Outer Parallelism

- Count MPI ranks, Slurm tasks, job-array tasks, Dask workers, Ray workers,
  Python multiprocessing processes, data-loader workers, or R parallel workers.
- Decide whether each process should be single-threaded or intentionally
  threaded.
- Confirm the scheduler request matches that design, especially
  `--ntasks` and `--cpus-per-task` for Slurm.

## Inner Thread Pools

- Align `OMP_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENBLAS_NUM_THREADS`,
  `BLIS_NUM_THREADS`, and `VECLIB_MAXIMUM_THREADS`.
- Align `NUMEXPR_NUM_THREADS`, `R_DATATABLE_NUM_THREADS`, and
  `JULIA_NUM_THREADS` when those runtimes are in use.
- Disable dynamic thread expansion first (`OMP_DYNAMIC=FALSE`,
  `MKL_DYNAMIC=FALSE`) unless a site or application guide says otherwise.

## Workload-Specific Notes

- NumPy, SciPy, scikit-learn, pandas, and NumExpr can call BLAS or OpenMP
  libraries through Python without the user explicitly creating threads.
- R packages can use threaded BLAS, OpenMP, or package-specific worker pools.
- Julia workloads may combine `JULIA_NUM_THREADS` with BLAS threads, so review
  both.
- GPU training can still oversubscribe CPU cores through preprocessing,
  data-loader workers, and BLAS-backed CPU fallbacks.

## Evidence To Compare

- Same input data and command.
- Same partition, node type, CPU count, process count, and memory request.
- CPU efficiency from scheduler accounting.
- Wall time and application-level throughput.
- Logs showing the applied thread variables.
