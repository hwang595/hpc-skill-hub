# Slurm Pending Reason Triage

Use this skill to explain why a Slurm job is pending without changing the job or
promising a start time. It separates dependency, priority, resource,
association/QOS, partition, reservation, and unavailable-node signals using a
point-in-time queue snapshot plus optional job and priority details.

## Prerequisites

- Confirm the target scheduler is Slurm and that the user may inspect the job.
- Obtain a job id only when the user intends to inspect that job. Without one,
  the live example lists pending jobs for the current user.
- Treat queue reasons as transient scheduler evidence. Capture the observation
  time and avoid interpreting one reason as permanent policy.
- Use public site documentation or a site adapter for account, QOS, partition,
  reservation, and support policy. Do not infer unpublished limits.

## Inputs And Outputs

The live input is an optional Slurm job id. Output is terminal-only `squeue`,
optional `scontrol`, optional `sprio`, and review prompts. The offline reviewer
accepts saved public-safe snapshots and prints only extracted reason/category
pairs; neither example writes files or changes scheduler state.

## Workflow

1. Prefer a saved synthetic or user-reviewed snapshot when reproducing an
   explanation. Review one or more snapshots offline:

   ```bash
   python3 examples/review-pending-snapshot.py <saved-squeue.txt> [saved-scontrol.txt]
   ```

2. If current scheduler evidence is needed, show the read-only command before
   running it. Inspect one job:

   ```bash
   bash examples/pending-reason-triage.sh 123456
   ```

   Or list only the current user's pending jobs:

   ```bash
   bash examples/pending-reason-triage.sh
   ```

3. Record the reason, dependency, partition, requested nodes/resources,
   priority fields, and observation time. Missing `scontrol` or `sprio` output
   is missing evidence, not a scheduler diagnosis.
4. Match the reason to the narrowest follow-up below. Ask for local policy or
   support review when the explanation depends on hidden limits or node state.

## Interpreting Results

| Reason class | What the snapshot supports | Safe follow-up |
| --- | --- | --- |
| `Dependency` | An upstream job, array task, or dependency condition is unresolved | Inspect the dependency expression and upstream terminal state |
| `Priority` | The job is eligible but other jobs currently rank ahead | Review visible priority factors; do not predict an exact start time |
| `Resources` | The requested resource combination is not currently available | Compare CPU, memory, GPU, node, feature, and time shape without blindly increasing them |
| `Assoc*` or `QOS*` limit | An account/QOS aggregate or per-job policy may be binding | Route to `slurm-qos-account-limit-triage` and compare visible policy evidence |
| Partition, reservation, or unavailable-node reason | Availability or local operations context may dominate | Check public partition/reservation state and prepare a redacted support handoff |

The reason can change as dependencies finish, resources free, or policy state
changes. `sprio` factors and numeric priority are comparative signals, not an
estimated start-time contract.

## Validation

A successful triage names the snapshot time and reason class, cites the evidence
used, distinguishes observed facts from policy hypotheses, and identifies one
bounded next check. It must explicitly retain uncertainty when fields are
missing or the reason changes between snapshots. No explanation should claim an
exact start time unless the scheduler itself provides a site-supported estimate.

## Resource And Cost

Both examples are read-only. The offline reviewer consumes negligible local CPU
and reads only selected text files. Live `squeue`, `scontrol`, and `sprio` calls
send small scheduler queries, so avoid rapid polling loops or broad all-user
queries that can load shared control services.

## Cleanup

No cleanup is required because the examples create no files and do not hold,
release, cancel, modify, or requeue jobs. Delete saved snapshots only according
to project retention rules; they may be useful when a transient reason changes.

## Site Adaptation

Priority weights, fairshare, QOS/association limits, reservations, hidden
partitions, and support escalation are site-specific. Preserve unknown account,
partition, QOS, and reservation values as unknown. Redact job names, usernames,
accounts, partitions, dependencies, hostnames, and internal policy fields before
publishing snapshots or sending them to an agent.

## Safety Notes

This skill is `low` risk and read-only, but scheduler snapshots can expose user
and project metadata. Never convert a triage request into `scancel`, `scontrol
hold/release`, requeue, dependency modification, or resubmission without a
separate explicit user request and review of the affected job id.
