# PyTorch DDP On Slurm

Use this skill when a PyTorch distributed job needs a small, reviewable Slurm
smoke test before launching a real training run.

## Example

Edit account, partition, and environment setup lines, then submit:

```bash
sbatch examples/ddp-smoke.sbatch
```

The example uses `srun` to start one Python process per requested GPU and runs
`examples/ddp_smoke.py`.

## Pattern

- Request a short GPU allocation before testing large training workloads.
- Load or activate the same PyTorch environment used by production jobs.
- Let Slurm provide rank and world-size variables through `srun`.
- Verify CUDA visibility, process group initialization, and one all-reduce.
- Keep the smoke test output with the training job issue or support ticket.

## Safety Notes

This skill is `medium` risk because it requests GPU resources and initializes
distributed communication. Keep wall time short, start with one node, and avoid
running real training until the smoke test succeeds. The included Python script
does not download data, allocate large tensors, or write model checkpoints.

## Success Criteria

- Every rank starts and prints its host, global rank, local rank, and world
  size.
- PyTorch imports successfully and reports whether CUDA is available.
- The distributed process group initializes with `nccl` when GPUs are visible,
  otherwise `gloo`.
- Rank 0 reports the expected all-reduce sum for the chosen world size.
