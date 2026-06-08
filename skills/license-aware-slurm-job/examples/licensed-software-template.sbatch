#!/usr/bin/env bash
#SBATCH --job-name=licensed-software
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=licensed-software-%j.out
##SBATCH --account=<account>
##SBATCH --partition=<partition>
##SBATCH --licenses=<license-resource>:1

set -euo pipefail

export RUN_LICENSED_APP="${RUN_LICENSED_APP:-0}"
export APP_MODULE="${APP_MODULE:-}"
export APP_COMMAND="${APP_COMMAND:-hostname}"
export OUTPUT_DIR="${OUTPUT_DIR:-license-aware-slurm-run}"

mkdir -p "${OUTPUT_DIR}"

echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "job=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "RUN_LICENSED_APP=${RUN_LICENSED_APP}"
echo "APP_MODULE=${APP_MODULE}"
echo "APP_COMMAND=${APP_COMMAND}"
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-unset}"
echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-unset}"
echo "SLURM_JOB_LICENSES=${SLURM_JOB_LICENSES:-unset}"
echo "SLURM_SUBMIT_DIR=${SLURM_SUBMIT_DIR:-unset}"

if command -v scontrol >/dev/null 2>&1; then
  echo "== scontrol show job =="
  if [ -n "${SLURM_JOB_ID:-}" ]; then
    scontrol show job "${SLURM_JOB_ID}" || true
  else
    echo "SLURM_JOB_ID is unset."
  fi
  echo "== scontrol show lic =="
  scontrol show lic || true
fi

if [ -n "${APP_MODULE}" ]; then
  if type module >/dev/null 2>&1; then
    module purge
    module load "${APP_MODULE}"
  else
    echo "APP_MODULE is set, but the module command is unavailable." >&2
    exit 2
  fi
fi

if [ "${RUN_LICENSED_APP}" != "1" ]; then
  echo "RUN_LICENSED_APP=0, exiting before the licensed application command."
  exit 0
fi

bash -lc "${APP_COMMAND}"
