#!/usr/bin/env bash
#SBATCH --job-name=wrf-realdata
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=wrf-realdata-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

case_name="${WRF_CASE_NAME:-wrf-realdata-smoke}"
run_template="${WRF_RUN_TEMPLATE:-/path/to/clean/WRF/run-template}"
namelist_file="${WRF_NAMELIST:-${script_dir}/namelist.input.template}"
met_em_glob="${WRF_MET_EM_GLOB:-/path/to/WPS/met_em.d01.*.nc}"
output_dir="${WRF_OUTPUT_DIR:-wrf-output}"
record_dir="${WRF_RECORD_DIR:-wrf-record}"
work_dir="${output_dir}/${case_name}"
real_ntasks="${WRF_REAL_NTASKS:-${SLURM_NTASKS:-4}}"
wrf_ntasks="${WRF_WRF_NTASKS:-${SLURM_NTASKS:-4}}"
log_file="${record_dir}/wrf-launch-$(date -u +%Y%m%d-%H%M%S).log"

absolute_path() {
  case "$1" in
    /*)
      printf "%s\n" "$1"
      ;;
    */*)
      printf "%s/%s\n" "$(cd "${1%/*}" && pwd)" "${1##*/}"
      ;;
    *)
      printf "%s/%s\n" "$(pwd)" "$1"
      ;;
  esac
}

mkdir -p "${output_dir}" "${record_dir}"

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_WRF=${RUN_WRF:-0}"
  echo "WRF_CASE_NAME=${case_name}"
  echo "WRF_RUN_TEMPLATE=${run_template}"
  echo "WRF_NAMELIST=${namelist_file}"
  echo "WRF_MET_EM_GLOB=${met_em_glob}"
  echo "WRF_OUTPUT_DIR=${output_dir}"
  echo "WRF_WORK_DIR=${work_dir}"
  echo "WRF_REAL_NTASKS=${real_ntasks}"
  echo "WRF_WRF_NTASKS=${wrf_ntasks}"
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-}"

  echo
  echo "== input checks =="
  if [ -d "${run_template}" ]; then
    echo "run_template_exists=true"
  else
    echo "missing_run_template=${run_template}"
  fi
  if [ -f "${namelist_file}" ]; then
    echo "namelist_exists=true"
  else
    echo "missing_namelist=${namelist_file}"
    exit 2
  fi

  shopt -s nullglob
  raw_met_files=( ${met_em_glob} )
  met_files=()
  for met_file in "${raw_met_files[@]}"; do
    if [ -f "${met_file}" ]; then
      met_files+=("${met_file}")
    fi
  done
  echo "met_em_match_count=${#met_files[@]}"
  if [ "${#met_files[@]}" -eq 0 ]; then
    echo "met_em_note=provide WRF_MET_EM_GLOB before RUN_WRF=1"
  fi

  echo
  echo "== launch plan =="
  stage_command=(cp -R "${run_template}/." "${work_dir}/")
  namelist_command=(cp "${namelist_file}" "${work_dir}/namelist.input")
  real_command=(srun -n "${real_ntasks}" ./real.exe)
  wrf_command=(srun -n "${wrf_ntasks}" ./wrf.exe)
  echo "stage_command=${stage_command[*]}"
  echo "namelist_command=${namelist_command[*]}"
  echo "met_em_link_pattern=${met_em_glob}"
  echo "real_command=(cd ${work_dir} && ${real_command[*]})"
  echo "wrf_command=(cd ${work_dir} && ${wrf_command[*]})"
  echo "expected_real_outputs=wrfinput_d0* wrfbdy_d01"
  echo "expected_wrf_outputs=wrfout_d0* wrfrst_d0* rsl.out.* rsl.error.*"

  if [ "${RUN_WRF:-0}" = "1" ]; then
    if [ ! -d "${run_template}" ]; then
      echo "Cannot run: WRF_RUN_TEMPLATE must point to a clean WRF run directory."
      exit 2
    fi
    if [ "${#met_files[@]}" -eq 0 ]; then
      echo "Cannot run: WRF_MET_EM_GLOB did not match any met_em files."
      exit 2
    fi
    if [ -e "${work_dir}" ]; then
      echo "Cannot run: WRF_WORK_DIR already exists. Choose a fresh WRF_OUTPUT_DIR or WRF_CASE_NAME."
      exit 2
    fi

    mkdir -p "${work_dir}"
    "${stage_command[@]}"
    "${namelist_command[@]}"
    for met_file in "${met_files[@]}"; do
      ln -sf "$(absolute_path "${met_file}")" "${work_dir}/"
    done

    (
      cd "${work_dir}"
      "${real_command[@]}"
    )
    if [ ! -f "${work_dir}/wrfbdy_d01" ]; then
      echo "real_output_missing=wrfbdy_d01"
      exit 2
    fi
    wrfinput_files=( "${work_dir}"/wrfinput_d0* )
    if [ "${#wrfinput_files[@]}" -eq 0 ]; then
      echo "real_output_missing=wrfinput_d0*"
      exit 2
    fi
    (
      cd "${work_dir}"
      "${wrf_command[@]}"
    )
  else
    echo "dry_run=true"
    echo "Set RUN_WRF=1 only after loading the correct module/container, reviewing namelist.input, and checking output volume."
  fi

  echo "staged_case=${work_dir}"
  echo "log_file=${log_file}"
} 2>&1 | tee "${log_file}"
