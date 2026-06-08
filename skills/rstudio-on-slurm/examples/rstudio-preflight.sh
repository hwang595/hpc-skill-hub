#!/usr/bin/env bash
set -euo pipefail

project_dir="${1:-${RSTUDIO_PROJECT_DIR:-$PWD}}"

echo "== host =="
hostname
echo "pwd=$PWD"
echo "project_dir=${project_dir}"

echo "== slurm =="
command -v sbatch || true
command -v srun || true
command -v squeue || true
command -v scancel || true

echo "== r =="
command -v R || true
command -v Rscript || true
R --version | sed -n '1,2p' || true
Rscript -e 'print(.libPaths())' || true

echo "== rstudio or site wrapper =="
command -v rserver || true
command -v rstudio-server || true
command -v ondemand || true
if [ -n "${RSTUDIO_LAUNCH_CMD:-}" ]; then
  echo "RSTUDIO_LAUNCH_CMD is set for review."
else
  echo "RSTUDIO_LAUNCH_CMD is not set."
fi

echo "== project =="
if [ -d "${project_dir}" ]; then
  find "${project_dir}" -maxdepth 1 -mindepth 1 | sed -n '1,10p'
else
  echo "ERROR: project directory does not exist: ${project_dir}" >&2
  exit 1
fi

echo "== next =="
echo "Confirm site policy, then submit examples/rstudio-session.sbatch in plan-only mode."
