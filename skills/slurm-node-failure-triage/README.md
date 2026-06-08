# Slurm Node Failure Triage

Use this skill when a Slurm job ended with `NODE_FAIL`, `BOOT_FAIL`, a launch
failure, lost-task symptoms, or logs that suggest one allocated node failed,
rebooted, became unreachable, or lost access to a required service.

The goal is to collect enough read-only evidence to decide whether the next
step is a safe retry, a focused array retry, a support handoff, a
checkpoint/restart change, or a deeper facility investigation.

## Example

Collect scheduler and log evidence for a failed job:

```bash
bash examples/slurm-node-failure-triage.sh <job-id> slurm-<job-id>.out
```

Scope node evidence when the failed node is known:

```bash
NODE_NAME=node012 bash examples/slurm-node-failure-triage.sh <job-id> failed-job.out
```

Write to a named report directory:

```bash
REPORT_DIR=node-failure-report bash examples/slurm-node-failure-triage.sh <job-id> failed-job.out
```

## What To Review

- `sacct` job and step states. `BOOT_FAIL` and `NODE_FAIL` point to
  infrastructure or launch-path evidence, but the job log may still contain
  useful application-side symptoms.
- `NodeList`, `NNodes`, partition, elapsed time, and exit code. These help
  separate a single-node incident from a workload that fails everywhere.
- `scontrol show job` while the job record is still visible. It may show the
  job state, allocated nodes, batch host, reason, and requeue-related fields.
- `sinfo -R` and node records when visible. Scheduler reason strings can be
  sensitive, so treat raw output as support evidence until reviewed.
- Array task patterns. One failed task on one node is different from many
  tasks failing across many nodes.

## Safety Notes

This skill is read-only. It does not drain, resume, reboot, power-cycle,
requeue, cancel, resubmit, or modify jobs or nodes. Generated reports may
include private paths, job names, usernames, account names, node names,
partition names, scheduler reason strings, dataset names, and application
arguments; review them before sharing outside a support context.

## Follow-Up

- If one array task failed with `NODE_FAIL`, retry only that task after checking
  whether the site has an active incident or drained-node notice.
- If many jobs failed on the same node, hand the evidence to support instead of
  repeatedly resubmitting large production jobs.
- If a job can safely restart, pair this with `checkpoint-restart-workflow` or
  `slurm-preemption-requeue`.
- If the failure resembles MPI transport or GPU communication loss, pair this
  with `mpi-fabric-diagnostics` or `nccl-diagnostics`.
- If the node name or reason string is not safe to publish, redact the report
  before opening a public issue or adoption report.
