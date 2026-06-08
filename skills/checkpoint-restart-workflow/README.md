# Checkpoint Restart Workflow

Use this skill when a job may run longer than a queue limit, may be preempted,
or is expensive enough that restarting from the beginning would waste compute
time.

## Example

Run the toy resumable command locally:

```bash
bash examples/resume-progress.sh checkpoints/demo 5
bash examples/resume-progress.sh checkpoints/demo 5
```

Submit the Slurm wrapper after replacing `<account>` and `<partition>`:

```bash
sbatch examples/checkpoint-wrapper.sbatch
```

## Design Pattern

- Write checkpoints to a durable user-owned directory.
- Detect existing progress before starting work.
- Keep logs separate from checkpoint state.
- Use a Slurm signal handler when site policy supports preemption or time-limit
  warnings.
- Make reruns idempotent: a second run should continue or verify completion,
  not corrupt previous state.

## Safety Notes

This skill is `medium` risk because the wrapper submits jobs and writes user
files. Checkpoint directories can grow large, so monitor storage usage and
retention policy.

## Success Criteria

- A fresh run creates checkpoint state.
- A second run detects existing state and resumes or exits cleanly.
- Partial output is not mistaken for verified final output.
- The job log records checkpoint directory, start mode, and completion status.
