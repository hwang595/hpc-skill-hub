#!/usr/bin/env bash
#SBATCH --job-name=qe-pwscf-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=qe-pwscf-smoke-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

record_dir="${QE_RECORD_DIR:-qe-record-${SLURM_JOB_ID:-local}}"
template_input="${QE_INPUT_TEMPLATE:-${script_dir}/si.scf.in.template}"
generated_input="${QE_GENERATED_INPUT:-${record_dir}/si.scf.in}"
output_file="${QE_OUTPUT_FILE:-${record_dir}/si.scf.out}"
qe_prefix="${QE_PREFIX:-si-smoke}"
qe_exe="${QE_EXE:-pw.x}"
qe_pseudo_dir="${QE_PSEUDO_DIR:-${record_dir}/pseudo}"
qe_outdir="${QE_OUTDIR:-${record_dir}/outdir}"
qe_wfcdir="${QE_WFCDIR:-${record_dir}/wfcdir}"
qe_max_seconds="${QE_MAX_SECONDS:-240}"
log_file="${record_dir}/qe-pwscf-smoke.log"

mkdir -p "${record_dir}" "${qe_pseudo_dir}" "${qe_outdir}" "${qe_wfcdir}"

render_input() {
  sed \
    -e "s|__PREFIX__|${qe_prefix}|g" \
    -e "s|__PSEUDO_DIR__|${qe_pseudo_dir}|g" \
    -e "s|__OUTDIR__|${qe_outdir}|g" \
    -e "s|__WFCDIR__|${qe_wfcdir}|g" \
    -e "s|__MAX_SECONDS__|${qe_max_seconds}|g" \
    "${template_input}" > "${generated_input}"
}

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "RUN_QE=${RUN_QE:-0}"
  echo
  echo "== scheduler layout =="
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-${SLURM_NPROCS:-4}}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-1}"
  echo
  echo "== inputs and paths =="
  echo "template_input=${template_input}"
  echo "generated_input=${generated_input}"
  echo "output_file=${output_file}"
  echo "qe_exe=${qe_exe}"
  echo "qe_prefix=${qe_prefix}"
  echo "qe_pseudo_dir=${qe_pseudo_dir}"
  echo "qe_outdir=${qe_outdir}"
  echo "qe_wfcdir=${qe_wfcdir}"
  echo "qe_max_seconds=${qe_max_seconds}"

  if [ ! -s "${template_input}" ]; then
    echo "ERROR: QE input template is missing or empty: ${template_input}" >&2
    exit 1
  fi

  render_input

  echo
  echo "== selected environment =="
  if command -v "${qe_exe}" >/dev/null 2>&1; then
    echo "${qe_exe}=$(command -v "${qe_exe}")"
    "${qe_exe}" --version || true
  else
    echo "${qe_exe}=not_found"
  fi

  echo
  echo "== pseudopotential check =="
  if grep -q "Si.pbe-n-kjpaw_psl.1.0.0.UPF" "${generated_input}"; then
    pseudo_file="${qe_pseudo_dir}/Si.pbe-n-kjpaw_psl.1.0.0.UPF"
    if [ -s "${pseudo_file}" ]; then
      echo "pseudo_file_exists=${pseudo_file}"
    else
      echo "pseudo_file_missing=${pseudo_file}"
    fi
  else
    echo "pseudo_file_check=custom_template_review_required"
  fi

  echo
  echo "== launch command =="
  echo "srun ${qe_exe} -in ${generated_input} > ${output_file}"

  if [ "${RUN_QE:-0}" = "1" ]; then
    command -v "${qe_exe}" >/dev/null 2>&1

    if [ -n "${pseudo_file:-}" ] && [ ! -s "${pseudo_file}" ]; then
      echo "ERROR: required pseudopotential is missing: ${pseudo_file}" >&2
      exit 2
    fi

    srun "${qe_exe}" -in "${generated_input}" > "${output_file}"
    echo "qe_output=${output_file}"
  else
    echo "dry_run=true"
    echo "Set RUN_QE=1 only after reviewing MPI layout, pseudopotentials, and scratch paths."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
