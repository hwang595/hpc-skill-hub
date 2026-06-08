#!/usr/bin/env bash
set -euo pipefail

venv_path="${1:-.venv-hpc}"
requirements_file="${2:-}"
record_dir="${RECORD_DIR:-venv-record}"

mkdir -p "${record_dir}"

echo "== python before environment =="
python3 -V
python3 -m pip --version

echo
echo "== creating virtual environment =="
python3 -m venv "${venv_path}"

# shellcheck disable=SC1091
. "${venv_path}/bin/activate"

if [ "${UPGRADE_PIP:-0}" = "1" ]; then
  python -m pip install --upgrade pip
else
  echo "Skipping pip upgrade; set UPGRADE_PIP=1 to opt in."
fi

if [ -n "${requirements_file}" ]; then
  echo
  echo "== installing requirements =="
  python -m pip install -r "${requirements_file}"
else
  echo "No requirements file provided; environment contains upgraded pip only."
fi

{
  echo "venv_path=${venv_path}"
  echo "python=$(python -V 2>&1)"
  echo "pip=$(python -m pip --version)"
  echo "VIRTUAL_ENV=${VIRTUAL_ENV:-}"
  echo
  echo "== environment variables =="
  env | sort | grep -E "^(MODULE|LMOD|PYTHON|PIP|VIRTUAL_ENV|PATH)=" || true
  echo
  echo "== pip freeze =="
  python -m pip freeze
} > "${record_dir}/python-venv-record.txt"

echo "record=${record_dir}/python-venv-record.txt"
echo "activate with: . ${venv_path}/bin/activate"
