# Slurm Efficiency Report

Use this skill after a Slurm job finishes to understand whether future runs
should request more or less wall time, memory, CPU cores, or nodes. It is useful
for support tickets, training follow-up, and performance tuning conversations.

## Example

```bash
bash examples/slurm-efficiency-report.sh 123456
```

Replace `123456` with a completed Slurm job id, array task id, or job step id.

## What It Collects

- `seff` output when the command is installed at the site.
- `sacct` accounting fields for state, elapsed time, requested memory, maximum
  resident memory, total CPU time, allocated CPUs, and nodes.
- A short interpretation checklist for future resource requests.

## Interpreting Results

- Low CPU efficiency can mean the program is serial, waiting on I/O, blocked on
  communication, or requesting too many CPUs.
- Low memory efficiency often means the next similar run can request less
  memory, with headroom for larger inputs.
- `OUT_OF_MEMORY`, high MaxRSS, or missing MaxRSS values should be reviewed
  with local accounting policy in mind.
- Very short elapsed time compared with requested wall time may be normal for
  smoke tests, but repeated production jobs should request tighter limits.
- GPU utilization usually needs application logs or site GPU telemetry; Slurm
  accounting alone may not tell the full story.

## Safety Notes

This skill is read-only. It queries Slurm accounting data and does not submit,
cancel, requeue, or modify jobs. Accounting retention, field availability, and
`seff` installation vary by site.
