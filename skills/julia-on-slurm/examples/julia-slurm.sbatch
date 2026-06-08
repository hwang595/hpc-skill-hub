#!/usr/bin/env bash
#SBATCH --job-name=julia-demo
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

# Replace this with the Julia module name used by your site, or remove it if
# julia is already on PATH.
module load julia 2>/dev/null || true

export JULIA_SCRIPT="${JULIA_SCRIPT:-examples/analysis.jl}"
export JULIA_PROJECT_DIR="${JULIA_PROJECT_DIR:-examples}"
export OUTPUT_DIR="${OUTPUT_DIR:-results}"
export JULIA_NUM_THREADS="${JULIA_NUM_THREADS:-${SLURM_CPUS_PER_TASK:-1}}"
export JULIA_DEPOT_PATH="${JULIA_DEPOT_PATH:-${PWD}/julia-depot:}"

primary_depot="${JULIA_DEPOT_PATH%%:*}"

mkdir -p logs "${OUTPUT_DIR}"
if [ -n "${primary_depot}" ]; then
  mkdir -p "${primary_depot}"
fi

echo "job=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "start=$(date -Iseconds)"
echo "JULIA_SCRIPT=${JULIA_SCRIPT}"
echo "JULIA_PROJECT_DIR=${JULIA_PROJECT_DIR}"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
echo "JULIA_NUM_THREADS=${JULIA_NUM_THREADS}"
echo "JULIA_DEPOT_PATH=${JULIA_DEPOT_PATH}"

julia --version
julia --project="${JULIA_PROJECT_DIR}" --threads="${JULIA_NUM_THREADS}" "${JULIA_SCRIPT}" "${OUTPUT_DIR}"

echo "end=$(date -Iseconds)"
