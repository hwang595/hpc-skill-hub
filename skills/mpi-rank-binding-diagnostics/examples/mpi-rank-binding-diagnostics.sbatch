#!/usr/bin/env bash
#SBATCH --job-name=mpi-rank-binding
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=mpi-rank-binding-%j.out

set -euo pipefail

export RUN_MPI_BINDING_PROBE="${RUN_MPI_BINDING_PROBE:-0}"
export MPI_MODULE="${MPI_MODULE:-}"
export MPI_LAUNCHER="${MPI_LAUNCHER:-srun}"
export MPI_TASKS="${MPI_TASKS:-${SLURM_NTASKS:-4}}"
export CPU_BIND="${CPU_BIND:-verbose,cores}"
export OUTPUT_DIR="${OUTPUT_DIR:-mpi-rank-binding-${SLURM_JOB_ID:-manual}}"

mkdir -p "${OUTPUT_DIR}"

if [ -n "${MPI_MODULE}" ]; then
  module purge
  module load "${MPI_MODULE}"
fi

probe_source="examples/mpi_rank_probe.c"
probe_binary="${OUTPUT_DIR}/mpi_rank_probe"
topology_report="${OUTPUT_DIR}/topology.txt"
rank_report="${OUTPUT_DIR}/rank-affinity.tsv"

{
  echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_MPI_BINDING_PROBE=${RUN_MPI_BINDING_PROBE}"
  echo "MPI_MODULE=${MPI_MODULE}"
  echo "MPI_LAUNCHER=${MPI_LAUNCHER}"
  echo "MPI_TASKS=${MPI_TASKS}"
  echo "CPU_BIND=${CPU_BIND}"
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-unset}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-unset}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-unset}"
  echo "SLURM_NTASKS_PER_NODE=${SLURM_NTASKS_PER_NODE:-unset}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-unset}"
  echo "SLURM_CPU_BIND=${SLURM_CPU_BIND:-unset}"
  echo
  echo "== command paths =="
  command -v mpicc || true
  command -v "${MPI_LAUNCHER}" || true
  command -v lscpu || true
  command -v numactl || true
  command -v hwloc-ls || true
  echo
  echo "== lscpu =="
  lscpu 2>/dev/null || true
  echo
  echo "== numactl hardware =="
  numactl --hardware 2>/dev/null || true
  echo
  echo "== hwloc summary =="
  hwloc-ls --of console 2>/dev/null | head -n 80 || true
} > "${topology_report}"

echo "Wrote topology report: ${topology_report}"
echo "compile_command=mpicc ${probe_source} -o ${probe_binary}"

if [ "${MPI_LAUNCHER}" = "srun" ]; then
  launch_command=("${MPI_LAUNCHER}" --ntasks "${MPI_TASKS}")
  if [ -n "${CPU_BIND}" ]; then
    launch_command+=(--cpu-bind="${CPU_BIND}")
  fi
  launch_command+=("${probe_binary}")
else
  launch_command=("${MPI_LAUNCHER}" -np "${MPI_TASKS}" "${probe_binary}")
fi

printf 'launch_command='
printf '%q ' "${launch_command[@]}"
printf '\n'

if [ "${RUN_MPI_BINDING_PROBE}" != "1" ]; then
  echo "RUN_MPI_BINDING_PROBE=0, dry-run complete. Set RUN_MPI_BINDING_PROBE=1 to compile and run."
  exit 0
fi

mpicc "${probe_source}" -o "${probe_binary}"
"${launch_command[@]}" | tee "${rank_report}"
echo "Wrote rank affinity report: ${rank_report}"
