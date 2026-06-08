#!/usr/bin/env bash
#SBATCH --job-name=gpu-binding-diag
#SBATCH --account=<account>
#SBATCH --partition=<gpu-partition>
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=2
#SBATCH --gpus-per-node=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=gpu-binding-diag-%j.out

set -euo pipefail

export RUN_GPU_BINDING_PROBE="${RUN_GPU_BINDING_PROBE:-0}"
export GPU_TASKS="${GPU_TASKS:-${SLURM_NTASKS:-2}}"
export GPUS_PER_TASK="${GPUS_PER_TASK:-1}"
export GPU_BIND="${GPU_BIND:-verbose,closest}"
export OUTPUT_DIR="${OUTPUT_DIR:-gpu-binding-${SLURM_JOB_ID:-manual}}"
export APP_MODULE="${APP_MODULE:-}"

mkdir -p "${OUTPUT_DIR}"

if [ -n "${APP_MODULE}" ]; then
  if type module >/dev/null 2>&1; then
    module purge
    module load "${APP_MODULE}"
  else
    echo "APP_MODULE is set, but the module command is unavailable." >&2
    exit 2
  fi
fi

probe_script="examples/print-gpu-binding.sh"
topology_report="${OUTPUT_DIR}/gpu-topology.txt"
binding_report="${OUTPUT_DIR}/gpu-binding.tsv"

{
  echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_GPU_BINDING_PROBE=${RUN_GPU_BINDING_PROBE}"
  echo "GPU_TASKS=${GPU_TASKS}"
  echo "GPUS_PER_TASK=${GPUS_PER_TASK}"
  echo "GPU_BIND=${GPU_BIND}"
  echo "APP_MODULE=${APP_MODULE}"
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-unset}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-unset}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-unset}"
  echo "SLURM_NTASKS_PER_NODE=${SLURM_NTASKS_PER_NODE:-unset}"
  echo "SLURM_GPUS=${SLURM_GPUS:-unset}"
  echo "SLURM_GPUS_ON_NODE=${SLURM_GPUS_ON_NODE:-unset}"
  echo "SLURM_GPUS_PER_TASK=${SLURM_GPUS_PER_TASK:-unset}"
  echo "SLURM_JOB_GPUS=${SLURM_JOB_GPUS:-unset}"
  echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
  echo "ROCR_VISIBLE_DEVICES=${ROCR_VISIBLE_DEVICES:-unset}"
  echo "HIP_VISIBLE_DEVICES=${HIP_VISIBLE_DEVICES:-unset}"
  echo
  echo "== command paths =="
  command -v srun || true
  command -v nvidia-smi || true
  command -v rocm-smi || true
  echo
  echo "== nvidia-smi list =="
  nvidia-smi -L 2>/dev/null || true
  echo
  echo "== nvidia-smi topology =="
  nvidia-smi topo -m 2>/dev/null || true
  echo
  echo "== rocm-smi =="
  rocm-smi --showid --showproductname 2>/dev/null || true
} > "${topology_report}"

launch_command=(srun --ntasks "${GPU_TASKS}" --gpus-per-task "${GPUS_PER_TASK}")
if [ -n "${GPU_BIND}" ]; then
  launch_command+=(--gpu-bind="${GPU_BIND}")
fi
launch_command+=(bash "${probe_script}")

echo "Wrote GPU topology report: ${topology_report}"
printf 'launch_command='
printf '%q ' "${launch_command[@]}"
printf '\n'

if [ "${RUN_GPU_BINDING_PROBE}" != "1" ]; then
  echo "RUN_GPU_BINDING_PROBE=0, dry-run complete. Set RUN_GPU_BINDING_PROBE=1 to launch the probe."
  exit 0
fi

"${launch_command[@]}" | tee "${binding_report}"
echo "Wrote GPU binding report: ${binding_report}"
