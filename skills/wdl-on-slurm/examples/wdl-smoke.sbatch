#!/usr/bin/env bash
#SBATCH --job-name=wdl-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=wdl-smoke-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

record_dir="${WDL_RECORD_DIR:-wdl-record-${SLURM_JOB_ID:-local}}"
wdl_document="${WDL_DOCUMENT:-${script_dir}/wordcount.wdl}"
sample_file="${WDL_SAMPLE_FILE:-${script_dir}/sample.txt}"
input_json="${WDL_INPUT_JSON:-${record_dir}/inputs.json}"
run_dir="${WDL_RUN_DIR:-${record_dir}/runs}"
output_json="${WDL_OUTPUT_JSON:-${record_dir}/outputs.json}"
miniwdl_exe="${MINIWDL_EXE:-miniwdl}"
runtime_defaults="${WDL_RUNTIME_DEFAULTS:-}"
log_file="${record_dir}/wdl-smoke.log"

mkdir -p "${record_dir}" "${run_dir}"

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "RUN_WDL=${RUN_WDL:-0}"
  echo
  echo "== scheduler layout =="
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-1}"
  echo
  echo "== wdl paths =="
  echo "wdl_document=${wdl_document}"
  echo "sample_file=${sample_file}"
  echo "input_json=${input_json}"
  echo "run_dir=${run_dir}"
  echo "output_json=${output_json}"

  if [ ! -s "${wdl_document}" ]; then
    echo "ERROR: WDL document is missing or empty: ${wdl_document}" >&2
    exit 1
  fi

  if [ -z "${WDL_INPUT_JSON:-}" ]; then
    if [ ! -s "${sample_file}" ]; then
      echo "ERROR: sample file is missing or empty: ${sample_file}" >&2
      exit 1
    fi
    cat > "${input_json}" <<JSON
{
  "wordcount.input_file": "${sample_file}"
}
JSON
  fi

  if [ ! -s "${input_json}" ]; then
    echo "ERROR: WDL input JSON is missing or empty: ${input_json}" >&2
    exit 1
  fi

  echo
  echo "== selected environment =="
  if command -v "${miniwdl_exe}" >/dev/null 2>&1; then
    echo "${miniwdl_exe}=$(command -v "${miniwdl_exe}")"
    "${miniwdl_exe}" --version || true
  else
    echo "${miniwdl_exe}=not_found"
  fi

  wdl_command=(
    "${miniwdl_exe}"
    run
    -i "${input_json}"
    -d "${run_dir}"
    -o "${output_json}"
    --no-color
  )

  if [ -n "${runtime_defaults}" ]; then
    wdl_command+=(--runtime-defaults "${runtime_defaults}")
  fi

  if [ "${WDL_COPY_INPUTS:-0}" = "1" ]; then
    wdl_command+=(--copy-input-files)
  fi

  wdl_command+=("${wdl_document}")

  echo
  echo "== launch command =="
  printf 'command='
  printf '%q ' "${wdl_command[@]}"
  printf '\n'

  if [ -n "${WDL_EXTRA_ARGS:-}" ]; then
    echo "WDL_EXTRA_ARGS=${WDL_EXTRA_ARGS}"
    echo "extra_args_note=review site-approved miniwdl options before adding them to the wrapper"
  fi

  if [ "${RUN_WDL:-0}" = "1" ]; then
    command -v "${miniwdl_exe}" >/dev/null 2>&1
    "${wdl_command[@]}"
    echo "wdl_output_json=${output_json}"
  else
    echo "dry_run=true"
    echo "Set RUN_WDL=1 only after reviewing paths, environment, and filesystem impact."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
