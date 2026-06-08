# GPU Sanity Check

Use this skill when a GPU job cannot see devices, fails to import CUDA/ROCm
libraries, or behaves differently on login and compute nodes.

## Example

```bash
sbatch examples/gpu-sanity.sbatch
```

## What It Checks

- Slurm GPU allocation variables.
- NVIDIA or AMD management CLI output.
- Python-level visibility for PyTorch when installed.

## Safety Notes

This skill is `medium` risk because it requests a GPU allocation. Keep the wall
time short and use a debug GPU partition where available.
