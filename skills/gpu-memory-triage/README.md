# GPU Memory Triage

Use this skill when a GPU workload fails with out-of-memory errors, cannot see
the requested device memory, or behaves differently between debug and production
allocations.

## Example

Submit the read-only triage job:

```bash
sbatch examples/gpu-memory-triage.sbatch
```

Scan an existing training log:

```bash
JOB_LOG=training.out sbatch examples/gpu-memory-triage.sbatch
```

## Pattern

- Confirm the scheduler actually allocated GPUs to the job.
- Record device memory totals and current utilization before changing code.
- Import the framework and print memory visibility without allocating large
  tensors.
- Scan logs for CUDA, ROCm, allocator, dataloader, and host OOM signals.
- Decide whether the next step is allocation repair, batch-size/model changes,
  precision changes, checkpointing, or data-loader tuning.

## Safety Notes

This skill is `low` risk and read-only. It requests a short GPU allocation when
run through Slurm, but the included Python probe does not allocate large tensors
or write checkpoints. Logs may contain private paths, dataset names, or model
identifiers, so treat reports as support artifacts.

## Success Criteria

- The report shows Slurm GPU allocation variables and device visibility.
- NVIDIA or AMD memory totals are captured when vendor tools are available.
- PyTorch memory availability is recorded when PyTorch is installed.
- Log scans surface likely OOM signals without hiding missing evidence.
