#!/usr/bin/env bash
#SBATCH --job-name=cwl-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=cwl-smoke-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

record_dir="${CWL_RECORD_DIR:-cwl-record-${SLURM_JOB_ID:-local}}"
cwl_document="${CWL_DOCUMENT:-${script_dir}/wordcount.cwl}"
sample_file="${CWL_SAMPLE_FILE:-${script_dir}/sample.txt}"
job_file="${CWL_JOB_FILE:-${record_dir}/job.yml}"
out_dir="${CWL_OUT_DIR:-${record_dir}/out}"
cache_dir="${CWL_CACHE_DIR:-${record_dir}/cache}"
tmp_dir="${CWL_TMP_DIR:-${record_dir}/tmp}"
tmp_out_dir="${CWL_TMP_OUT_DIR:-${record_dir}/tmp-out}"
cwltool_exe="${CWLTOOL_EXE:-cwltool}"
log_file="${record_dir}/cwl-smoke.log"

mkdir -p "${record_dir}" "${out_dir}" "${cache_dir}" "${tmp_dir}" "${tmp_out_dir}"

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "RUN_CWL=${RUN_CWL:-0}"
  echo
  echo "== scheduler layout =="
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-1}"
  echo
  echo "== cwl paths =="
  echo "cwl_document=${cwl_document}"
  echo "sample_file=${sample_file}"
  echo "job_file=${job_file}"
  echo "out_dir=${out_dir}"
  echo "cache_dir=${cache_dir}"
  echo "tmp_dir=${tmp_dir}"
  echo "tmp_out_dir=${tmp_out_dir}"

  if [ ! -s "${cwl_document}" ]; then
    echo "ERROR: CWL document is missing or empty: ${cwl_document}" >&2
    exit 1
  fi

  if [ -z "${CWL_JOB_FILE:-}" ]; then
    if [ ! -s "${sample_file}" ]; then
      echo "ERROR: sample file is missing or empty: ${sample_file}" >&2
      exit 1
    fi
    cat > "${job_file}" <<JOB
input_file:
  class: File
  path: ${sample_file}
JOB
  fi

  if [ ! -s "${job_file}" ]; then
    echo "ERROR: CWL job file is missing or empty: ${job_file}" >&2
    exit 1
  fi

  echo
  echo "== selected environment =="
  if command -v "${cwltool_exe}" >/dev/null 2>&1; then
    echo "${cwltool_exe}=$(command -v "${cwltool_exe}")"
    "${cwltool_exe}" --version || true
    "${cwltool_exe}" --validate "${cwl_document}" || true
  else
    echo "${cwltool_exe}=not_found"
  fi

  cwl_command=(
    "${cwltool_exe}"
    --outdir "${out_dir}"
    --cachedir "${cache_dir}"
    --tmpdir-prefix "${tmp_dir}/cwl."
    --tmp-outdir-prefix "${tmp_out_dir}/cwl."
    "${cwl_document}"
    "${job_file}"
  )

  if [ "${CWL_PARALLEL:-0}" = "1" ]; then
    cwl_command=("${cwltool_exe}" --parallel "${cwl_command[@]:1}")
  fi

  echo
  echo "== launch command =="
  printf 'command='
  printf '%q ' "${cwl_command[@]}"
  printf '\n'

  if [ -n "${CWL_EXTRA_ARGS:-}" ]; then
    echo "CWL_EXTRA_ARGS=${CWL_EXTRA_ARGS}"
    echo "extra_args_note=review site-approved cwltool options before adding them to the wrapper"
  fi

  if [ "${RUN_CWL:-0}" = "1" ]; then
    command -v "${cwltool_exe}" >/dev/null 2>&1
    "${cwltool_exe}" --validate "${cwl_document}"
    "${cwl_command[@]}"
  else
    echo "dry_run=true"
    echo "Set RUN_CWL=1 only after reviewing paths, environment, and filesystem impact."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
