# Array Retry Review Checklist

Use this checklist before setting `RUN_SBATCH_RETRY=1`.

## Failure Scope

- Confirm whether failures are limited to specific array task ids.
- Compare failed manifest rows with completed rows for larger inputs, missing
  files, or unusual parameters.
- Separate infrastructure failures such as `NODE_FAIL` or `PREEMPTED` from
  application failures such as `FAILED`, `TIMEOUT`, or `OUT_OF_MEMORY`.

## Retry Command

- Use a compact `--array=` expression that includes only failed task ids.
- Add a conservative concurrency cap, for example `%2`, `%4`, or a local
  site-approved value.
- Keep account, partition, memory, time, licenses, and filesystem assumptions
  aligned with the original job or with the reviewed fix.

## Output Safety

- Confirm retry tasks write task-specific logs and outputs.
- Avoid overwriting successful outputs unless the workflow is explicitly
  idempotent.
- Move or archive partial outputs from failed tasks when the application cannot
  resume safely.
- Keep the retry plan and accounting output with the final workflow record.
