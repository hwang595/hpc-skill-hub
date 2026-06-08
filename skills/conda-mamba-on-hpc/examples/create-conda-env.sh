#!/usr/bin/env bash
set -euo pipefail

env_prefix="${1:-conda-env-hpc}"
environment_file="${2:-examples/environment.yml}"
record_dir="${RECORD_DIR:-conda-record}"

mkdir -p "${record_dir}"

if command -v micromamba >/dev/null 2>&1; then
  tool="micromamba"
elif command -v mamba >/dev/null 2>&1; then
  tool="mamba"
elif command -v conda >/dev/null 2>&1; then
  tool="conda"
else
  echo "No conda, mamba, or micromamba command found."
  exit 2
fi

echo "tool=${tool}"
echo "env_prefix=${env_prefix}"
echo "environment_file=${environment_file}"
echo "CONDA_PKGS_DIRS=${CONDA_PKGS_DIRS:-unset}"

case "${tool}" in
  micromamba)
    micromamba create -y -p "${env_prefix}" -f "${environment_file}"
    micromamba list -p "${env_prefix}" > "${record_dir}/conda-list.txt"
    micromamba env export -p "${env_prefix}" > "${record_dir}/environment-export.yml"
    ;;
  mamba)
    mamba env create -y -p "${env_prefix}" -f "${environment_file}"
    conda list -p "${env_prefix}" > "${record_dir}/conda-list.txt"
    conda env export -p "${env_prefix}" > "${record_dir}/environment-export.yml"
    ;;
  conda)
    conda env create -y -p "${env_prefix}" -f "${environment_file}"
    conda list -p "${env_prefix}" > "${record_dir}/conda-list.txt"
    conda env export -p "${env_prefix}" > "${record_dir}/environment-export.yml"
    ;;
esac

{
  echo "tool=${tool}"
  echo "env_prefix=${env_prefix}"
  echo "environment_file=${environment_file}"
  echo "CONDA_PKGS_DIRS=${CONDA_PKGS_DIRS:-unset}"
  echo
  echo "== relevant environment =="
  env | sort | grep -E "^(CONDA|MAMBA|PYTHON|PATH)=" || true
} > "${record_dir}/conda-env-record.txt"

echo "record_dir=${record_dir}"
echo "activate by prefix with your site's supported conda or mamba command."
