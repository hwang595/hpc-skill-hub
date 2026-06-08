#!/usr/bin/env bash
#SBATCH --job-name=rscript-demo
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

# Replace this with the R module name used by your site, or remove it if R is
# already on PATH.
module load R 2>/dev/null || true

export R_SCRIPT="${R_SCRIPT:-examples/analysis.R}"
export OUTPUT_DIR="${OUTPUT_DIR:-results}"
export R_LIBS_USER="${R_LIBS_USER:-${PWD}/r-library}"

primary_r_lib="${R_LIBS_USER%%:*}"

mkdir -p logs "${OUTPUT_DIR}" "${primary_r_lib}"

echo "job=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "start=$(date -Iseconds)"
echo "R_SCRIPT=${R_SCRIPT}"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
echo "R_LIBS_USER=${R_LIBS_USER}"

Rscript --version
Rscript --vanilla "${R_SCRIPT}" "${OUTPUT_DIR}"

echo "end=$(date -Iseconds)"
