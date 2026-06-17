#!/usr/bin/env bash
#SBATCH --job-name=gpu-smoke
#SBATCH --account=<account>
#SBATCH --partition=<gpu-partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%j.out

set -euo pipefail

module purge
# Replace <cuda-or-rocm-module> with a site-approved GPU runtime module before running.
module load "<cuda-or-rocm-module>"

echo "job=${SLURM_JOB_ID}"
echo "host=$(hostname)"
nvidia-smi || rocm-smi || true

# Replace with the real GPU workload.
srun bash -lc 'python3 - <<PY
print("hello from gpu allocation")
PY'
