#!/usr/bin/env bash
#SBATCH --job-name=lammps-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=lammps-smoke-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

lammps_exe="${LAMMPS_EXE:-lmp}"
input_script="${LAMMPS_INPUT:-${script_dir}/in.lj}"
output_dir="${LAMMPS_OUTPUT_DIR:-lammps-output}"
record_dir="${LAMMPS_RECORD_DIR:-lammps-record}"
restart_dir="${LAMMPS_RESTART_DIR:-${output_dir}/restart}"
log_file="${record_dir}/lammps-launch-$(date -u +%Y%m%d-%H%M%S).log"
lammps_log="${output_dir}/log.lammps"

mkdir -p "${output_dir}" "${record_dir}" "${restart_dir}"

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_LAMMPS=${RUN_LAMMPS:-0}"
  echo "LAMMPS_EXE=${lammps_exe}"
  echo "LAMMPS_INPUT=${input_script}"
  echo "LAMMPS_OUTPUT_DIR=${output_dir}"
  echo "LAMMPS_RESTART_DIR=${restart_dir}"
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-}"
  echo "SLURM_GPUS_PER_NODE=${SLURM_GPUS_PER_NODE:-}"

  echo
  echo "== input checks =="
  if [ -f "${input_script}" ]; then
    echo "input_script_exists=true"
  else
    echo "missing_input_script=${input_script}"
    exit 2
  fi

  echo
  echo "== launch plan =="
  command=(
    srun
    "${lammps_exe}"
    -in "${input_script}"
    -log "${lammps_log}"
    -var restart_dir "${restart_dir}"
  )
  if [ -n "${LAMMPS_EXTRA_ARGS:-}" ]; then
    echo "LAMMPS_EXTRA_ARGS=${LAMMPS_EXTRA_ARGS}"
    echo "extra_args_note=append site-approved accelerator flags manually after reviewing the command"
  fi
  echo "command=${command[*]}"

  if [ "${RUN_LAMMPS:-0}" = "1" ]; then
    "${command[@]}"
  else
    echo "dry_run=true"
    echo "Set RUN_LAMMPS=1 only after loading the correct module/container and reviewing output volume."
  fi

  echo "lammps_log=${lammps_log}"
  echo "log_file=${log_file}"
} 2>&1 | tee "${log_file}"
