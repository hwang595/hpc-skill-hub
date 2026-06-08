# Slurm Resource Estimator

Use this skill before submitting a larger production job. It collects accounting
records so the user can request resources based on evidence instead of guesses.

## Example

```bash
bash examples/resource-history.sh 30
```

The argument is the number of days of history to inspect.

## Interpreting Results

- Compare `Elapsed` with requested wall time.
- Compare `MaxRSS` with requested memory.
- Look for jobs that ended in `OUT_OF_MEMORY`, `TIMEOUT`, or `FAILED`.
- Add headroom for natural workload variation.

## Safety Notes

This skill is read-only. Accounting availability and field names vary by site.
