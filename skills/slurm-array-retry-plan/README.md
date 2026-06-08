# Slurm Array Retry Plan

Use this skill after a Slurm job array partially fails and you want to retry
only the failed task ids instead of resubmitting the whole array.

The example script reads Slurm accounting with `sacct`, or an exported sacct
table for offline testing, then writes a failed-task list, a compact Slurm
array expression, optional failed manifest rows, and a reviewable retry command.
It does not submit anything unless `RUN_SBATCH_RETRY=1` is set.

## Examples

Create a plan from live Slurm accounting:

```bash
bash examples/array-retry-plan.sh <array-job-id> examples/manifest-array.sbatch
```

Create a plan from an exported accounting table:

```bash
SACCT_FILE=examples/mock-sacct-array.txt \
  bash examples/array-retry-plan.sh 123456 examples/manifest-array.sbatch
```

Add a conservative retry concurrency cap:

```bash
RETRY_CONCURRENCY=4 bash examples/array-retry-plan.sh <array-job-id> retry.sbatch
```

Submit only after reviewing the generated plan:

```bash
RUN_SBATCH_RETRY=1 bash examples/array-retry-plan.sh <array-job-id> retry.sbatch
```

## What To Review

- The failed task ids match real failures, not `.batch` or `.extern` job steps.
- The retry states are appropriate for your site and workflow.
- The retry script is idempotent and will not overwrite completed outputs.
- The array concurrency cap respects filesystem, license, database, and
  scheduler policy.
- Optional manifest rows match the same indexing convention as the original
  `SLURM_ARRAY_TASK_ID` usage.

## Safety Notes

This skill is `medium` risk because retrying arrays can launch many jobs and
can overwrite outputs if the workload is not idempotent. The included planner
defaults to read-only plan generation. Set `RUN_SBATCH_RETRY=1` only after
reviewing the task list, retry command, output paths, and site policy.
