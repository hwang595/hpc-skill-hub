# Slurm Pending Reason Triage

Use this skill when a Slurm job stays pending and the user needs a public-safe,
read-only explanation of the scheduler signals. It helps distinguish common
causes such as dependencies, priority, fairshare, requested resources,
partition limits, reservations, or unavailable nodes.

## Examples

Inspect one pending job:

```bash
bash examples/pending-reason-triage.sh 123456
```

List pending jobs for the current user:

```bash
bash examples/pending-reason-triage.sh
```

## What It Collects

- `squeue` reason, state, partition, priority, requested nodes, time limit, and
  remaining dependency fields.
- `scontrol show job` details when a specific job id is provided.
- `sprio` priority factors when the site exposes the command.

## Interpreting Results

- `Dependency` usually means the job waits for another job or array task.
- `Priority` often means the job is eligible but lower priority than other work.
- `Resources` usually means the requested CPU, memory, GPU, node, or feature
  combination is not currently available.
- `ReqNodeNotAvail`, `PartitionDown`, or reservation-related reasons usually
  need local scheduler or operations context.
- A very large memory, GPU, time, or node request can make a job wait longer
  even when the reason string looks generic.
- `sprio` values are site policy signals, not promises about exact start time.

## Safety Notes

This skill is read-only. It does not modify, hold, release, cancel, or requeue
jobs. Queue snapshots can still expose job names, user names, accounts,
partitions, and scheduler reason strings, so avoid posting raw output publicly
unless local policy allows it.
