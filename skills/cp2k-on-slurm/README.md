# CP2K On Slurm

Use this skill when a simulation team wants to run CP2K jobs on Slurm with an
explicit MPI/OpenMP layout, CP2K data-file checks, output capture, and restart
planning.

## Example

Create a dry-run launch plan:

```bash
sbatch examples/cp2k-smoke.sbatch
```

After loading a site-approved CP2K module or container and pointing to reviewed
data files, run the small water energy example:

```bash
RUN_CP2K=1 \
CP2K_BASIS_FILE=/path/to/BASIS_MOLOPT \
CP2K_POTENTIAL_FILE=/path/to/GTH_POTENTIALS \
  sbatch examples/cp2k-smoke.sbatch
```

The bundled input template is based on a tiny water single-point energy smoke
test. Replace it with a reviewed project input before production molecular
dynamics, geometry optimization, large cells, or expensive hybrid-functional
calculations.

## Pattern

- Start with dry-run mode and a small input before scaling atom count, cutoff,
  k-points, trajectory output, or run length.
- Match the executable to the site build. Common names include `cp2k.psmp` for
  MPI plus OpenMP and `cp2k.popt` for MPI-only builds.
- Keep `OMP_NUM_THREADS`, `--ntasks`, and `--cpus-per-task` consistent with the
  selected CP2K binary and local binding policy.
- Stage basis set and potential files from a reviewed CP2K data directory, and
  record the exact paths used by the generated input.
- Preserve generated input, stdout, Slurm metadata, executable evidence, and
  restart files under a durable record directory.

## Safety Notes

This skill is `medium` risk because CP2K jobs can consume many MPI ranks, mix
MPI/OpenMP threading, use GPU-enabled builds, and create large restart,
wavefunction, trajectory, or cube files. The example defaults to dry-run mode
and executes CP2K only when `RUN_CP2K=1` is set.

## Success Criteria

- The launch plan records executable, MPI/OpenMP layout, generated input,
  CP2K data-file paths, output file, and restart policy.
- With `RUN_CP2K=1`, CP2K starts through Slurm and writes the configured output
  file.
- The generated input and output are preserved with the run record.
- Restart and continuation files are documented before follow-on calculations.
