# Nextflow On Slurm

Use this skill when a Nextflow workflow should run through Slurm instead of the
local executor.

## Example

```bash
cp examples/nextflow.config ./nextflow.config
bash examples/run-nextflow.sh hello
```

## Adaptation Points

- Set the correct account, partition, queue size, and work directory.
- Keep `process.executor = 'slurm'` inside the Slurm profile.
- Put `workDir` on a filesystem intended for many task work directories.
- Use containers only when your site supports the chosen runtime.

## Safety Notes

This skill is `medium` risk because workflows may launch many scheduler jobs.
Start with small test inputs and conservative queue limits.
