# Ray On Slurm

Use this skill when a Python or AI/HPC workload needs a Ray cluster inside a
Slurm allocation with explicit head-node selection, resource bounds, logs, and
temporary directories.

## Example

Review the account, partition, and Python environment placeholders, then submit
in dry-run mode first:

```bash
sbatch examples/ray-slurm.sbatch
```

Dry-run mode records the launch plan without starting Ray. To run a tiny Ray
task smoke test:

```bash
RUN_RAY_SMOKE=1 \
PYTHON_ENV=/path/to/venv \
RAY_SCRIPT=examples/ray_smoke.py \
  sbatch examples/ray-slurm.sbatch
```

For multi-user clusters, choose a site-approved, non-overlapping port policy
before launching many Ray jobs at once. The example uses `ray symmetric-run`,
with the head port embedded in `--address`; advanced sites should switch to a
manual `ray start` pattern when they need full control of every Ray service
port.

## Pattern

- Activate the same Python environment on every allocated node.
- Use `scontrol show hostnames "$SLURM_JOB_NODELIST"` to pick the head node.
- Keep Ray CPU and GPU counts aligned with `SLURM_CPUS_PER_TASK` and
  `SLURM_GPUS_PER_TASK` or `SLURM_GPUS_ON_NODE`.
- Make the head port explicit in `--address`.
- For production multi-tenant clusters, use a site-reviewed manual `ray start`
  pattern when every Ray service and worker port must be pinned.
- Put Ray temporary files under an explicit user-owned directory.
- Start with `RUN_RAY_SMOKE=0` and inspect the launch plan.
- Use `RUN_RAY_SMOKE=1` only on a short test allocation before scaling up.

## Safety Notes

This skill is `medium` risk because Ray starts long-lived processes across all
allocated nodes and binds multiple ports. Port collisions, stale processes,
oversubscribed GPUs, and node-local temporary data are common failure modes.
Keep initial runs short, make the head port explicit, and confirm local network
policy before using dashboards or Ray Client ports.

## Success Criteria

- The dry-run log records selected head node, Ray address, optional port policy,
  CPU/GPU counts, and temporary directory.
- With `RUN_RAY_SMOKE=1`, Ray starts across the requested Slurm nodes.
- The smoke script connects to the Ray cluster and reports available resources.
- A JSON result file is written under the record directory.
- Ray processes stop when the Slurm job exits.
