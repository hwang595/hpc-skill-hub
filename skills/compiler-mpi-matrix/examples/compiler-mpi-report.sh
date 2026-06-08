#!/usr/bin/env bash
set -euo pipefail

target="${1:-}"
outdir="${OUTDIR:-compiler-mpi-report}"
mkdir -p "${outdir}"
report="${outdir}/compiler-mpi-report.txt"

{
  echo "== host =="
  hostname

  echo
  echo "== loaded modules =="
  module list 2>&1 || true

  echo
  echo "== compiler and mpi commands =="
  for cmd in cc c++ gcc g++ gfortran clang clang++ mpicc mpicxx mpifort mpirun srun; do
    printf "%-10s" "${cmd}"
    command -v "${cmd}" || true
  done

  echo
  echo "== wrapper details =="
  for wrapper in mpicc mpicxx mpifort; do
    if command -v "${wrapper}" >/dev/null 2>&1; then
      echo "-- ${wrapper} --"
      "${wrapper}" --version 2>&1 | head -n 3 || true
      "${wrapper}" -show 2>&1 || "${wrapper}" --showme 2>&1 || true
    fi
  done

  echo
  echo "== key environment variables =="
  for var in PATH LD_LIBRARY_PATH LIBRARY_PATH CPATH CMAKE_PREFIX_PATH MPI_HOME CC CXX FC; do
    printf "%s=%s\n" "${var}" "${!var:-}"
  done

  if [ -n "${target}" ] && [ -e "${target}" ]; then
    echo
    echo "== linked libraries for ${target} =="
    ldd "${target}" || true
  fi
} > "${report}"

if [ "${COMPILE_SMOKE:-0}" = "1" ]; then
  if command -v mpicc >/dev/null 2>&1; then
    mpicc examples/hello-mpi.c -o "${outdir}/hello-mpi"
    echo "smoke_binary=${outdir}/hello-mpi" >> "${report}"
  else
    echo "COMPILE_SMOKE requested but mpicc was not found." >> "${report}"
  fi
fi

echo "report=${report}"
