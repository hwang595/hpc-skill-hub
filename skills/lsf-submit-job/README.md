# LSF Submit Job

Use this skill when a user needs to turn a command into an IBM Spectrum LSF
`bsub` batch job.

## Assumptions

- The cluster uses LSF-style `bsub` submission.
- Users submit jobs from a login or submit node.
- Project, queue, resource string, GPU, and MPI syntax may be site-specific.
- `#BSUB` directives are interpreted by `bsub` before the job script runs.

## How To Use

Pick the closest example under `examples/`, replace placeholders such as
`<project>` and `<queue>`, then submit:

```bash
bsub < examples/cpu.lsf
```

For a first run, keep the wall time short and write output to a test directory.
Use `bjobs <job-id>` or the site-recommended status command to inspect the
submitted job.

## Safety Notes

This skill is `medium` risk because `bsub` allocates shared compute resources.
Review resource requests before submitting. LSF deployments differ in queue,
project, memory, GPU, and MPI launch syntax, so treat the examples as safe
starting points rather than site policy.

## Success Criteria

- `bsub` prints a job id.
- `bjobs <job-id>` or the local status command shows the job pending, running,
  or completed.
- The output file contains the expected hostname, timestamp, working directory,
  and command output.
