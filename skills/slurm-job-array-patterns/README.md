# Slurm Job Array Patterns

Use this skill when a workload has many independent tasks, such as parameter
sweeps, sample-level analysis, or file-by-file preprocessing.

## Example

Review the manifest, choose a conservative concurrency cap, then submit:

```bash
sbatch --array=1-3%2 examples/manifest-array.sbatch
```

Replace `<account>` and `<partition>` before submitting on a real cluster.

## Manifest Pattern

Keep one task per line in a tab-separated manifest:

```text
sample_a	inputs/sample_a.txt	results/sample_a.out
sample_b	inputs/sample_b.txt	results/sample_b.out
```

The array task id selects the matching line. This makes it easy to rerun a
single failed task with `--array=<task-id>`.

## Safety Notes

This skill is `medium` risk because arrays can submit many tasks and consume
shared resources quickly. Start with a small range and a concurrency cap such as
`%2` or `%10`, then scale after checking logs and scheduler policy.

## Success Criteria

- Each task writes a distinct log file.
- The selected manifest line matches `SLURM_ARRAY_TASK_ID`.
- A failed task can be rerun without rerunning the entire array.
- Output paths are user-owned and do not collide between tasks.
