# Time Limit Review Checklist

Use this checklist after collecting a Slurm time-limit triage report.

## Confirm The Failure Mode

- Is the top-level job or a child step in `TIMEOUT`?
- Is `Elapsed` equal to or very close to `Timelimit`?
- Did the application log show signal handling, checkpointing, cleanup, or
  partial output before Slurm recorded the final state?
- Did the job launch late, restart, requeue, or run on a different partition
  than expected?

## Choose The Next Action

- Increase walltime when the workload was progressing normally and the queue
  policy allows the larger request.
- Split the workload when one run is too large for the available partition
  limits.
- Add or tune checkpoint/restart when useful work is lost at timeout.
- Reduce concurrency when too many simultaneous workers slow each other down
  through I/O, memory, license, or thread contention.
- Retry only the slow or failed array tasks when most tasks finished
  successfully.

## Handoff Notes

- Include `summary.md`, `sacct-accounting.txt`, and the relevant log snippets.
- Redact private paths, tokens, dataset identifiers, and collaborator names
  before sharing outside the project or support queue.
- Do not ask support to raise a system-wide limit without showing the elapsed
  time, partition, requested time limit, and restart behavior.
