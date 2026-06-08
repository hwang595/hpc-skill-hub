#!/usr/bin/env bash
#SBATCH --job-name=rstudio-session
#SBATCH --account=<account>
#SBATCH --partition=<debug-partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=02:00:00
#SBATCH --output=rstudio-session-%j.out

set -euo pipefail

project_dir="${RSTUDIO_PROJECT_DIR:-${SLURM_SUBMIT_DIR:-$PWD}}"
port="${RSTUDIO_PORT:-8787}"
launch_cmd="${RSTUDIO_LAUNCH_CMD:-}"

echo "job_id=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "project_dir=${project_dir}"
echo "port=${port}"
echo "RUN_RSTUDIO_SESSION=${RUN_RSTUDIO_SESSION:-0}"

if ! command -v R >/dev/null 2>&1; then
  echo "ERROR: R is not available in PATH. Load the site-approved R module first." >&2
  exit 1
fi

R --version | sed -n '1,2p'
Rscript -e 'cat("R_LIBS_USER=", Sys.getenv("R_LIBS_USER"), "\n", sep = "")' || true

if [ ! -d "${project_dir}" ]; then
  echo "ERROR: project directory does not exist: ${project_dir}" >&2
  exit 1
fi

if [ "${RUN_RSTUDIO_SESSION:-0}" != "1" ]; then
  echo "Plan-only mode. Review site policy and set RUN_RSTUDIO_SESSION=1 to launch."
  echo "Set RSTUDIO_LAUNCH_CMD to the site-approved Workbench, OnDemand, or RStudio wrapper command."
  echo "Example wrapper variables available to the command:"
  echo "  RSTUDIO_PROJECT_DIR=${project_dir}"
  echo "  RSTUDIO_PORT=${port}"
  exit 0
fi

if [ -z "${launch_cmd}" ]; then
  echo "ERROR: RUN_RSTUDIO_SESSION=1 requires RSTUDIO_LAUNCH_CMD." >&2
  exit 1
fi

export RSTUDIO_PROJECT_DIR="${project_dir}"
export RSTUDIO_PORT="${port}"
cd "${project_dir}"
exec bash -lc "${launch_cmd}"
