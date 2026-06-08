# Snakemake On Slurm

Use this skill when a Snakemake workflow needs to submit rules as Slurm jobs.

## Example

```bash
snakemake --dry-run
bash examples/run-snakemake.sh
```

## Adaptation Points

- Update `examples/slurm-profile/config.yaml` for your account and partition.
- Keep default resources small until the workflow has passed a dry run.
- Ensure the workflow writes intermediate files to a filesystem designed for the
  expected file count.

## Safety Notes

This skill is `medium` risk because Snakemake can submit many jobs. Use
`--jobs` to cap concurrency.
