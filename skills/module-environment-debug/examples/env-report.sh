#!/usr/bin/env bash
set -euo pipefail

target="${1:-}"

echo "== host =="
hostname

echo
echo "== loaded modules =="
module list 2>&1 || true

echo
echo "== common tools =="
for cmd in gcc g++ gfortran cc c++ mpicc mpicxx mpifort mpirun srun python python3 nvcc hipcc; do
  printf "%-10s" "${cmd}"
  command -v "${cmd}" || true
done

echo
echo "== key environment variables =="
for var in PATH LD_LIBRARY_PATH LIBRARY_PATH CPATH CMAKE_PREFIX_PATH MPI_HOME CUDA_HOME ROCM_HOME; do
  printf "%s=%s\n" "${var}" "${!var:-}"
done

if [ -n "${target}" ] && [ -e "${target}" ]; then
  echo
  echo "== linked libraries for ${target} =="
  ldd "${target}" || true
fi
