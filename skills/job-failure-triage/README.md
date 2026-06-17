# Job Failure Triage

Use this skill when a job failed and the user needs a structured first look
before changing code or resource requests.

## Example

```bash
bash examples/triage-slurm-job.sh <job-id> slurm-<job-id>.out
```

The example collects scheduler evidence such as `sacct` output, job details,
and log snippets before recommending a fix.

## Common Signals

- `OUT_OF_MEMORY`: review out-of-memory evidence, then increase memory,
  reduce concurrency, or profile memory use.
- `TIMEOUT`: request more wall time or checkpoint the workload.
- `FAILED` with exit code `127`: command not found or module not loaded.
- Permission errors: check file ownership, scratch path, and group access.
- Empty output: verify the script reached the workload command.

## Safety Notes

This skill is read-only, but logs may contain private paths or dataset names.
