# CMake HPC Build Site Policy Checklist

Review these items before running a large configure, build, test, or install on
a shared HPC system.

## Build Location

- Use an out-of-source build directory.
- Prefer scratch, project, or a site-approved build filesystem.
- Avoid building large projects in home directories or metadata-sensitive
  shared paths.
- Keep enough quota, inode, and temporary-directory space for generated files.

## Modules And Compilers

- Record loaded modules before configure.
- Confirm `CC`, `CXX`, and `FC` match the intended compiler family.
- Confirm `mpicc`, `mpicxx`, and `mpifort` come from the intended MPI module.
- Confirm CUDA, ROCm, HDF5, NetCDF, BLAS/LAPACK, and other dependencies are
  found from the intended prefixes.

## Running Builds

- Use a build node or scheduled allocation for expensive builds.
- Limit parallelism to the CPUs and memory available to the session.
- Avoid tests that launch MPI jobs on login nodes.
- Run configure, build, test, and install as separate phases.

## Installing

- Install only to a user-owned prefix unless a software maintainer approves
  the destination.
- Do not overwrite production module trees from an unreviewed build.
- Preserve configure, build, test, and install logs for support handoff.

## Sharing

- Redact private paths, project names, account strings, and hostnames before
  posting logs publicly.
