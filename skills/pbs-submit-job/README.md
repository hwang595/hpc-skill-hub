# PBS Submit Job

Use this skill when a user needs to turn a command into a PBS, OpenPBS, or PBS
Pro batch job.

## Assumptions

- The cluster uses PBS-style `qsub` submission.
- Users submit jobs from a login or submit node.
- Project, queue, GPU, and MPI resource syntax may be site-specific.
- PBS directives must appear before the first executable shell command.

## How To Use

Pick the closest example under `examples/`, replace placeholders such as
`<project>` and `<queue>`, then submit:

```bash
qsub examples/cpu.pbs
```

For a first run, keep the wall time short and write output to a test directory.
Use `qstat -f <job-id>` or the site-recommended queue command to inspect the
submitted job.

## Safety Notes

This skill is `medium` risk because `qsub` allocates shared compute resources.
Review resource requests before submitting. PBS implementations differ in GPU,
place, queue, and project syntax, so treat the examples as safe starting points
rather than site policy.

## Success Criteria

- `qsub` prints a job id.
- `qstat -f <job-id>` or the local status command shows the job queued,
  running, or completed.
- The output file contains the expected hostname, timestamp, working directory,
  and command output.
