# Grid Engine Submit Job

Use this skill when a user needs to turn a command into a Sun Grid Engine,
Oracle Grid Engine, Son of Grid Engine, or Univa Grid Engine `qsub` batch job.

## Assumptions

- The cluster uses Grid Engine-style `qsub` submission.
- Users submit jobs from a login or submit node.
- Project, queue, memory, GPU, and parallel environment syntax may be
  site-specific.
- `#$` directives are interpreted by `qsub` before the job script runs.

## How To Use

Pick the closest example under `examples/`, replace placeholders such as
`<project>` and `<queue>`, then submit:

```bash
qsub examples/cpu.sge
```

For a first run, keep wall time short and write output to a test directory.
Use `qstat -j <job-id>` or the site-recommended status command to inspect the
submitted job.

## Safety Notes

This skill is `medium` risk because `qsub` allocates shared compute resources.
Review slot counts, array ranges, memory requests, and queue policy before
submitting. Grid Engine sites differ in complex names, parallel environments,
and default request files, so treat examples as safe starting points rather
than site policy.

## Success Criteria

- `qsub` prints a job id.
- `qstat -j <job-id>` or the local status command shows the job pending,
  running, or completed.
- The output file contains the expected hostname, timestamp, working directory,
  and command output.
