#!/usr/bin/env bash
#SBATCH --job-name=checkpoint-demo
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:10:00
#SBATCH --signal=B:TERM@60
#SBATCH --output=checkpoint-%j.out

set -euo pipefail

checkpoint_dir="${CHECKPOINT_DIR:-checkpoints/demo}"
target_steps="${TARGET_STEPS:-5}"

on_signal() {
  echo "received termination signal at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "checkpoint_dir=${checkpoint_dir}"
}

trap on_signal TERM

mkdir -p "${checkpoint_dir}"

echo "job_id=${SLURM_JOB_ID:-local}"
echo "checkpoint_dir=${checkpoint_dir}"
echo "target_steps=${target_steps}"

bash examples/resume-progress.sh "${checkpoint_dir}" "${target_steps}"
