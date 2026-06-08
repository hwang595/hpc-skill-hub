# NCCL Diagnostics

Use this skill when a distributed GPU job hangs, times out, or fails during
NCCL process-group initialization or collective communication.

## Example

Collect environment and topology evidence:

```bash
sbatch examples/nccl-diagnostics.sbatch
```

After confirming the allocation is appropriate and `all_reduce_perf` is
available, run a small NCCL test explicitly:

```bash
RUN_NCCL_TESTS=1 sbatch examples/nccl-diagnostics.sbatch
```

## Pattern

- Start with one short GPU allocation and capture the scheduler environment.
- Record GPU visibility and topology before changing communication settings.
- Enable `NCCL_DEBUG=INFO` and a focused `NCCL_DEBUG_SUBSYS` value.
- Compare a failing training job against a tiny optional `nccl-tests` run.
- Attach the diagnostic log to the support ticket or training issue.

## Safety Notes

This skill is `medium` risk because it requests GPU resources and can exercise
interconnects. The example defaults to evidence collection only. It runs
`all_reduce_perf` only when `RUN_NCCL_TESTS=1` is set, and the default test size
is intentionally small.

## Success Criteria

- The log records Slurm task layout, GPU visibility, and selected NCCL/CUDA
  environment variables.
- `nvidia-smi topo -m` output is captured when `nvidia-smi` is available.
- If `RUN_NCCL_TESTS=1`, `all_reduce_perf` completes at the requested scale or
  fails with a captured NCCL debug message.
- The evidence is enough to decide whether the next step is application-level
  debugging, environment repair, or facility/network escalation.
