#!/usr/bin/env bash
#SBATCH --job-name=cpu-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%j.out

set -euo pipefail

echo "job=${SLURM_JOB_ID}"
echo "host=$(hostname)"
echo "start=$(date -Iseconds)"

# Replace this with the real workload.
srun bash -lc 'python3 - <<PY
import os
print("hello from cpu job")
print("cpus:", os.environ.get("SLURM_CPUS_PER_TASK"))
PY'

echo "end=$(date -Iseconds)"
