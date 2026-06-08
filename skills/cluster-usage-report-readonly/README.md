# Cluster Usage Report Readonly

Use this skill when an HPC support team needs a small, shareable snapshot of
Slurm usage evidence for a review, support handoff, training report, or
community discussion.

The example script is read-only. It runs reporting commands such as `sacct`,
`sreport`, `squeue`, and `sinfo` when they are available, then writes text
outputs into a local report directory.

## Assumptions

- The site uses Slurm.
- `sacct` is available to the user running the report.
- Optional commands such as `sreport`, `squeue`, and `sinfo` may or may not be
  available depending on local policy.
- Accounting visibility is site-specific. Some users only see their own jobs;
  support staff may see account, association, or cluster-wide records.

## Example

Collect the last 14 days of visible accounting data:

```bash
bash examples/cluster-usage-report.sh 14
```

Collect account-scoped data when local policy allows it:

```bash
bash examples/cluster-usage-report.sh 30 <account>
```

Write reports to an explicit output directory:

```bash
bash examples/cluster-usage-report.sh 30 <account> usage-report-june
```

## Review The Output

The script creates files such as:

- `summary.md`: report scope and review reminders.
- `sacct-jobs.txt`: visible accounting records for the selected window.
- `sreport-utilization.txt`: optional cluster utilization summary.
- `squeue-current.txt`: optional current queue snapshot.
- `sinfo-partitions.txt`: optional partition and node-state snapshot.

Before sharing a report outside the support team, review it for usernames,
account names, project names, job names, private partitions, hostnames, and
other local policy details.

## Success Criteria

- The report directory exists.
- Each generated file includes the command that produced it.
- Missing optional tools are recorded instead of treated as fatal errors.
- The report remains read-only and does not submit, cancel, modify, or
  reconfigure jobs.

## Safety Notes

This skill is low risk because it only reads scheduler information and writes
local text files. It can still expose operational or private information if the
site's accounting data includes users, accounts, job names, nodes, or
partitions. Redact or summarize sensitive fields before publication.

Do not use this skill as a substitute for a facility's official accounting,
quota, allocation, billing, or incident-reporting process.
