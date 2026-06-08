#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: SOURCE_DIR=/path/to/source [BUILD_DIR=...] [INSTALL_PREFIX=...] %s\n' "$0"
  printf '\n'
  printf 'Default mode writes environment evidence and a reviewable CMake build plan.\n'
  printf 'Set RUN_CMAKE_CONFIGURE=1, RUN_CMAKE_BUILD=1, RUN_CTEST=1, or RUN_CMAKE_INSTALL=1 to execute phases.\n'
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

source_dir="${SOURCE_DIR:-${1:-}}"
if [ -z "${source_dir}" ]; then
  usage >&2
  exit 2
fi

if [ ! -f "${source_dir}/CMakeLists.txt" ]; then
  printf 'CMakeLists.txt not found under SOURCE_DIR: %s\n' "${source_dir}" >&2
  exit 1
fi

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
build_dir="${BUILD_DIR:-${PWD}/build-hpc-${timestamp}}"
install_prefix="${INSTALL_PREFIX:-${PWD}/install-hpc}"
report_dir="${REPORT_DIR:-${PWD}/cmake-hpc-build-report-${timestamp}}"
generator="${CMAKE_GENERATOR:-Unix Makefiles}"
build_type="${CMAKE_BUILD_TYPE:-Release}"
parallel_jobs="${CMAKE_BUILD_PARALLEL_LEVEL:-${SLURM_CPUS_PER_TASK:-2}}"
extra_options="${CMAKE_CACHE_OPTIONS:-}"

mkdir -p "${report_dir}"

capture() {
  local output_file="$1"
  shift
  {
    printf '$'
    printf ' %q' "$@"
    printf '\n\n'
    "$@"
  } >"${output_file}" 2>&1 || {
    printf '\nWARN: command exited non-zero; inspect this output before relying on it.\n' >>"${output_file}"
  }
}

capture_shell() {
  local output_file="$1"
  shift
  {
    printf '$ %s\n\n' "$*"
    "$@"
  } >"${output_file}" 2>&1 || {
    printf '\nWARN: command exited non-zero; inspect this output before relying on it.\n' >>"${output_file}"
  }
}

record_missing() {
  local output_file="$1"
  local tool_name="$2"
  {
    printf 'MISSING: %s was not found in PATH.\n' "${tool_name}"
    printf 'Load the appropriate compiler, CMake, MPI, or build-tool modules before running build phases.\n'
  } >"${output_file}"
}

for tool in cmake ctest ninja make cc c++ gcc g++ gfortran mpicc mpicxx mpifort; do
  if command -v "${tool}" >/dev/null 2>&1; then
    capture "${report_dir}/${tool}-version.txt" "${tool}" --version
  else
    record_missing "${report_dir}/${tool}-version.txt" "${tool}"
  fi
done

{
  printf 'SOURCE_DIR=%s\n' "${source_dir}"
  printf 'BUILD_DIR=%s\n' "${build_dir}"
  printf 'INSTALL_PREFIX=%s\n' "${install_prefix}"
  printf 'REPORT_DIR=%s\n' "${report_dir}"
  printf 'CMAKE_GENERATOR=%s\n' "${generator}"
  printf 'CMAKE_BUILD_TYPE=%s\n' "${build_type}"
  printf 'CMAKE_BUILD_PARALLEL_LEVEL=%s\n' "${parallel_jobs}"
  printf 'CMAKE_CACHE_OPTIONS=%s\n' "${extra_options}"
  printf 'RUN_CMAKE_CONFIGURE=%s\n' "${RUN_CMAKE_CONFIGURE:-0}"
  printf 'RUN_CMAKE_BUILD=%s\n' "${RUN_CMAKE_BUILD:-0}"
  printf 'RUN_CTEST=%s\n' "${RUN_CTEST:-0}"
  printf 'RUN_CMAKE_INSTALL=%s\n' "${RUN_CMAKE_INSTALL:-0}"
} >"${report_dir}/build-settings.env"

{
  for var in PATH LD_LIBRARY_PATH LIBRARY_PATH CPATH CMAKE_PREFIX_PATH PKG_CONFIG_PATH MPI_HOME CUDA_HOME ROCM_HOME CC CXX FC; do
    printf '%s=%s\n' "${var}" "${!var-}"
  done
} >"${report_dir}/selected-environment.env"

if command -v module >/dev/null 2>&1; then
  capture_shell "${report_dir}/module-list.txt" bash -lc "module list"
else
  record_missing "${report_dir}/module-list.txt" "module"
fi

configure_cmd=(
  cmake
  -S "${source_dir}"
  -B "${build_dir}"
  -G "${generator}"
  -DCMAKE_BUILD_TYPE="${build_type}"
  -DCMAKE_INSTALL_PREFIX="${install_prefix}"
)

if [ -n "${extra_options}" ]; then
  # shellcheck disable=SC2206
  extra_array=( ${extra_options} )
  configure_cmd+=("${extra_array[@]}")
fi

build_cmd=(cmake --build "${build_dir}" --parallel "${parallel_jobs}")
test_cmd=(ctest --test-dir "${build_dir}" --output-on-failure)
install_cmd=(cmake --install "${build_dir}")

{
  printf '# CMake HPC Build Plan\n\n'
  printf '## Configure\n\n```bash\n'
  printf '%q ' "${configure_cmd[@]}"
  printf '\n```\n\n'
  printf '## Build\n\n```bash\n'
  printf '%q ' "${build_cmd[@]}"
  printf '\n```\n\n'
  printf '## Test\n\n```bash\n'
  printf '%q ' "${test_cmd[@]}"
  printf '\n```\n\n'
  printf '## Install\n\n```bash\n'
  printf '%q ' "${install_cmd[@]}"
  printf '\n```\n\n'
  printf '## Review Notes\n\n'
  printf '%s\n' '- Confirm the compiler and MPI wrappers match the loaded modules.'
  printf '%s\n' '- Keep build directories out of source trees and away from metadata-sensitive filesystems.'
  printf '%s\n' '- Confirm install prefix ownership before enabling RUN_CMAKE_INSTALL=1.'
  printf '%s\n' '- Enable phases one at a time and preserve logs for failed configure/build/test/install steps.'
} >"${report_dir}/build-plan.md"

if [ "${RUN_CMAKE_CONFIGURE:-0}" = "1" ]; then
  capture "${report_dir}/cmake-configure.log" "${configure_cmd[@]}"
fi

if [ "${RUN_CMAKE_BUILD:-0}" = "1" ]; then
  capture "${report_dir}/cmake-build.log" "${build_cmd[@]}"
fi

if [ "${RUN_CTEST:-0}" = "1" ]; then
  capture "${report_dir}/ctest.log" "${test_cmd[@]}"
fi

if [ "${RUN_CMAKE_INSTALL:-0}" = "1" ]; then
  capture "${report_dir}/cmake-install.log" "${install_cmd[@]}"
fi

printf 'CMake HPC build report written to %s\n' "${report_dir}"
