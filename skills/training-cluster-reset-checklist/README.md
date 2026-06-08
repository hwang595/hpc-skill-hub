# Training Cluster Reset Checklist

Use this skill when instructors or HPC support teams need a repeatable way to
prepare a training environment before a workshop, monitor it during class, and
review it after the event.

The included preflight script is read-only. Cleanup and reset actions stay in a
human-reviewed checklist because training environments often involve accounts,
quotas, shared filesystems, reservation policy, licensed software, and local
security rules.

## Assumptions

- The training environment uses Slurm or a Slurm-backed teaching partition.
- Some commands may be unavailable to instructors and should be reviewed by
  local support staff.
- Workshop identifiers, account names, reservations, partitions, and paths may
  be private at some sites. Use public placeholders in shared material.
- Destructive cleanup is not portable and should live in site-specific runbooks,
  not in the core skill.

## Example

Collect a general preflight report:

```bash
bash examples/training-preflight.sh
```

Collect a report for a named event and partition:

```bash
bash examples/training-preflight.sh intro-hpc-2026 debug
```

Write to an explicit output directory:

```bash
bash examples/training-preflight.sh intro-hpc-2026 debug training-preflight-report
```

Then review:

```bash
less examples/reset-checklist.md
```

## What To Check

- The training partition or reservation is visible.
- Queue depth is low enough for short exercises.
- Example modules, Python environments, containers, and workflow tools are
  visible before learners arrive.
- Shared example data and scratch/project paths have enough space.
- Known test jobs from previous workshops are complete or intentionally kept.
- Post-workshop cleanup has approval from the site owner.

## Success Criteria

- The preflight report directory exists.
- Missing optional commands are recorded clearly.
- The reset checklist is reviewed by an instructor and a local site contact.
- No cleanup command is run from this skill without site-specific approval.

## Safety Notes

This skill is medium risk because training reset workflows often lead to
cleanup, account, reservation, or shared-filesystem actions. The portable
examples are read-only by design. Keep destructive steps in private,
site-reviewed runbooks or public site adapters that explain policy without
exposing sensitive details.
