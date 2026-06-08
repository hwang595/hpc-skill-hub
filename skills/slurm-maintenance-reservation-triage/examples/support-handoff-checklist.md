# Slurm Maintenance Reservation Handoff Checklist

Use this checklist after collecting `maintenance-reservation-triage.sh` output.
Keep private job names, users, accounts, partitions, node names, reservation
names, and maintenance messages out of public issues.

## Queue Evidence

- Does `squeue` show `ReqNodeNotAvail`, `PartitionDown`, `PartitionInactive`,
  `Reservation`, `Unavailable`, `Drain`, `Down`, or a maintenance-like reason?
- Does the job have an expected start time or expected node list, and does that
  overlap a maintenance window?
- Does the job request a reservation explicitly, or is it blocked by a
  reservation it did not request?

## Request Shape

- Check requested partition, node count, CPU count, memory, features,
  constraints, GPUs, licenses, and time limit.
- Look for pinned node lists or constraints that target drained or reserved
  nodes.
- Compare the affected job with a smaller or less constrained job only if site
  policy allows users to run such a probe.

## Node And Partition State

- Review `sinfo` for partition availability, state, time limits, and node
  states.
- Review `sinfo -R` for maintenance, administrator, reservation, hardware, or
  drained-node reasons.
- If a node is named in the job or expected node list, compare `scontrol show
  node` with the visible reason string.

## Reservation Review

- If `scontrol show reservation` is visible, check reservation start/end time,
  flags, users, accounts, groups, partitions, and node list.
- Confirm whether the reservation is a planned maintenance reservation,
  training reservation, dedicated project reservation, or operational hold.
- Do not recommend reservation changes from public issue context; route those to
  site operations.

## User Communication

- Tell the user when the evidence points to site maintenance instead of job
  failure.
- Suggest waiting, changing only site-approved request fields, or contacting
  support with the redacted report.
- Link public status pages or published maintenance notices when available.
