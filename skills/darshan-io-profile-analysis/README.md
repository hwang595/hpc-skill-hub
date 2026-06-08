# Darshan I/O Profile Analysis

Use this skill when a workload already produced a Darshan log and the next step
is to turn that log into evidence about I/O behavior, not to run a new
benchmark.

Darshan logs can reveal executable names, job ids, user ids, file paths, mount
points, and accessed filenames. Keep reports public-safe before attaching them
to issues, pull requests, tickets, or community discussions.

## Example

Analyze one existing log:

```bash
bash examples/analyze-darshan-log.sh /path/to/job.darshan.gz darshan-report
```

The script writes parser output and review notes to `darshan-report`. Optional
PDF, per-file, and DXT summaries are listed in `optional-commands.sh` and stay
disabled unless requested through explicit environment variables.

## What It Collects

- `darshan-parser` text output for the log.
- Optional `darshan-parser --perf`, `--file`, and `--total` summaries when the
  installed utility supports them.
- `darshan-config --log-path` and version/configuration hints when available.
- Review notes for POSIX, MPI-IO, HDF5, PnetCDF, shared-file, small-I/O,
  metadata, and imbalance questions.
- Explicit commands for optional PDF, per-file, and DXT summaries.

## Safety Notes

This skill is `low` risk because the default workflow only reads a user-provided
Darshan log and writes local analysis files. It does not submit jobs, enable
instrumentation, preload libraries, change Darshan runtime configuration, or
scan a site log directory automatically.

Do not publish raw logs or parser output without checking paths, user ids,
executable names, job ids, file names, and mount points. Per-file summaries and
DXT traces may be especially sensitive and can also create a lot of output.

## Success Criteria

- The report identifies whether Darshan utility commands were available.
- Parser output captures job-level metadata, mounted filesystems, modules, and
  file records when the log is valid.
- Optional summary commands are reviewable before they are run.
- Review notes distinguish I/O pattern evidence from storage benchmark claims.
- Public handoff material redacts private paths, users, job ids, and filenames.

## Instrumenting New Runs

Use `examples/instrumentation-checklist.md` before collecting new logs. New
instrumentation can involve compiler wrappers, `LD_PRELOAD`, site policy,
environment variables, or DXT trace settings, so it should be reviewed before a
production run.
