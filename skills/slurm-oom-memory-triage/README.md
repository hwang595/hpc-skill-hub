# Slurm OOM Memory Triage

Use this skill when a Slurm job failed with `OUT_OF_MEMORY`, `OOM`, a killed
process, missing `MaxRSS`, or application logs that suggest the workload
exceeded the memory available to its allocation.

The goal is to collect enough read-only evidence to decide whether the next run
should request more memory, reduce per-node concurrency, change data-loading
behavior, stage inputs differently, or move to a profiling workflow.

## Example

Collect scheduler and log evidence:

```bash
bash examples/slurm-oom-triage.sh <job-id> slurm-<job-id>.out
```

Scan a log when Slurm accounting is not available from the current system:

```bash
JOB_LOG=failed-job.out bash examples/slurm-oom-triage.sh
```

Write to a named report directory:

```bash
REPORT_DIR=oom-report bash examples/slurm-oom-triage.sh <job-id> failed-job.out
```

## What To Review

- `sacct` job and step states. The batch step may show `OUT_OF_MEMORY` even
  when the top-level job state is less specific.
- `ReqMem`, `ReqTRES`, and `AllocTRES` so the memory request is interpreted in
  context with CPUs, tasks, nodes, and site policy.
- `MaxRSS`, `AveRSS`, and missing memory fields. Jobs killed early may not leave
  a complete peak-memory record.
- Log lines mentioning OOM, killed workers, cgroup limits, allocator failures,
  data-loader workers, Java heap, Python memory errors, or MPI rank exits.
- Whether the workload launched more concurrent processes or threads than the
  memory request was sized for.

## Safety Notes

This skill is read-only. It does not cancel, modify, resubmit, or clean up jobs.
Generated reports may include private paths, job names, usernames, account
names, dataset names, and application arguments; review them before sharing
outside a support context.

## Follow-Up

- If `MaxRSS` is close to `ReqMem`, rerun with a larger memory request or fewer
  simultaneous workers.
- If `MaxRSS` is absent or far below the request, inspect application logs and
  site cgroup messages before assuming the request was enough.
- If only some array tasks fail, compare input sizes and per-task memory use.
- If memory grows over time, use `performance-profile-basic` or an
  application-specific profiler before scaling the production job.
- If the job also uses GPUs, pair this with `gpu-memory-triage` to separate
  host memory from device memory pressure.
