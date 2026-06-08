#!/usr/bin/env bash
#SBATCH --job-name=nccl-diagnostics
#SBATCH --account=<account>
#SBATCH --partition=<gpu-partition>
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=nccl-diagnostics-%j.out

set -euo pipefail

record_dir="${NCCL_RECORD_DIR:-nccl-diagnostics-${SLURM_JOB_ID:-local}}"
mkdir -p "${record_dir}"
log_file="${record_dir}/nccl-diagnostics.log"

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "RUN_NCCL_TESTS=${RUN_NCCL_TESTS:-0}"

  echo
  echo "== scheduler layout =="
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
  echo "SLURM_JOB_NUM_NODES=${SLURM_JOB_NUM_NODES:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
  echo "SLURM_TASKS_PER_NODE=${SLURM_TASKS_PER_NODE:-}"
  echo "SLURM_GPUS_PER_NODE=${SLURM_GPUS_PER_NODE:-}"
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-}"

  echo
  echo "== selected environment =="
  env | sort | grep -E '^(SLURM|CUDA|NVIDIA|NCCL|UCX|OMPI|PMI|PMIX)_' || true

  echo
  echo "== gpu topology =="
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
    nvidia-smi topo -m || true
  else
    echo "nvidia-smi not found"
  fi

  export NCCL_DEBUG="${NCCL_DEBUG:-INFO}"
  export NCCL_DEBUG_SUBSYS="${NCCL_DEBUG_SUBSYS:-INIT,ENV,GRAPH,NET}"

  echo
  echo "== nccl debug settings =="
  echo "NCCL_DEBUG=${NCCL_DEBUG}"
  echo "NCCL_DEBUG_SUBSYS=${NCCL_DEBUG_SUBSYS}"
  echo "NCCL_SOCKET_IFNAME=${NCCL_SOCKET_IFNAME:-}"
  echo "NCCL_IB_DISABLE=${NCCL_IB_DISABLE:-}"

  echo
  echo "== optional nccl-tests =="
  if [ "${RUN_NCCL_TESTS:-0}" = "1" ]; then
    if command -v all_reduce_perf >/dev/null 2>&1; then
      srun all_reduce_perf \
        -b "${NCCL_TEST_MIN_BYTES:-8}" \
        -e "${NCCL_TEST_MAX_BYTES:-64M}" \
        -f "${NCCL_TEST_STEP_FACTOR:-2}" \
        -g "${NCCL_TEST_GPUS_PER_TASK:-1}"
    else
      echo "all_reduce_perf not found; install or load nccl-tests before enabling RUN_NCCL_TESTS"
      exit 2
    fi
  else
    echo "dry_run=true"
    echo "Set RUN_NCCL_TESTS=1 only after confirming nccl-tests is available."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
