#!/usr/bin/env bash
#SBATCH --job-name=array-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:05:00
#SBATCH --array=1-5
#SBATCH --output=slurm-%A_%a.out

set -euo pipefail

echo "array_job=${SLURM_ARRAY_JOB_ID}"
echo "task=${SLURM_ARRAY_TASK_ID}"
echo "host=$(hostname)"

# Replace this with per-task work, for example selecting line N from a manifest.
sleep 5
