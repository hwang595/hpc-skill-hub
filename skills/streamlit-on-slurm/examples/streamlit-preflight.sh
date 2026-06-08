#!/usr/bin/env bash
set -euo pipefail

app_path="${1:-${STREAMLIT_APP:-examples/streamlit_app.py}}"
project_dir="${STREAMLIT_PROJECT_DIR:-$PWD}"

echo "== host =="
hostname
echo "pwd=$PWD"
echo "project_dir=${project_dir}"
echo "app_path=${app_path}"

echo "== slurm =="
command -v sbatch || true
command -v srun || true
command -v squeue || true
command -v scancel || true

echo "== python =="
command -v python3 || true
python3 --version || true

echo "== streamlit =="
command -v streamlit || true
streamlit version || true

echo "== app =="
if [ -f "${project_dir}/${app_path}" ]; then
  python3 -m py_compile "${project_dir}/${app_path}"
  sed -n '1,40p' "${project_dir}/${app_path}"
else
  echo "ERROR: Streamlit app does not exist: ${project_dir}/${app_path}" >&2
  exit 1
fi

echo "== next =="
echo "Confirm site policy, then submit examples/streamlit-app.sbatch in plan-only mode."
