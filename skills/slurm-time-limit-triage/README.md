# Slurm Time Limit Triage

Use this skill when a Slurm job ended as `TIMEOUT`, was killed near its
requested walltime, stopped after receiving scheduler signals, or repeatedly
finishes just before the time limit without producing complete outputs.

The goal is to collect enough read-only evidence to decide whether the next run
should request a longer time limit, checkpoint more often, split the workload,
reduce concurrency, adjust workflow retries, or investigate one unusually slow
task.

## Example

Collect scheduler and log evidence:

```bash
bash examples/slurm-time-limit-triage.sh <job-id> slurm-<job-id>.out
```

Scan a log when Slurm accounting is not available from the current system:

```bash
JOB_LOG=failed-job.out bash examples/slurm-time-limit-triage.sh
```

Write to a named report directory:

```bash
REPORT_DIR=time-limit-report bash examples/slurm-time-limit-triage.sh <job-id> failed-job.out
```

## What To Review

- `sacct` job and step states. A top-level row can say `TIMEOUT` while a batch
  or extern step shows additional exit-code or signal details.
- `Elapsed` versus `Timelimit`, plus `Submit`, `Start`, and `End`, so runtime
  exhaustion is separated from queue wait or launch delay.
- `ExitCode` signal values and application logs. Some applications handle
  termination signals and write checkpoint or cleanup messages before Slurm
  records the final timeout.
- Array task spread. One slow task may need different chunking, input-size
  balancing, or retry handling rather than a blanket walltime increase.
- Checkpoint cadence. Checkpoints should happen often enough to leave useful
  restart points before the scheduler sends termination signals.

## Safety Notes

This skill is read-only. It does not change `TimeLimit`, cancel, requeue,
resubmit, or modify jobs. Generated reports may include private paths, job
names, usernames, account names, node names, dataset names, and application
arguments; review them before sharing outside a support context.

## Follow-Up

- If `Elapsed` is equal to or just below `Timelimit`, request more walltime or
  reduce problem size for the next run.
- If the job timed out after doing useful work, pair this with
  `checkpoint-restart-workflow`.
- If only some array tasks timed out, compare their inputs and use
  `slurm-array-retry-plan` for focused retries.
- If runtime varies widely across tasks, inspect I/O, filesystem load,
  data staging, and node-local scratch behavior.
- If `sacct` does not retain the needed fields, rerun a short reproducer with
  application-level timestamps and checkpoint logging enabled.
