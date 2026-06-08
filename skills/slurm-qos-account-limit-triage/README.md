# Slurm QOS Account Limit Triage

Use this skill when a Slurm job is pending or rejected because of account,
association, QOS, fairshare, or TRES-minute policy. It is a deeper follow-up to
`slurm-pending-reason-triage` for reason strings such as `AssocGrp*Limit`,
`AssocMax*Limit`, `QOSGrp*Limit`, `QOSMax*Limit`, `InvalidAccount`,
`InvalidQOS`, or `Priority`.

## Example

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

## Safety Notes

This skill is `low` risk because it only runs read-only Slurm commands and
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
