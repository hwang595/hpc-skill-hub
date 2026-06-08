#!/usr/bin/env bash
#SBATCH --job-name=hybrid-mpi-openmp
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=hybrid-mpi-openmp-%j.out

set -euo pipefail

export RUN_HYBRID_PROBE="${RUN_HYBRID_PROBE:-0}"
export MPI_MODULE="${MPI_MODULE:-}"
export MPI_TASKS="${MPI_TASKS:-${SLURM_NTASKS:-4}}"
export OMP_THREADS="${OMP_THREADS:-${SLURM_CPUS_PER_TASK:-2}}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-${OMP_THREADS}}"
export OMP_PLACES="${OMP_PLACES:-cores}"
export OMP_PROC_BIND="${OMP_PROC_BIND:-close}"
export CPU_BIND="${CPU_BIND:-verbose,cores}"
export OPENMP_FLAG="${OPENMP_FLAG:--fopenmp}"
export OUTPUT_DIR="${OUTPUT_DIR:-hybrid-mpi-openmp-${SLURM_JOB_ID:-manual}}"

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

probe_source="examples/hybrid_mpi_openmp_probe.c"
probe_binary="${OUTPUT_DIR}/hybrid_mpi_openmp_probe"
topology_report="${OUTPUT_DIR}/topology.txt"
rank_thread_report="${OUTPUT_DIR}/rank-thread-affinity.tsv"

{
  echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_HYBRID_PROBE=${RUN_HYBRID_PROBE}"
  echo "MPI_MODULE=${MPI_MODULE}"
  echo "MPI_TASKS=${MPI_TASKS}"
  echo "OMP_THREADS=${OMP_THREADS}"
  echo "OMP_NUM_THREADS=${OMP_NUM_THREADS}"
  echo "OMP_PLACES=${OMP_PLACES}"
  echo "OMP_PROC_BIND=${OMP_PROC_BIND}"
  echo "CPU_BIND=${CPU_BIND}"
  echo "OPENMP_FLAG=${OPENMP_FLAG}"
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-unset}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-unset}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-unset}"
  echo "SLURM_NTASKS_PER_NODE=${SLURM_NTASKS_PER_NODE:-unset}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-unset}"
  echo "SLURM_CPU_BIND=${SLURM_CPU_BIND:-unset}"
  echo
  echo "== command paths =="
  command -v mpicc || true
  command -v srun || true
  command -v lscpu || true
  echo
  echo "== lscpu =="
  lscpu 2>/dev/null || true
} > "${topology_report}"

compile_command=(mpicc "${OPENMP_FLAG}" "${probe_source}" -o "${probe_binary}")
launch_command=(srun --ntasks "${MPI_TASKS}")
if [ -n "${CPU_BIND}" ]; then
  launch_command+=(--cpu-bind="${CPU_BIND}")
fi
launch_command+=("${probe_binary}")

echo "Wrote topology report: ${topology_report}"
printf 'compile_command='
printf '%q ' "${compile_command[@]}"
printf '\n'
printf 'launch_command='
printf '%q ' "${launch_command[@]}"
printf '\n'

if [ "${RUN_HYBRID_PROBE}" != "1" ]; then
  echo "RUN_HYBRID_PROBE=0, dry-run complete. Set RUN_HYBRID_PROBE=1 to compile and run."
  exit 0
fi

"${compile_command[@]}"
"${launch_command[@]}" | tee "${rank_thread_report}"
echo "Wrote rank/thread affinity report: ${rank_thread_report}"
