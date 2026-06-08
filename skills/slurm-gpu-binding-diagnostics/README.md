# Slurm GPU Binding Diagnostics

Use this skill when a multi-GPU job starts but tasks appear to pile onto one
device, see different GPU ids than expected, ignore a requested GPU binding
policy, or behave differently across nodes. It focuses on Slurm GPU allocation
and per-task visibility evidence rather than framework-specific training code.

## Example

Replace `<account>` and `<gpu-partition>`, then submit in dry-run mode first:

```bash
sbatch examples/gpu-binding-diagnostics.sbatch
```

Dry-run mode writes the intended `srun` command without launching the per-task
probe. To collect a small binding report:

```bash
RUN_GPU_BINDING_PROBE=1 \
GPU_TASKS=2 \
GPUS_PER_TASK=1 \
GPU_BIND=verbose,closest \
  sbatch examples/gpu-binding-diagnostics.sbatch
```

Use the same partition, GPU type, task shape, and launch policy that the real
workload uses before comparing results.

## Pattern

- Request a small GPU allocation with explicit task and GPU counts.
- Record `SLURM_*`, `CUDA_VISIBLE_DEVICES`, `ROCR_VISIBLE_DEVICES`, and
  `HIP_VISIBLE_DEVICES`.
- Capture `nvidia-smi -L`, `nvidia-smi topo -m`, or `rocm-smi` output when the
  vendor tool is available.
- Launch one short `srun` step with the reviewed `--gpu-bind` policy.
- Compare local task ids, visible device lists, and Slurm GPU variables.
- Change one setting at a time, such as `--gpus-per-task`, `--gpus-per-node`,
  `--gpu-bind`, or framework local-rank handling.

## Safety Notes

This skill is `medium` risk because it submits a GPU job and can reserve scarce
accelerators. The default job is intentionally tiny, and
`RUN_GPU_BINDING_PROBE` defaults to `0` so users can inspect the launch plan
before consuming GPU time. Do not publish raw reports if they contain private
node names, GPU UUIDs, partition names, or site policy details.

## Success Criteria

- Dry-run mode prints the intended `srun` command and GPU binding policy.
- `gpu-topology.txt` records visible Slurm GPU variables and optional vendor
  topology evidence.
- `gpu-binding.tsv` contains one row per Slurm task.
- Each task sees the intended visible GPU set for the selected binding policy.
- Framework launchers use local rank or visible-device ordering consistently
  with the Slurm evidence.
