#!/usr/bin/env bash
set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

pipeline="${1:-nf-core/rnaseq}"
samplesheet="${2:-${script_dir}/samplesheet.csv}"
outdir="${3:-nfcore-results}"
work_dir="${4:-nfcore-work}"
config_path="${NFCORE_CONFIG:-${script_dir}/nfcore-slurm.config}"
profile="${NFCORE_PROFILE:-test,singularity,hpc_slurm}"
revision="${NFCORE_REVISION:-}"
record_dir="${NFCORE_RECORD_DIR:-nfcore-record}"

if [ ! -f "${samplesheet}" ]; then
  echo "error: samplesheet does not exist: ${samplesheet}"
  exit 2
fi

if [ ! -f "${config_path}" ]; then
  echo "error: config does not exist: ${config_path}"
  exit 2
fi

mkdir -p "${record_dir}" "${outdir}" "${work_dir}"
log_file="${record_dir}/nfcore-launch-$(date -u +%Y%m%d-%H%M%S).log"

cache_dir="${NXF_SINGULARITY_CACHEDIR:-${PWD}/singularity-cache}"
export NXF_SINGULARITY_CACHEDIR="${cache_dir}"
mkdir -p "${NXF_SINGULARITY_CACHEDIR}"

command=(nextflow run "${pipeline}")
if [ -n "${revision}" ]; then
  command+=(-r "${revision}")
fi

command+=(
  -profile "${profile}"
  -c "${config_path}"
  --input "${samplesheet}"
  --outdir "${outdir}"
  -work-dir "${work_dir}"
)

if [ "${NFCORE_RESUME:-0}" = "1" ]; then
  command+=(-resume)
fi

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "pipeline=${pipeline}"
  echo "revision=${revision:-<not-pinned>}"
  echo "profile=${profile}"
  echo "config_path=${config_path}"
  echo "samplesheet=${samplesheet}"
  echo "outdir=${outdir}"
  echo "work_dir=${work_dir}"
  echo "NXF_SINGULARITY_CACHEDIR=${NXF_SINGULARITY_CACHEDIR}"
  echo "NFCORE_RESUME=${NFCORE_RESUME:-0}"
  echo "RUN_NFCORE=${RUN_NFCORE:-0}"
  echo "command=${command[*]}"
  echo
} | tee "${log_file}"

if [ "${RUN_NFCORE:-0}" = "1" ]; then
  "${command[@]}" 2>&1 | tee -a "${log_file}"
else
  echo "dry_run=true" | tee -a "${log_file}"
  echo "Set RUN_NFCORE=1 only after reviewing the plan and using a small test profile." | tee -a "${log_file}"
fi

echo "log_file=${log_file}"
