# Slurm Maintenance Reservation Triage

Use this skill when a Slurm job is pending or delayed around a planned
maintenance window, an advanced reservation, drained nodes, down partitions, or
resource unavailability that may not be caused by the user's application.

The goal is to gather public-safe, read-only scheduler evidence before changing
job requests, canceling jobs, or opening a support ticket.

## Examples

Inspect one job:

```bash
bash examples/maintenance-reservation-triage.sh 123456
```

Scope the output to a partition, node, or reservation:

```bash
PARTITION=gpu NODE=gpu001 RESERVATION=maintenance_2026q2 \
  bash examples/maintenance-reservation-triage.sh 123456
```

List current user's pending jobs plus maintenance-like signals:

```bash
bash examples/maintenance-reservation-triage.sh
```

## What It Collects

- `squeue` pending reason, partition, requested nodes, start estimate, expected
  nodes, and reservation field for a job or the current user's pending jobs.
- `sinfo` partition state, node state, and unavailable-node reasons.
- `scontrol show job`, `scontrol show node`, and `scontrol show reservation`
  when the site exposes those read-only details.
- A short review prompt that separates maintenance/reservation signals from
  resource request or policy mismatches.

## Common Signals

- `ReqNodeNotAvail`, `PartitionDown`, `PartitionInactive`, `Reservation`,
  `Unavailable`, `Drain`, or `Down` in the reason field.
- `sinfo -R` shows a maintenance, reservation, hardware, or administrator
  reason for nodes the job appears to need.
- `scontrol show reservation` shows a reservation that overlaps the user's
  requested partition, feature, nodes, or time window.
- The job requests a node, feature, constraint, or GPU type that is reserved or
  drained while other partitions remain healthy.

## Safety Notes

This skill is read-only. It does not submit, cancel, hold, release, requeue, or
modify jobs, nodes, partitions, or reservations. Queue and reservation output
can expose user names, accounts, job names, node names, maintenance reasons, and
site policy. Redact private details before sharing outside the site.
