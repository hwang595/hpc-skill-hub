#!/usr/bin/env bash
set -euo pipefail

image="${1:-<image.sif>}"
container_app="${2:-<container-app>}"
mpi_dir="${3:-}"

echo "== host =="
hostname
command -v apptainer || command -v singularity || true
command -v srun || true
command -v mpirun || true
command -v mpiexec || true
mpirun --version 2>/dev/null | head -n 1 || true

echo "== image =="
apptainer inspect "${image}" 2>/dev/null | sed -n '1,20p' || true

echo "== container commands =="
bind_args=()
if [[ -n "${mpi_dir}" ]]; then
  bind_args+=(--bind "${mpi_dir}:${mpi_dir}:ro")
fi

apptainer exec \
  --cleanenv \
  "${bind_args[@]}" \
  "${image}" \
  /bin/sh -lc "hostname; command -v mpirun || true; command -v mpiexec || true; test -e '${container_app}' && echo app-present || true"

echo "== next =="
echo "Review host/container MPI compatibility, then submit a one-node or tiny two-node smoke test."
