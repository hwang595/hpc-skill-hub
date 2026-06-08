# Slurm Output Log Triage

Use this skill when a Slurm job ran or failed but the user cannot find the
stdout/stderr log, the log is empty, the log was written somewhere unexpected,
or the log contains only a scheduler-level message instead of application
output.

The goal is to collect enough read-only evidence to decide whether the issue is
a default Slurm filename, an unexpected working directory, a split stdout/stderr
path, a directory that did not exist at launch, permissions, quota, early
submission failure, or an application that wrote output somewhere else.

## Example

Collect scheduler and default log-path evidence:

```bash
bash examples/slurm-output-log-triage.sh <job-id>
```

Inspect a known log file:

```bash
bash examples/slurm-output-log-triage.sh <job-id> logs/my-job.out
```

Inspect split stdout and stderr paths:

```bash
ERROR_FILE=logs/my-job.err bash examples/slurm-output-log-triage.sh <job-id> logs/my-job.out
```

Write to a named report directory:

```bash
REPORT_DIR=output-log-report bash examples/slurm-output-log-triage.sh <job-id> logs/my-job.out
```

## What To Review

- Slurm's default output file is usually `slurm-%j.out` for ordinary jobs and
  `slurm-%A_%a.out` for array tasks unless `--output` or `--error` was set.
- `sacct` may show `StdOut`, `StdErr`, and `SubmitLine`, but filename patterns
  can remain unexpanded in accounting.
- `scontrol show job` may show `WorkDir`, `StdOut`, `StdErr`, and `Command`
  while the job record is still visible.
- Relative output paths are interpreted relative to the job working directory,
  not necessarily the directory where the user is searching now.
- Missing parent directories, permissions, quotas, and filesystem errors can
  prevent useful logs from appearing where expected.

## Safety Notes

This skill is read-only. It does not move, delete, truncate, create, or rewrite
user logs. Generated reports may include private paths, job names, usernames,
account names, project names, dataset names, commands, and application
arguments; review them before sharing outside a support context.

## Follow-Up

- Add explicit `#SBATCH --output=logs/%x-%j.out` and
  `#SBATCH --error=logs/%x-%j.err` after confirming `logs/` exists before
  submission.
- Add `pwd`, `hostname`, `date`, and a clear first `echo` near the top of a
  batch script so an empty log has a recognizable launch boundary.
- If the log exists but has no application output, check whether the job failed
  before reaching the workload command.
- If paths point to project or scratch storage, pair this with
  `quota-and-filesystem-triage` or `shared-project-permissions-triage`.
- If logs are scattered across array tasks, pair this with
  `slurm-job-array-patterns` or `slurm-array-retry-plan`.
