# CMake HPC Build Preflight

Use this skill before building CMake-based scientific software on an HPC
system, especially when compiler, MPI, CUDA/ROCm, HDF5, NetCDF, BLAS/LAPACK, or
install-prefix choices need to match site modules.

The example script defaults to plan-only mode. It records environment evidence
and writes exact commands, but it does not run configure, build, test, or
install unless the corresponding `RUN_*` variables are set.

## Example

Create a build plan:

```bash
SOURCE_DIR=/path/to/source \
BUILD_DIR=/scratch/$USER/build/my-code \
INSTALL_PREFIX=/project/$USER/apps/my-code \
bash examples/cmake-hpc-build-plan.sh
```

Run phases one at a time after review:

```bash
RUN_CMAKE_CONFIGURE=1 bash examples/cmake-hpc-build-plan.sh
RUN_CMAKE_CONFIGURE=1 RUN_CMAKE_BUILD=1 bash examples/cmake-hpc-build-plan.sh
RUN_CMAKE_CONFIGURE=1 RUN_CMAKE_BUILD=1 RUN_CTEST=1 bash examples/cmake-hpc-build-plan.sh
RUN_CMAKE_INSTALL=1 bash examples/cmake-hpc-build-plan.sh
```

## What It Captures

- CMake, CTest, Ninja, Make, compiler, and MPI wrapper visibility.
- `PATH`, `LD_LIBRARY_PATH`, `LIBRARY_PATH`, `CPATH`, `CMAKE_PREFIX_PATH`,
  `MPI_HOME`, `CUDA_HOME`, `ROCM_HOME`, `CC`, `CXX`, and `FC`.
- Optional module state when `module list` is available.
- Source, build, install-prefix, generator, build type, parallelism, and cache
  options.
- Reviewable configure, build, test, and install commands.

## Safety Notes

This skill is `medium` risk because real builds can consume CPU, memory, disk
space, inodes, and licenses, and installs can overwrite user-owned software
prefixes. Keep build directories out of source trees and use user-owned install
prefixes.

Do not install into shared module trees, system directories, or group software
paths without maintainer approval. Avoid large parallel builds on login nodes.

## Success Criteria

- The selected compiler and MPI wrappers match the intended modules.
- The build directory is out-of-source and on a filesystem suitable for build
  artifacts.
- `CMAKE_INSTALL_PREFIX` is user-owned and reviewable before install.
- Cache options are recorded and can be reproduced.
- Configure, build, test, and install logs are captured separately.
- Any failed phase leaves enough evidence for support or upstream issue
  triage.

## Presets

`examples/CMakePresets.hpc.example.json` shows a portable pattern for storing
common HPC build settings in `CMakePresets.json`. Keep personal paths, accounts,
and site-private module names out of public examples.
