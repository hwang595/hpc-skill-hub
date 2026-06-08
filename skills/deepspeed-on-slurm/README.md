# DeepSpeed On Slurm

Use this skill when a large model training job needs a conservative DeepSpeed
launch pattern on a Slurm GPU cluster.

## Example

Create a launch plan and environment report:

```bash
sbatch examples/deepspeed-slurm.sbatch
```

After reviewing the environment, run a tiny DeepSpeed smoke test explicitly:

```bash
RUN_DEEPSPEED_SMOKE=1 sbatch examples/deepspeed-slurm.sbatch
```

## Pattern

- Start with one short GPU allocation before scaling to multi-node training.
- Capture Slurm task layout, GPU visibility, Python package versions, and the
  DeepSpeed config path.
- Keep checkpoint, log, and dataset paths separate from ephemeral scratch.
- Run a tiny DeepSpeed smoke test before launching expensive training.
- Scale nodes, ZeRO stage, offload, precision, and checkpoint cadence only after
  the smoke test and data staging pattern are understood.

## Safety Notes

This skill is `medium` risk because DeepSpeed jobs can consume expensive GPU,
network, memory, and storage resources. The included Slurm script defaults to
plan-only mode and runs the smoke test only when `RUN_DEEPSPEED_SMOKE=1` is set.
The smoke test does not download data, train a real model, or write checkpoints.

## Success Criteria

- The launch plan records Slurm task layout, GPU visibility, and DeepSpeed
  availability.
- The config file is explicit and stored with the run record.
- The smoke test imports DeepSpeed and PyTorch, initializes a tiny model, and
  completes one training step.
- The real training job has reviewed checkpoint and log paths before scaling.
