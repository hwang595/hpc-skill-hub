# Slurm Monitor Job

Use this skill to answer "what is my job doing?" without changing cluster
state.

## Example

```bash
bash examples/monitor-job.sh <job-id>
```

## What It Checks

- Current queue state with `squeue`.
- Accounting state with `sacct`, when accounting is enabled.
- Slurm controller details with `scontrol show job`.
- Output and error file paths when available.

## Safety Notes

This skill is read-only and `low` risk. It may expose project names, usernames,
or node names in terminal output, so avoid pasting reports into public issues
without redaction.
