#!/usr/bin/env bash
#SBATCH --job-name=jax-smoke
#SBATCH --account=<account>
#SBATCH --partition=<gpu-partition>
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=jax-smoke-%j.out

set -euo pipefail

record_dir="${JAX_RECORD_DIR:-jax-record-${SLURM_JOB_ID:-local}}"
smoke_script="${JAX_SMOKE_SCRIPT:-examples/jax_smoke.py}"
mkdir -p "${record_dir}"
log_file="${record_dir}/jax-slurm.log"

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "smoke_script=${smoke_script}"
  echo "RUN_JAX_SMOKE=${RUN_JAX_SMOKE:-0}"

  echo
  echo "== scheduler layout =="
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
  echo "SLURM_JOB_NUM_NODES=${SLURM_JOB_NUM_NODES:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
  echo "SLURM_NTASKS_PER_NODE=${SLURM_NTASKS_PER_NODE:-}"
  echo "SLURM_GPUS_PER_NODE=${SLURM_GPUS_PER_NODE:-}"
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-}"
  echo "ROCR_VISIBLE_DEVICES=${ROCR_VISIBLE_DEVICES:-}"

  echo
  echo "== selected environment =="
  # Load or activate the same environment used by the real JAX workload.
  # Examples:
  # module load python cuda
  # source ~/venvs/jax/bin/activate
  # conda activate jax
  env | sort | grep -E '^(SLURM|CUDA|ROCR|HIP|NVIDIA|JAX|XLA|TPU|PYTHON)_' || true

  echo
  echo "== accelerator visibility =="
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
  else
    echo "nvidia-smi not found"
  fi

  echo
  echo "== python packages =="
  python3 - <<'PY' || true
try:
    import jax
    print("jax:", jax.__version__)
    print("default_backend:", jax.default_backend())
    print("local_device_count:", jax.local_device_count())
except Exception as exc:
    print("jax_probe_error:", exc)
PY

  echo
  echo "== launch plan =="
  if [ -n "${SLURM_JOB_NODELIST:-}" ] && command -v scontrol >/dev/null 2>&1; then
    export MASTER_ADDR="$(scontrol show hostnames "${SLURM_JOB_NODELIST}" | head -n 1)"
  else
    export MASTER_ADDR="${MASTER_ADDR:-127.0.0.1}"
  fi
  export MASTER_PORT="${MASTER_PORT:-29501}"
  export JAX_COORDINATOR_ADDRESS="${JAX_COORDINATOR_ADDRESS:-${MASTER_ADDR}:${MASTER_PORT}}"
  export JAX_NUM_PROCESSES="${SLURM_NTASKS:-1}"
  export XLA_PYTHON_CLIENT_PREALLOCATE="${XLA_PYTHON_CLIENT_PREALLOCATE:-false}"
  echo "JAX_COORDINATOR_ADDRESS=${JAX_COORDINATOR_ADDRESS}"
  echo "JAX_NUM_PROCESSES=${JAX_NUM_PROCESSES}"
  echo "XLA_PYTHON_CLIENT_PREALLOCATE=${XLA_PYTHON_CLIENT_PREALLOCATE}"
  echo "srun python3 ${smoke_script}"

  if [ "${RUN_JAX_SMOKE:-0}" = "1" ]; then
    srun python3 "${smoke_script}"
  else
    echo "dry_run=true"
    echo "Set RUN_JAX_SMOKE=1 only after reviewing the launch plan."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
