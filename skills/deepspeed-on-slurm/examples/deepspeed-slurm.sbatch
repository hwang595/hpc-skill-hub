#!/usr/bin/env bash
#SBATCH --job-name=deepspeed-smoke
#SBATCH --account=<account>
#SBATCH --partition=<gpu-partition>
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=00:10:00
#SBATCH --output=deepspeed-smoke-%j.out

set -euo pipefail

record_dir="${DEEPSPEED_RECORD_DIR:-deepspeed-record-${SLURM_JOB_ID:-local}}"
config_path="${DEEPSPEED_CONFIG:-examples/ds_config_zero2.json}"
smoke_script="${DEEPSPEED_SMOKE_SCRIPT:-examples/deepspeed_smoke.py}"
mkdir -p "${record_dir}"
log_file="${record_dir}/deepspeed-slurm.log"

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "config_path=${config_path}"
  echo "RUN_DEEPSPEED_SMOKE=${RUN_DEEPSPEED_SMOKE:-0}"

  echo
  echo "== scheduler layout =="
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
  echo "SLURM_JOB_NUM_NODES=${SLURM_JOB_NUM_NODES:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
  echo "SLURM_NTASKS_PER_NODE=${SLURM_NTASKS_PER_NODE:-}"
  echo "SLURM_GPUS_PER_NODE=${SLURM_GPUS_PER_NODE:-}"
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-}"

  echo
  echo "== selected environment =="
  env | sort | grep -E '^(SLURM|CUDA|NVIDIA|NCCL|UCX|PMI|PMIX|DEEPSPEED|PYTHON)_' || true

  echo
  echo "== gpu visibility =="
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
  else
    echo "nvidia-smi not found"
  fi

  echo
  echo "== python packages =="
  python3 - <<'PY' || true
try:
    import torch
    print("torch:", torch.__version__)
    print("cuda_available:", torch.cuda.is_available())
    print("cuda_device_count:", torch.cuda.device_count())
except Exception as exc:
    print("torch_probe_error:", exc)

try:
    import deepspeed
    print("deepspeed:", deepspeed.__version__)
except Exception as exc:
    print("deepspeed_probe_error:", exc)
PY

  echo
  echo "== storage checklist =="
  echo "checkpoint_dir=<durable project path, not node-local scratch>"
  echo "log_dir=${record_dir}"
  echo "dataset_dir=<staged dataset path>"
  echo "resume_policy=<explicit checkpoint restore policy>"

  echo
  echo "== launch plan =="
  if [ -n "${SLURM_JOB_NODELIST:-}" ] && command -v scontrol >/dev/null 2>&1; then
    export MASTER_ADDR="$(scontrol show hostnames "${SLURM_JOB_NODELIST}" | head -n 1)"
  else
    export MASTER_ADDR="${MASTER_ADDR:-127.0.0.1}"
  fi
  export MASTER_PORT="${MASTER_PORT:-29500}"
  export WORLD_SIZE="${SLURM_NTASKS:-1}"
  echo "MASTER_ADDR=${MASTER_ADDR}"
  echo "MASTER_PORT=${MASTER_PORT}"
  echo "WORLD_SIZE=${WORLD_SIZE}"
  echo "srun python3 ${smoke_script} --deepspeed_config ${config_path}"

  if [ "${RUN_DEEPSPEED_SMOKE:-0}" = "1" ]; then
    if ! command -v deepspeed >/dev/null 2>&1; then
      echo "deepspeed command not found; load or activate the DeepSpeed environment first"
      exit 2
    fi
    srun python3 "${smoke_script}" --deepspeed_config "${config_path}"
  else
    echo "dry_run=true"
    echo "Set RUN_DEEPSPEED_SMOKE=1 only after reviewing the launch plan."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
