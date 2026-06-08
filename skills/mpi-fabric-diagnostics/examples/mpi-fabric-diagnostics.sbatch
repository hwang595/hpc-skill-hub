#!/usr/bin/env bash
#SBATCH --job-name=mpi-fabric-diag
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=mpi-fabric-diag-%j.out

set -euo pipefail

export RUN_MPI_FABRIC_PROBE="${RUN_MPI_FABRIC_PROBE:-0}"
export MPI_MODULE="${MPI_MODULE:-}"
export MPI_TASKS="${MPI_TASKS:-${SLURM_NTASKS:-4}}"
export OUTPUT_DIR="${OUTPUT_DIR:-mpi-fabric-${SLURM_JOB_ID:-manual}}"
export MPI_LAUNCHER="${MPI_LAUNCHER:-srun}"
export PROBE_ITERATIONS="${PROBE_ITERATIONS:-100}"

mkdir -p "${OUTPUT_DIR}"

if [ -n "${MPI_MODULE}" ]; then
  if type module >/dev/null 2>&1; then
    module purge
    module load "${MPI_MODULE}"
  else
    echo "MPI_MODULE is set, but the module command is unavailable." >&2
    exit 2
  fi
fi

probe_source="examples/mpi_fabric_probe.c"
probe_binary="${OUTPUT_DIR}/mpi_fabric_probe"
fabric_report="${OUTPUT_DIR}/fabric-environment.txt"
probe_report="${OUTPUT_DIR}/mpi-fabric-probe.tsv"

{
  echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_MPI_FABRIC_PROBE=${RUN_MPI_FABRIC_PROBE}"
  echo "MPI_MODULE=${MPI_MODULE}"
  echo "MPI_LAUNCHER=${MPI_LAUNCHER}"
  echo "MPI_TASKS=${MPI_TASKS}"
  echo "PROBE_ITERATIONS=${PROBE_ITERATIONS}"
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-unset}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-unset}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-unset}"
  echo "SLURM_NTASKS_PER_NODE=${SLURM_NTASKS_PER_NODE:-unset}"
  echo
  echo "== selected environment =="
  env | sort | grep -E '^(SLURM|MPI|PMI|PMIX|OMPI|MPICH|I_MPI|UCX|FI_|OFI|NCCL)_' || true
  echo
  echo "== command paths =="
  command -v mpicc || true
  command -v "${MPI_LAUNCHER}" || true
  command -v ompi_info || true
  command -v ucx_info || true
  command -v fi_info || true
  command -v ibv_devinfo || true
  echo
  echo "== mpicc version =="
  mpicc --version 2>&1 | head -n 5 || true
  echo
  echo "== Open MPI transport hints =="
  ompi_info --parsable --all 2>/dev/null | grep -Ei '(^mca:(pml|btl|mtl|osc|coll)|ucx|ofi|pmix)' | head -n 120 || true
  echo
  echo "== UCX version and devices =="
  ucx_info -v 2>/dev/null || true
  ucx_info -d 2>/dev/null | head -n 160 || true
  echo
  echo "== libfabric providers =="
  fi_info -l 2>/dev/null || true
  fi_info -e 2>/dev/null | head -n 120 || true
  echo
  echo "== InfiniBand devices =="
  ibv_devinfo -l 2>/dev/null || true
} > "${fabric_report}"

compile_command=(mpicc "${probe_source}" -o "${probe_binary}")
if [ "${MPI_LAUNCHER}" = "srun" ]; then
  launch_command=("${MPI_LAUNCHER}" --ntasks "${MPI_TASKS}" "${probe_binary}")
else
  launch_command=("${MPI_LAUNCHER}" -np "${MPI_TASKS}" "${probe_binary}")
fi

echo "Wrote fabric environment report: ${fabric_report}"
printf 'compile_command='
printf '%q ' "${compile_command[@]}"
printf '\n'
printf 'launch_command='
printf '%q ' "${launch_command[@]}"
printf '\n'

if [ "${RUN_MPI_FABRIC_PROBE}" != "1" ]; then
  echo "RUN_MPI_FABRIC_PROBE=0, dry-run complete. Set RUN_MPI_FABRIC_PROBE=1 to compile and run."
  exit 0
fi

"${compile_command[@]}"
"${launch_command[@]}" | tee "${probe_report}"
echo "Wrote MPI fabric probe report: ${probe_report}"
