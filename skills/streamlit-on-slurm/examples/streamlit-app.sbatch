#!/usr/bin/env bash
#SBATCH --job-name=streamlit-app
#SBATCH --account=<account>
#SBATCH --partition=<debug-partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=streamlit-app-%j.out

set -euo pipefail

app_path="${STREAMLIT_APP:-examples/streamlit_app.py}"
project_dir="${STREAMLIT_PROJECT_DIR:-${SLURM_SUBMIT_DIR:-$PWD}}"
port="${STREAMLIT_PORT:-8501}"
address="${STREAMLIT_ADDRESS:-127.0.0.1}"

echo "job_id=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "project_dir=${project_dir}"
echo "app_path=${app_path}"
echo "address=${address}"
echo "port=${port}"
echo "RUN_STREAMLIT_APP=${RUN_STREAMLIT_APP:-0}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is not available in PATH." >&2
  exit 1
fi

if ! command -v streamlit >/dev/null 2>&1; then
  echo "ERROR: streamlit is not available in PATH. Activate the site-approved Python environment first." >&2
  exit 1
fi

python3 --version
streamlit version || true

cd "${project_dir}"
if [ ! -f "${app_path}" ]; then
  echo "ERROR: Streamlit app does not exist: ${project_dir}/${app_path}" >&2
  exit 1
fi

if [ "${RUN_STREAMLIT_APP:-0}" != "1" ]; then
  echo "Plan-only mode. Review site policy and set RUN_STREAMLIT_APP=1 to launch."
  echo "Planned command:"
  echo "streamlit run '${app_path}' --server.address='${address}' --server.port='${port}' --server.headless=true"
  exit 0
fi

exec streamlit run "${app_path}" \
  --server.address="${address}" \
  --server.port="${port}" \
  --server.headless=true
