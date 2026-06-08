#!/usr/bin/env bash
#SBATCH --job-name=cp2k-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=cp2k-smoke-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

record_dir="${CP2K_RECORD_DIR:-cp2k-record-${SLURM_JOB_ID:-local}}"
template_input="${CP2K_INPUT_TEMPLATE:-${script_dir}/h2o-energy.inp.template}"
generated_input="${CP2K_GENERATED_INPUT:-${record_dir}/h2o-energy.inp}"
output_file="${CP2K_OUTPUT_FILE:-${record_dir}/h2o-energy.out}"
cp2k_project="${CP2K_PROJECT:-h2o-smoke}"
cp2k_exe="${CP2K_EXE:-cp2k.psmp}"
cp2k_data_dir="${CP2K_DATA_DIR:-${record_dir}/cp2k-data}"
cp2k_basis_file="${CP2K_BASIS_FILE:-${cp2k_data_dir}/BASIS_MOLOPT}"
cp2k_potential_file="${CP2K_POTENTIAL_FILE:-${cp2k_data_dir}/GTH_POTENTIALS}"
cp2k_print_level="${CP2K_PRINT_LEVEL:-LOW}"
cp2k_omp_threads="${CP2K_OMP_THREADS:-${SLURM_CPUS_PER_TASK:-1}}"
log_file="${record_dir}/cp2k-smoke.log"

mkdir -p "${record_dir}" "${cp2k_data_dir}"

render_input() {
  sed \
    -e "s|__PROJECT__|${cp2k_project}|g" \
    -e "s|__BASIS_SET_FILE__|${cp2k_basis_file}|g" \
    -e "s|__POTENTIAL_FILE__|${cp2k_potential_file}|g" \
    -e "s|__PRINT_LEVEL__|${cp2k_print_level}|g" \
    "${template_input}" > "${generated_input}"
}

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "RUN_CP2K=${RUN_CP2K:-0}"
  echo
  echo "== scheduler layout =="
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-${SLURM_NPROCS:-4}}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-1}"
  echo "SLURM_GPUS_PER_NODE=${SLURM_GPUS_PER_NODE:-}"
  echo "OMP_NUM_THREADS=${cp2k_omp_threads}"
  echo
  echo "== inputs and paths =="
  echo "template_input=${template_input}"
  echo "generated_input=${generated_input}"
  echo "output_file=${output_file}"
  echo "cp2k_exe=${cp2k_exe}"
  echo "cp2k_project=${cp2k_project}"
  echo "cp2k_basis_file=${cp2k_basis_file}"
  echo "cp2k_potential_file=${cp2k_potential_file}"
  echo "cp2k_print_level=${cp2k_print_level}"
  echo "CP2K_EXTRA_ARGS_REVIEW_ONLY=${CP2K_EXTRA_ARGS:-}"

  if [ ! -s "${template_input}" ]; then
    echo "ERROR: CP2K input template is missing or empty: ${template_input}" >&2
    exit 1
  fi

  render_input

  echo
  echo "== selected environment =="
  if command -v "${cp2k_exe}" >/dev/null 2>&1; then
    echo "${cp2k_exe}=$(command -v "${cp2k_exe}")"
    "${cp2k_exe}" --version || true
  else
    echo "${cp2k_exe}=not_found"
  fi

  echo
  echo "== data file checks =="
  if [ -s "${cp2k_basis_file}" ]; then
    echo "basis_file_exists=${cp2k_basis_file}"
  else
    echo "basis_file_missing=${cp2k_basis_file}"
  fi
  if [ -s "${cp2k_potential_file}" ]; then
    echo "potential_file_exists=${cp2k_potential_file}"
  else
    echo "potential_file_missing=${cp2k_potential_file}"
  fi

  echo
  echo "== launch command =="
  echo "export OMP_NUM_THREADS=${cp2k_omp_threads}"
  echo "srun ${cp2k_exe} -i ${generated_input} -o ${output_file}"
  if [ -n "${CP2K_EXTRA_ARGS:-}" ]; then
    echo "extra_args_note=review these site-specific flags before editing the command"
    echo "CP2K_EXTRA_ARGS_REVIEW_ONLY=${CP2K_EXTRA_ARGS}"
  fi

  if [ "${RUN_CP2K:-0}" = "1" ]; then
    command -v "${cp2k_exe}" >/dev/null 2>&1

    if [ ! -s "${cp2k_basis_file}" ]; then
      echo "ERROR: required CP2K basis set file is missing: ${cp2k_basis_file}" >&2
      exit 2
    fi
    if [ ! -s "${cp2k_potential_file}" ]; then
      echo "ERROR: required CP2K potential file is missing: ${cp2k_potential_file}" >&2
      exit 2
    fi

    export OMP_NUM_THREADS="${cp2k_omp_threads}"
    srun "${cp2k_exe}" -i "${generated_input}" -o "${output_file}"
    echo "cp2k_output=${output_file}"
  else
    echo "dry_run=true"
    echo "Set RUN_CP2K=1 only after reviewing MPI/OpenMP layout, data files, and output volume."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
