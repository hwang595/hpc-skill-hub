#!/usr/bin/env bash
#SBATCH --job-name=tensorflow-smoke
#SBATCH --account=<account>
#SBATCH --partition=<gpu-partition>
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=00:10:00
#SBATCH --output=tensorflow-smoke-%j.out

set -euo pipefail

record_dir="${TF_RECORD_DIR:-tensorflow-record-${SLURM_JOB_ID:-local}}"
smoke_script="${TF_SMOKE_SCRIPT:-examples/tensorflow_smoke.py}"
worker_port="${TF_WORKER_PORT:-12345}"
mkdir -p "${record_dir}"
log_file="${record_dir}/tensorflow-slurm.log"

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "smoke_script=${smoke_script}"
  echo "RUN_TENSORFLOW_SMOKE=${RUN_TENSORFLOW_SMOKE:-0}"

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
  # source ~/venvs/tensorflow/bin/activate
  # conda activate tensorflow
  env |
    sort |
    grep -E '^(SLURM|CUDA|NVIDIA|NCCL|TF|PYTHON)_' |
    grep -Ev '(TOKEN|SECRET|PASSWORD|PASS|KEY|CREDENTIAL|AUTH)' || true

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
    import tensorflow as tf
    print("tensorflow:", tf.__version__)
    print("physical_gpus:", len(tf.config.list_physical_devices("GPU")))
except Exception as exc:
    print("tensorflow_probe_error:", exc)
PY

  echo
  echo "== launch plan =="
  export TF_WORKER_PORT="${worker_port}"
  if [ -n "${SLURM_JOB_NODELIST:-}" ] && command -v scontrol >/dev/null 2>&1; then
    export TF_WORKERS="$(
      scontrol show hostnames "${SLURM_JOB_NODELIST}" |
        python3 -c 'import os, sys; port = os.environ.get("TF_WORKER_PORT", "12345"); print(",".join(f"{line.strip()}:{port}" for line in sys.stdin if line.strip()))'
    )"
  else
    export TF_WORKERS="${TF_WORKERS:-127.0.0.1:${worker_port}}"
  fi
  export TF_NUM_WORKERS="${SLURM_JOB_NUM_NODES:-1}"
  export TF_SMOKE_SCRIPT="${smoke_script}"

  echo "TF_WORKER_PORT=${TF_WORKER_PORT}"
  echo "TF_WORKERS=${TF_WORKERS}"
  echo "TF_NUM_WORKERS=${TF_NUM_WORKERS}"
  echo "srun --ntasks=${TF_NUM_WORKERS} --ntasks-per-node=1 bash -lc 'TF_TASK_INDEX=\${SLURM_PROCID:-0} python3 ${smoke_script}'"

  if [ "${RUN_TENSORFLOW_SMOKE:-0}" = "1" ]; then
    srun --ntasks="${TF_NUM_WORKERS}" --ntasks-per-node=1 bash -lc '
      set -euo pipefail
      export TF_TASK_INDEX="${SLURM_PROCID:-0}"
      echo "node=$(hostname) TF_TASK_INDEX=${TF_TASK_INDEX} TF_WORKERS=${TF_WORKERS}"
      python3 "${TF_SMOKE_SCRIPT}"
    '
  else
    echo "dry_run=true"
    echo "Set RUN_TENSORFLOW_SMOKE=1 only after reviewing the launch plan."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
