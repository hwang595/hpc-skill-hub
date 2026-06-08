# Apptainer Run Container

Use this skill when a workload is packaged as an Apptainer/Singularity image and
needs to run on a shared HPC cluster.

## Examples

```bash
bash examples/inspect-image.sh /path/to/image.sif
sbatch examples/run-container.sbatch
```

## Adaptation Points

- Replace `<image.sif>` with a local SIF image.
- Bind only the directories needed by the workload.
- Use `--nv` for NVIDIA GPUs or `--rocm` for AMD GPUs when supported.
- Set the working directory explicitly with `--pwd`.

## Safety Notes

This skill is `medium` risk because the Slurm example allocates compute time and
the container can write to bound host directories.
