#!/usr/bin/env bash
#SBATCH --job-name=accelerate-smoke
#SBATCH --account=<account>
#SBATCH --partition=<gpu-partition>
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=00:10:00
#SBATCH --output=accelerate-smoke-%j.out

set -euo pipefail

record_dir="${ACCELERATE_RECORD_DIR:-accelerate-record-${SLURM_JOB_ID:-local}}"
smoke_script="${ACCELERATE_SMOKE_SCRIPT:-examples/accelerate_smoke.py}"
processes_per_node="${ACCELERATE_PROCESSES_PER_NODE:-1}"
mixed_precision="${ACCELERATE_MIXED_PRECISION:-no}"
mkdir -p "${record_dir}"
log_file="${record_dir}/accelerate-slurm.log"

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "smoke_script=${smoke_script}"
  echo "RUN_ACCELERATE_SMOKE=${RUN_ACCELERATE_SMOKE:-0}"

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
  # Load or activate the same environment used by the real training job.
  # Examples:
  # module load python cuda
  # source ~/venvs/accelerate/bin/activate
  # conda activate accelerate
  env | sort | grep -E '^(SLURM|CUDA|NVIDIA|NCCL|TORCH|ACCELERATE|PYTHON)_' || true

  echo
  echo "== gpu visibility =="
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
  else
    echo "nvidia-smi not found"
  fi

  echo
  echo "== package probe =="
  python3 - <<'PY' || true
try:
    import accelerate
    print("accelerate:", accelerate.__version__)
except Exception as exc:
    print("accelerate_probe_error:", exc)

try:
    import torch
    print("torch:", torch.__version__)
    print("cuda_available:", torch.cuda.is_available())
    print("cuda_device_count:", torch.cuda.device_count())
except Exception as exc:
    print("torch_probe_error:", exc)
PY

  echo
  echo "== launch plan =="
  if [ -n "${SLURM_JOB_NODELIST:-}" ] && command -v scontrol >/dev/null 2>&1; then
    export MASTER_ADDR="$(scontrol show hostnames "${SLURM_JOB_NODELIST}" | head -n 1)"
  else
    export MASTER_ADDR="${MASTER_ADDR:-127.0.0.1}"
  fi
  export MASTER_PORT="${MASTER_PORT:-29502}"
  export ACCELERATE_NUM_MACHINES="${SLURM_JOB_NUM_NODES:-1}"
  export ACCELERATE_PROCESSES_PER_NODE="${processes_per_node}"
  export ACCELERATE_NUM_PROCESSES="$((ACCELERATE_NUM_MACHINES * ACCELERATE_PROCESSES_PER_NODE))"
  export ACCELERATE_MIXED_PRECISION="${mixed_precision}"
  export ACCELERATE_MAIN_PROCESS_IP="${MASTER_ADDR}"
  export ACCELERATE_MAIN_PROCESS_PORT="${MASTER_PORT}"
  export ACCELERATE_SMOKE_SCRIPT="${smoke_script}"

  echo "ACCELERATE_NUM_MACHINES=${ACCELERATE_NUM_MACHINES}"
  echo "ACCELERATE_PROCESSES_PER_NODE=${ACCELERATE_PROCESSES_PER_NODE}"
  echo "ACCELERATE_NUM_PROCESSES=${ACCELERATE_NUM_PROCESSES}"
  echo "ACCELERATE_MIXED_PRECISION=${ACCELERATE_MIXED_PRECISION}"
  echo "ACCELERATE_MAIN_PROCESS_IP=${ACCELERATE_MAIN_PROCESS_IP}"
  echo "ACCELERATE_MAIN_PROCESS_PORT=${ACCELERATE_MAIN_PROCESS_PORT}"
  echo "srun --ntasks=${ACCELERATE_NUM_MACHINES} --ntasks-per-node=1 bash -lc 'accelerate launch ... ${smoke_script}'"

  if [ "${RUN_ACCELERATE_SMOKE:-0}" = "1" ]; then
    if ! command -v accelerate >/dev/null 2>&1; then
      echo "accelerate command not found; load or activate the Accelerate environment first"
      exit 2
    fi
    srun --ntasks="${ACCELERATE_NUM_MACHINES}" --ntasks-per-node=1 bash -lc '
      set -euo pipefail
      machine_rank="${SLURM_PROCID:-0}"
      launch_args=(
        --num_machines "${ACCELERATE_NUM_MACHINES}"
        --num_processes "${ACCELERATE_NUM_PROCESSES}"
        --machine_rank "${machine_rank}"
        --main_process_ip "${ACCELERATE_MAIN_PROCESS_IP}"
        --main_process_port "${ACCELERATE_MAIN_PROCESS_PORT}"
        --mixed_precision "${ACCELERATE_MIXED_PRECISION}"
      )
      if [ "${ACCELERATE_NUM_PROCESSES}" -gt 1 ]; then
        launch_args=(--multi_gpu "${launch_args[@]}")
      fi
      echo "node=$(hostname) machine_rank=${machine_rank} accelerate launch ${launch_args[*]} ${ACCELERATE_SMOKE_SCRIPT}"
      accelerate launch "${launch_args[@]}" "${ACCELERATE_SMOKE_SCRIPT}"
    '
  else
    echo "dry_run=true"
    echo "Set RUN_ACCELERATE_SMOKE=1 only after reviewing the launch plan."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
