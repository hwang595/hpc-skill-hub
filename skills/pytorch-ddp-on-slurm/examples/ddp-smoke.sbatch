#!/usr/bin/env bash
#SBATCH --job-name=pytorch-ddp-smoke
#SBATCH --account=<account>
#SBATCH --partition=<gpu-partition>
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=pytorch-ddp-smoke-%j.out

set -euo pipefail

echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "host=$(hostname)"
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
echo "SLURM_JOB_NUM_NODES=${SLURM_JOB_NUM_NODES:-}"
echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
echo "SLURM_GPUS_PER_NODE=${SLURM_GPUS_PER_NODE:-}"

# Load or activate the same environment used by the real training job.
# Examples:
# module load python cuda
# source ~/venvs/pytorch/bin/activate
# conda activate torch

if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
fi

export MASTER_ADDR="$(scontrol show hostnames "${SLURM_JOB_NODELIST}" | head -n 1)"
export MASTER_PORT="${MASTER_PORT:-29500}"
export WORLD_SIZE="${SLURM_NTASKS}"

srun python3 examples/ddp_smoke.py

echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
