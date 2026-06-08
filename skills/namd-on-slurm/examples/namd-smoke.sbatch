#!/usr/bin/env bash
#SBATCH --job-name=namd-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=namd-smoke-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

namd_exe="${NAMD_EXE:-namd2}"
namd_config="${NAMD_CONFIG:-${script_dir}/namd-smoke.conf}"
output_dir="${NAMD_OUTPUT_DIR:-namd-output}"
record_dir="${NAMD_RECORD_DIR:-namd-record}"
restart_prefix="${NAMD_RESTART_PREFIX:-${output_dir}/restart/namd-smoke}"
log_file="${record_dir}/namd-launch-$(date -u +%Y%m%d-%H%M%S).log"
namd_log="${output_dir}/namd-smoke.log"
namd_pes="${NAMD_PES:-${SLURM_NTASKS:-1}}"

mkdir -p "${output_dir}" "${record_dir}" "$(dirname "${restart_prefix}")"

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_NAMD=${RUN_NAMD:-0}"
  echo "NAMD_EXE=${namd_exe}"
  echo "NAMD_CONFIG=${namd_config}"
  echo "NAMD_OUTPUT_DIR=${output_dir}"
  echo "NAMD_RESTART_PREFIX=${restart_prefix}"
  echo "NAMD_PES=${namd_pes}"
  echo "NAMD_EXTRA_ARGS_REVIEW_ONLY=${NAMD_EXTRA_ARGS:-}"
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_NNODES=${SLURM_NNODES:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-}"
  echo "SLURM_GPUS_PER_NODE=${SLURM_GPUS_PER_NODE:-}"

  echo
  echo "== input checks =="
  if [ -f "${namd_config}" ]; then
    echo "config_exists=true"
  else
    echo "missing_config=${namd_config}"
    exit 2
  fi

  echo
  echo "== launch plan =="
  command=(
    srun
    "${namd_exe}"
    "+p${namd_pes}"
  )
  if [ -n "${NAMD_EXTRA_ARGS:-}" ]; then
    echo "extra_args_note=review these site-specific flags before editing the command"
    echo "NAMD_EXTRA_ARGS_REVIEW_ONLY=${NAMD_EXTRA_ARGS}"
  fi
  command+=(
    "${namd_config}"
  )
  echo "command=${command[*]} > ${namd_log}"

  if [ "${RUN_NAMD:-0}" = "1" ]; then
    "${command[@]}" > "${namd_log}"
  else
    echo "dry_run=true"
    echo "Set RUN_NAMD=1 only after loading the correct module/container and reviewing output volume."
  fi

  echo "namd_log=${namd_log}"
  echo "restart_prefix=${restart_prefix}"
  echo "log_file=${log_file}"
} 2>&1 | tee "${log_file}"
