# Output Log Review Checklist

Use this checklist after collecting a Slurm output-log triage report.

## Confirm Where Slurm Tried To Write

- Does `sacct-accounting.txt` show `StdOut` or `StdErr` filename patterns?
- Does `scontrol-job.txt` show `WorkDir`, `StdOut`, `StdErr`, or `Command`?
- Was the user searching from the same directory where the job was submitted or
  where `--chdir` placed the job?
- Was the job an array task that used `slurm-%A_%a.out` instead of
  `slurm-%j.out`?
- Were stdout and stderr split into different files?

## Confirm Whether The Path Was Writable

- Did the parent directory exist before the job started?
- Could the batch host write to that filesystem at launch time?
- Do `path-checks.txt` and any provided logs show permission, quota, inode, or
  stale-file symptoms?
- Is the file present but zero bytes, or does it contain only scheduler-level
  messages?

## Choose The Next Action

- Add explicit `#SBATCH --output` and `#SBATCH --error` paths after creating
  the parent log directory.
- Add early `echo`, `pwd`, `hostname`, and `date` lines to the script.
- Use absolute paths for support reproduction, then simplify once the issue is
  understood.
- Pair with filesystem or permission triage when the parent directory or log
  file is not writable.
- Pair with job-failure triage when the log exists and shows the workload
  started but failed.

## Handoff Notes

- Include `summary.md`, `sacct-accounting.txt`, `scontrol-job.txt`,
  `path-hints.txt`, `path-checks.txt`, and relevant log snippets.
- Redact private paths, user names, account names, job names, project names,
  dataset identifiers, and command arguments before public sharing.
