# Memory Request Review

Use this checklist after collecting `sacct`, optional `seff`, optional
`scontrol`, and log evidence.

## Scheduler Evidence

- Did any job step report `OUT_OF_MEMORY` or `OOM`?
- Does the batch step differ from the top-level job state?
- Are `ReqMem`, `ReqTRES`, `AllocTRES`, CPUs, tasks, and nodes consistent with
  the intended job shape?
- Is `MaxRSS` near the requested memory, missing, or much lower than expected?
- Did the job fail quickly, after a long ramp-up, or only for some array tasks?

## Application Evidence

- Did the application launch more ranks, threads, workers, or data-loader
  processes than expected?
- Do logs mention killed workers, allocator failures, Java heap errors, Python
  `MemoryError`, MPI rank termination, cgroup limits, or kernel OOM messages?
- Did input size, number of samples, mesh resolution, chunk size, or batch size
  change from the last successful run?
- Does temporary data land on a memory-backed filesystem or an unexpectedly
  small local directory?

## Next Run

- Increase memory only after confirming whether the request is per node, per
  CPU, or shaped by local site policy.
- Reduce concurrency when many independent processes share one node.
- Keep application heap or worker limits below the Slurm memory request with
  room for native libraries and file caches.
- Run a smaller profiling case before scaling production inputs.
- For array jobs, separate failed task ids and compare their inputs with tasks
  that completed.
