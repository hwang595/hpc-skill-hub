# Job Failure Triage

Use this skill for an evidence-first first pass over a failed Slurm job before
changing code, dependencies, or resource requests. It correlates scheduler
state and exit code with application logs, then routes the case to a narrower
workflow; it does not claim a root cause from a single keyword.

## Prerequisites

- Obtain the job id when available and identify the corresponding stdout or
  stderr log without exposing private paths in public reports.
- Run from a host where the user may read the job and log. `sacct` or `scontrol`
  can be unavailable because of site policy or accounting retention.
- Preserve the original script, log, and scheduler output before rerunning or
  editing anything. Do not assume a failed batch step and its child steps share
  the same state or exit code.

## Inputs And Outputs

Input is either a log path or a job id plus log path. Output is terminal text
containing available `sacct` and `scontrol` evidence, the last 80 log lines, and
matched failure clues. No files are written or scheduler state changed.

## Workflow

Start with a log-only review when scheduler accounting is unavailable:

```bash
bash examples/triage-slurm-job.sh slurm-123456.out
```

Correlate it with one job when the id is known:

```bash
bash examples/triage-slurm-job.sh 123456 slurm-123456.out
```

Then complete `examples/triage-evidence-checklist.md`: record facts separately
from hypotheses, compare batch and step exit codes, identify the earliest useful
error, and select one narrow follow-up. Reproduce only after the proposed change
and expected signal are explicit.

## Common Signals

| Evidence | Working interpretation | Preferred next step |
| --- | --- | --- |
| `OUT_OF_MEMORY`, cgroup OOM, worker killed | Memory limit or process fan-out may be involved | Use `slurm-oom-memory-triage`; compare request, peak use, and steps |
| `TIMEOUT` or time-limit signal | Walltime expired, possibly after useful checkpoint output | Use `slurm-time-limit-triage`; inspect progress and checkpoint cadence |
| `NODE_FAIL`, launch failure, lost task | Node or infrastructure failure may dominate application exit | Use `slurm-node-failure-triage`; preserve node and step evidence |
| Exit `127`, command not found, module error | Environment or script setup failed before workload start | Inspect module/runtime setup and exact command path |
| Permission denied or no such file | Identity, path traversal, mount, working directory, or staging issue | Verify paths read-only before changing permissions or moving data |
| Python traceback, MPI abort, segmentation fault | Application failure; scheduler state may only report the consequence | Find the first causal application message and minimal reproducer |

Several signals can coexist. For example, an MPI launcher may report an abort
after one rank is OOM-killed. Prefer the earliest scheduler and application
evidence that explains the later cascade.

## Validation

A useful triage report identifies the job and log reviewed, separates observed
facts from hypotheses, accounts for missing evidence, and proposes one bounded
next diagnostic. It is not successful merely because a keyword matched. A root
cause requires consistent scheduler, step, and application evidence or a
controlled reproduction.

## Resource And Cost

The example is read-only and consumes negligible CPU and filesystem bandwidth;
it reads only the selected log and scheduler metadata. A later reproduction can
consume allocation quota, so estimate its CPU, memory, GPU, storage, and
walltime separately and keep it smaller than the original workload when useful.

## Cleanup

No cleanup is required because the script writes no files and changes no jobs.
If a user creates a redacted incident note, retain or delete it under project
policy. Do not cancel, requeue, or resubmit the failed job as part of triage.

## Site Adaptation

Accounting fields, retention, step names, log naming, and support escalation
paths differ by cluster. Treat missing `sacct` data as missing evidence, not
proof that no scheduler failure occurred. Redact usernames, hostnames, accounts,
partitions, project paths, dataset names, and support-only diagnostics before
sharing output publicly.

## Safety Notes

This skill is `low` risk and read-only. Logs can contain secrets, command-line
tokens, private paths, or regulated data fragments. Review and redact output
before pasting it into an agent, issue, benchmark result, or support ticket.
