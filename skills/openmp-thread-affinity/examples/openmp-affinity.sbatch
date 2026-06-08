#!/usr/bin/env bash
#SBATCH --job-name=openmp-affinity
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=4G
#SBATCH --time=00:05:00
#SBATCH --output=openmp-affinity-%j.out

set -euo pipefail

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export OMP_PLACES="${OMP_PLACES:-cores}"
export OMP_PROC_BIND="${OMP_PROC_BIND:-close}"

echo "host=$(hostname)"
echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

bash examples/inspect-thread-env.sh
