# Node Failure Review Checklist

Use this checklist after collecting a Slurm node-failure triage report.

## Confirm The Failure Mode

- Does `sacct` show `NODE_FAIL`, `BOOT_FAIL`, `FAILED`, or a child step with a
  stronger node-related signal?
- Is the failure isolated to one node, one partition, one array task, or one
  time window?
- Do logs mention launch failure, lost tasks, slurmstepd, transport errors,
  filesystem I/O errors, GPU loss, or node communication problems?
- Does `sinfo -R` show unavailable-node reasons that line up with the job
  timing?
- Is the node evidence safe to share with the intended audience?

## Choose The Next Action

- Retry a small or single failed array task when the failure appears transient
  and site policy allows it.
- Hand the report to support when many jobs or users hit the same node,
  partition, or unavailable-node reason.
- Use checkpoint/restart when useful work can survive node loss.
- Avoid repeated large retries while a node or partition incident is active.
- Pair with MPI, NCCL, filesystem, or GPU triage skills when logs point to a
  specific subsystem.

## Handoff Notes

- Include `summary.md`, `sacct-accounting.txt`, `scontrol-job.txt`,
  `sinfo-node-reasons.txt`, and relevant log snippets.
- Redact private paths, user names, account names, node names, job names,
  dataset identifiers, and reason strings before public sharing.
- State whether the job is restartable and whether prior retries landed on the
  same node or partition.
