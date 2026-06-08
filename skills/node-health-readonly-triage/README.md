# Node Health Readonly Triage

Use this skill when a support team needs quick, read-only evidence about a
Slurm node or partition before deciding whether a user failure is likely caused
by the job, the application environment, or a possible node incident.

The example script does not drain, resume, reboot, cancel, or reconfigure
anything. It writes user-visible scheduler evidence to a local report directory
for human review.

## Assumptions

- The site uses Slurm.
- `sinfo` is available.
- `scontrol`, `squeue`, and `sacct` may be restricted or unavailable depending
  on site policy.
- Node names, partition names, job ids, and reasons may be sensitive at some
  sites. Review and redact before sharing publicly.

## Example

Collect a general node and partition snapshot:

```bash
bash examples/node-health-triage.sh
```

Collect evidence for one node:

```bash
bash examples/node-health-triage.sh <node-name>
```

Include seven days of visible accounting data for the node and write to a named
directory:

```bash
bash examples/node-health-triage.sh <node-name> 7 node-triage-report
```

## Review The Output

The script creates files such as:

- `summary.md`: report scope and handoff guidance.
- `sinfo-nodes.txt`: visible node and partition state.
- `scontrol-node.txt`: optional detailed node record for the selected node.
- `squeue-node.txt`: optional current jobs on the selected node.
- `sacct-node.txt`: optional recent accounting records for the selected node.

Use the evidence to ask focused follow-up questions:

- Is the node `idle`, `alloc`, `mix`, `drain`, `down`, or in another state?
- Is a scheduler reason visible, and is it public enough to share?
- Are multiple users or jobs seeing failures on the same node?
- Does recent accounting show repeated failures, timeouts, or out-of-memory
  states?
- Does this need escalation to facility operations rather than user-level
  debugging?

## Success Criteria

- The report directory exists.
- Missing optional tools are recorded instead of causing a partial report to
  look successful without explanation.
- Every generated file includes the command that produced it.
- The report remains read-only.

## Safety Notes

This skill is low risk because it only reads scheduler state and writes local
text files. It can still reveal operational details such as node names,
partitions, job names, users, accounts, or scheduler reason strings. Treat the
raw report as internal support evidence until it has been reviewed.

Do not use this skill as a replacement for official incident response, node
health automation, or administrator-only diagnostics.
