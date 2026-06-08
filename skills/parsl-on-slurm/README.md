# Parsl On Slurm

Use this skill when a Python workflow should run Parsl tasks through Slurm with
explicit provider settings, bounded worker blocks, and reviewable logs.

## Example

Review the account, partition, and Python environment placeholders, then start
with dry-run mode:

```bash
bash examples/parsl-slurm-demo.sh
```

Dry-run mode writes a JSON launch plan without asking Parsl to submit Slurm
worker blocks. To run a tiny smoke workflow on a Slurm test partition:

```bash
RUN_PARSL=1 \
PARSL_ACCOUNT=<account> \
PARSL_PARTITION=<partition> \
PARSL_BLOCKS=1 \
PYTHON_ENV=/path/to/venv \
  bash examples/parsl-slurm-demo.sh
```

Keep `PARSL_BLOCKS`, `PARSL_NODES_PER_BLOCK`, `PARSL_CORES_PER_NODE`,
`PARSL_MAX_WORKERS_PER_NODE`, and `PARSL_WALLTIME` small until the site-specific
worker shape has been reviewed.

## Pattern

- Prepare a Python environment with `parsl`.
- Choose one executor label and one Slurm provider shape.
- Keep account, partition, walltime, nodes per block, cores per node, and max
  workers per node explicit.
- Use `RUN_PARSL=0` first to write and inspect the launch plan.
- Put Parsl run directories and task output under explicit user-owned paths.
- Scale by blocks only after a tiny smoke workflow succeeds.
- Record result JSON, run directory, worker block count, and relevant Slurm job
  ids for support handoff.
- Call `parsl.dfk().cleanup()` so provider jobs are cleaned up when the driver
  exits.

## Safety Notes

This skill is `medium` risk because a single Parsl driver can submit and scale
Slurm worker blocks. Start with one short block on a test partition, avoid
adaptive scaling until site policy is clear, and keep worker logs under a
bounded directory. Do not run the driver from a shared login node for long
workflows unless local policy explicitly permits that pattern.

## Success Criteria

- Dry-run mode writes a launch plan with the expected account, partition,
  block count, worker count, walltime, and run directory.
- With `RUN_PARSL=1`, Parsl creates one small Slurm-backed worker block.
- The smoke workflow runs several tiny Python apps and writes `parsl-result.json`.
- Parsl run logs are stored under the configured run directory.
- Worker blocks are cleaned up when the driver exits.
