#!/usr/bin/env bash
#SBATCH --job-name=matlab-demo
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=logs/%x-%j.out
##SBATCH --licenses=<matlab-license>:1

set -euo pipefail

# Replace this with the MATLAB module name used by your site, or remove it if
# matlab is already on PATH.
module load matlab 2>/dev/null || true

export MATLAB_ENTRYPOINT="${MATLAB_ENTRYPOINT:-analysis}"
export MATLAB_WORKDIR="${MATLAB_WORKDIR:-examples}"
export OUTPUT_DIR="${OUTPUT_DIR:-results}"
export MATLAB_LOG="${MATLAB_LOG:-logs/matlab-${SLURM_JOB_ID:-local}.log}"

mkdir -p logs "${OUTPUT_DIR}"

echo "job=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "start=$(date -Iseconds)"
echo "MATLAB_ENTRYPOINT=${MATLAB_ENTRYPOINT}"
echo "MATLAB_WORKDIR=${MATLAB_WORKDIR}"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
echo "MATLAB_LOG=${MATLAB_LOG}"
echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-unset}"

matlab -logfile "${MATLAB_LOG}" -batch "addpath(getenv('MATLAB_WORKDIR')); feval(getenv('MATLAB_ENTRYPOINT'))"

echo "end=$(date -Iseconds)"
