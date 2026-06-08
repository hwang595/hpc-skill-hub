# Parallel HDF5 NetCDF Preflight

Use this skill before running a data-intensive MPI application that writes
HDF5, NetCDF-4, classic NetCDF through PnetCDF, or related MPI-IO output. It is
especially useful for weather, climate, simulation, electronic-structure, and
analysis workflows where build mismatches can look like filesystem or MPI
failures.

## Example

Collect a report without compiling or running MPI jobs:

```bash
bash examples/parallel-io-preflight.sh
```

Write the report to an explicit directory and prepare smoke-test commands for
an approved scratch path:

```bash
OUTPUT_DIR=parallel-io-report SCRATCH_DIR=/path/to/scratch MPI_TASKS=2 \
  bash examples/parallel-io-preflight.sh
```

## What It Checks

- HDF5 wrapper availability: `h5pcc`, `h5cc`, and `h5dump`.
- HDF5 build configuration when exposed by the wrapper.
- NetCDF build configuration through `nc-config --all`.
- NetCDF parallel capability hints such as `--has-parallel4` when supported.
- MPI compiler wrapper identity through `mpicc`.
- A reviewable build and run plan for tiny parallel HDF5 and NetCDF C smoke
  programs.

## Safety Notes

This skill is `medium` risk because the optional smoke tests compile code, run
MPI tasks, and write small files to a shared filesystem. The preflight script
itself does not run the smoke tests; it writes a plan for a user or support
engineer to review first.

Use a small task count, a short test allocation, and a scratch or project path
approved for temporary I/O. Do not run smoke tests in a tight loop or on a
login node.

## Success Criteria

- The report records which HDF5, NetCDF, MPI, and launcher tools are visible.
- HDF5 reports parallel support or the absence of a parallel wrapper is clear.
- NetCDF reports whether parallel NetCDF-4 support appears enabled.
- The generated build plan uses site-visible wrappers instead of hard-coded
  include or library paths.
- If the optional smoke tests are run, the output file can be inspected with
  `h5dump` or `ncdump` without errors.
