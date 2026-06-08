# Slurm Preemption And Requeue

Use this skill when a Slurm job may be preempted, requeued after node failure,
or manually requeued by an authorized owner after checkpoint state has been
reviewed.

This skill complements `checkpoint-restart-workflow`: that skill focuses on
restartable state, while this one focuses on Slurm signal and requeue behavior.

## Example

Review the Slurm wrapper after replacing `<account>` and `<partition>`:

```bash
bash -n examples/preemption-requeue.sbatch
```

The wrapper is review-only by default. To run the toy worker inside an
allocation, submit with:

```bash
sbatch --export=RUN_REQUEUE_WORKER=1 examples/preemption-requeue.sbatch
```

Run the toy worker locally to confirm restart behavior without using Slurm:

```bash
OUTPUT_DIR=/tmp/slurm-preemption-requeue-demo bash examples/signal-aware-worker.sh
OUTPUT_DIR=/tmp/slurm-preemption-requeue-demo bash examples/signal-aware-worker.sh
```

## Design Pattern

- Use `#SBATCH --requeue` only when the workload can restart safely.
- Use `#SBATCH --signal=B:USR1@120` or a site-approved variant to request a
  warning signal before termination.
- Write progress to durable storage outside node-local scratch.
- Treat a requeued job as a fresh execution of the batch script with existing
  state and the same job id.
- Keep stop-request, checkpoint, log, and final-output files distinct.
- Make explicit manual requeue an operator-reviewed action, not a hidden loop.

## Safety Notes

This skill is `medium` risk because `sbatch` consumes shared resources and
requeue behavior can repeat work. Do not enable automatic requeue handling for
non-idempotent workloads, commands that overwrite final output, or jobs that
cannot prove checkpoint compatibility.

The example does not call `scontrol requeue`. Use
`examples/requeue-operator-checklist.md` before any manual requeue action.

## Success Criteria

- The job log records `SLURM_JOB_ID`, restart count when available, signal
  policy, output directory, and whether the worker actually ran.
- A signal or stop request writes checkpoint state before exit.
- A repeated run detects existing state and resumes from the next step.
- Manual requeue decisions have evidence that output is restart-safe.
