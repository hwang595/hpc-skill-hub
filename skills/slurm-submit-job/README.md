# Slurm Submit Job

Use this skill when a user needs to turn a command into a Slurm batch job.

## Assumptions

- The cluster uses Slurm.
- Users submit jobs from a login or submit node.
- Account, partition, module names, and GPU resource syntax may be site-specific.

## How To Use

Pick the closest example under `examples/`, replace placeholders such as
`<account>` and `<partition>`, then submit:

```bash
sbatch examples/cpu.sbatch
```

For a first run, keep the wall time short and write output to a test directory.

## Safety Notes

This skill is `medium` risk because `sbatch` allocates shared compute
resources. Review resource requests before submitting.

## Success Criteria

- `sbatch` prints a job id.
- `squeue -j <job-id>` shows the job queued or running.
- The output file contains the expected hostname, timestamp, and command output.
