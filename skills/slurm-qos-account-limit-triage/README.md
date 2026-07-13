# Slurm QOS Account Limit Triage

Use this skill when a Slurm job is pending or rejected because of account,
association, QOS, fairshare, or TRES-minute policy. It is a deeper follow-up to
`slurm-pending-reason-triage` for reason strings such as `AssocGrp*Limit`,
`AssocMax*Limit`, `QOSGrp*Limit`, `QOSMax*Limit`, `InvalidAccount`,
`InvalidQOS`, or `Priority`.

## Prerequisites

- Confirm the scheduler is Slurm and that the user may inspect the selected job,
  association, QOS, and fairshare fields exposed by local policy.
- Record the job id, user, account, QOS, partition, requested TRES, and snapshot
  time. Do not query another user's policy records without authorization.
- Treat hidden `sacctmgr`, `sshare`, or `sprio` output as missing evidence, not
  proof that no policy limit exists.
- Choose a new output directory; the collector refuses to overwrite an existing
  evidence bundle.

## Workflow

Collect a report for a pending job:

```bash
bash examples/qos-account-limit-triage.sh 123456
```

Collect visible policy evidence for the current user:

```bash
bash examples/qos-account-limit-triage.sh
```

Write to an explicit report directory:

```bash
bash examples/qos-account-limit-triage.sh 123456 "$USER" qos-limit-report
```

Review saved queue and visible policy fixtures offline:

```bash
python3 examples/review-qos-evidence.py \
  --queue <squeue.txt> --policy <visible-policy.txt>
```

## What It Collects

- `squeue` pending reason, account, QOS, priority, partition, time, and
  dependency fields.
- `scontrol show job` details for a selected job when available.
- `sacctmgr show assoc` records visible for the selected user.
- `sacctmgr show qos` fields that commonly explain QOS resource limits.
- `sshare` fairshare and TRES-minute evidence when exposed by the site.
- `sprio` priority factors when available.

## Interpreting Results

- `AssocGrp*Limit` usually means an account or user association has reached an
  aggregate resource limit.
- `AssocMax*Limit` usually means the job request violates a per-job association
  limit.
- `QOSGrp*Limit` usually means the requested QOS has reached an aggregate
  resource limit.
- `QOSMax*Limit` usually means the job request violates a per-job QOS limit.
- `InvalidAccount` or `InvalidQOS` usually means the requested account, QOS, or
  association is not valid for the user, partition, or cluster.
- `Priority` may reflect fairshare, QOS priority, partition priority, job age,
  or other site policy.

## Resource And Cost

The collector writes a small local report and sends bounded read-only queries to
Slurm control/accounting services. Avoid polling loops and broad all-user policy
queries. Changing CPU, GPU, memory, walltime, QOS, or account can alter queue
cost and eligibility and must be reviewed separately.

## Cleanup

The script creates one report directory and never changes scheduler state.
Retain or remove the local bundle under project policy. It does not hold,
release, cancel, requeue, resubmit, or edit the selected job or policy records.

## Site Adaptation

Association hierarchy, QOS names, fairshare, TRES limits, visibility, and
support procedures are site-specific. Do not promise a start time or infer
hidden policy. Redact users, accounts, QOS, partitions, job names, and internal
limits before public sharing.

## Safety Notes

This skill is `low` risk because it runs bounded read-only Slurm commands and
writes local text reports. It does not modify accounts, QOS records,
associations, fairshare, jobs, reservations, or scheduler configuration.

The report can expose usernames, accounts, project names, job names, QOS names,
partition names, and local policy. Review or summarize it before posting
outside the support channel approved by the site.

## Success Criteria

- The report directory contains a summary and the available read-only command
  outputs.
- Missing optional commands are recorded instead of treated as fatal errors.
- The selected job's account, QOS, pending reason, and requested resources can
  be compared with visible association and QOS limits.
- The next action is clear: adjust the job request, choose a valid account/QOS,
  wait for fairshare or group limits to recover, or contact support with the
  evidence bundle.
