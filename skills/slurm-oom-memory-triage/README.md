# Slurm OOM Memory Triage

Use this skill when a Slurm job failed with `OUT_OF_MEMORY`, `OOM`, a killed
process, missing `MaxRSS`, or application logs that suggest the workload
exceeded the memory available to its allocation.

The goal is to collect enough read-only evidence to decide whether the next run
should request more memory, reduce per-node concurrency, change data-loading
behavior, stage inputs differently, or move to a profiling workflow.

## Prerequisites

- Confirm the scheduler is Slurm and that the user may inspect the selected job
  and log. Completed-job accounting may be delayed, purged, or hidden by policy.
- Preserve job and step identifiers separately; top-level, batch, extern, and
  application steps can report different states and memory fields.
- Treat `ReqMem` units and per-node/per-CPU scope according to local Slurm
  configuration. Do not compare values until their scope is understood.
- Choose a new report directory. The collector refuses to overwrite an existing
  path or continue when an explicitly requested log is missing.

## Workflow

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

Review synthetic or redacted evidence without contacting Slurm:

```bash
python3 examples/review-oom-evidence.py \
  --accounting <sacct.txt> --log <job-log.txt> --require-both
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

## Resource And Cost

The collector sends a few bounded read-only Slurm queries and writes a small
local text report. Avoid repeated broad accounting queries. Any proposed rerun,
profiling job, larger memory request, reduced concurrency, or input staging can
consume allocation, CPU, memory, storage, and walltime and needs separate review.

## Cleanup

The script creates one report directory and never deletes it. Retain the bundle
for comparison or remove it under project policy after review. It does not
cancel, modify, or resubmit the failed job.

## Site Adaptation

Accounting retention, `ReqMem` scope, cgroup signals, `seff` availability, and
support escalation vary by site. Preserve missing fields as missing evidence and
redact usernames, accounts, hostnames, paths, job names, and application
arguments before public sharing.

## Safety Notes

This skill is scheduler read-only but creates a local report directory. It does
not cancel, modify, resubmit, or clean up jobs. Generated reports may include
private paths, job names, usernames, account
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
