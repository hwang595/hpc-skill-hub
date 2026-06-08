# HTCondor Submit Job

Use this skill when a user needs to turn a command or many independent tasks
into HTCondor jobs.

## Assumptions

- The site uses HTCondor and allows user jobs through `condor_submit`.
- The submit host can see the executable and any input files named by the submit
  description, or the site uses HTCondor file transfer.
- Accounting groups, containers, GPU names, and file-transfer policy may be
  site-specific.

## How To Use

Pick the closest submit file under `examples/`, review resource requests and
log paths, then submit:

```bash
condor_submit examples/cpu.sub
```

For a first run, keep `queue 1`, use tiny inputs, and inspect the result with:

```bash
condor_q <cluster-id>
```

## Safety Notes

This skill is `medium` risk because one submit description can queue many jobs,
consume shared execute slots, and create many output files. Review `queue`
counts, resource requests, file transfer settings, and per-process log names
before submitting.

## Success Criteria

- `condor_submit` prints a cluster or job id.
- `condor_q <cluster-id>` shows jobs idle, running, held, or completed according
  to site policy.
- Per-process stdout, stderr, and log files are written to the configured output
  directory.
