#!/usr/bin/env bash
#SBATCH --job-name=vscode-tunnel
#SBATCH --account=<account>
#SBATCH --partition=<debug-partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=vscode-tunnel-%j.out

set -euo pipefail

project_dir="${VSCODE_PROJECT_DIR:-${SLURM_SUBMIT_DIR:-$PWD}}"
tunnel_name="${VSCODE_TUNNEL_NAME:-hpc-skill-${SLURM_JOB_ID:-local}}"
code_cli="${VSCODE_CODE_CLI:-code}"

echo "job_id=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "project_dir=${project_dir}"
echo "tunnel_name=${tunnel_name}"
echo "RUN_VSCODE_TUNNEL=${RUN_VSCODE_TUNNEL:-0}"

if ! command -v "${code_cli}" >/dev/null 2>&1; then
  echo "ERROR: VS Code CLI '${code_cli}' is not available in PATH." >&2
  echo "Load the site-approved module or install the standalone CLI according to site policy." >&2
  exit 1
fi

"${code_cli}" tunnel --help >/dev/null

if [ "${RUN_VSCODE_TUNNEL:-0}" != "1" ]; then
  echo "Plan-only mode. Review site policy, then resubmit with RUN_VSCODE_TUNNEL=1."
  echo "Planned command:"
  echo "cd '${project_dir}'"
  echo "${code_cli} tunnel --accept-server-license-terms --name '${tunnel_name}'"
  exit 0
fi

cd "${project_dir}"
exec "${code_cli}" tunnel \
  --accept-server-license-terms \
  --name "${tunnel_name}"
