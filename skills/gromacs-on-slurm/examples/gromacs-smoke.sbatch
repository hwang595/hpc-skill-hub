#!/usr/bin/env bash
#SBATCH --job-name=gromacs-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=gromacs-smoke-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

gmx_cmd="${GMX_CMD:-gmx}"
mdp_file="${GMX_MDP:-${script_dir}/smoke.mdp}"
coord_file="${GMX_COORD:-${script_dir}/conf.gro}"
top_file="${GMX_TOP:-${script_dir}/topol.top}"
output_dir="${GMX_OUTPUT_DIR:-gromacs-output}"
record_dir="${GMX_RECORD_DIR:-gromacs-record}"
deffnm="${GMX_DEFFNM:-smoke}"
tpr_file="${output_dir}/${deffnm}.tpr"
checkpoint_file="${output_dir}/${deffnm}.cpt"
log_file="${record_dir}/gromacs-launch-$(date -u +%Y%m%d-%H%M%S).log"

mkdir -p "${output_dir}" "${record_dir}"

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_GROMACS=${RUN_GROMACS:-0}"
  echo "GMX_CMD=${gmx_cmd}"
  echo "GMX_MDP=${mdp_file}"
  echo "GMX_COORD=${coord_file}"
  echo "GMX_TOP=${top_file}"
  echo "GMX_NB=${GMX_NB:-}"
  echo "GMX_PME=${GMX_PME:-}"
  echo "GMX_GPU_ID=${GMX_GPU_ID:-}"
  echo "GMX_OUTPUT_DIR=${output_dir}"
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-}"
  echo "SLURM_GPUS_PER_NODE=${SLURM_GPUS_PER_NODE:-}"
  echo "OMP_NUM_THREADS=${OMP_NUM_THREADS:-${SLURM_CPUS_PER_TASK:-1}}"

  echo
  echo "== input checks =="
  for path in "${mdp_file}" "${coord_file}" "${top_file}"; do
    if [ -f "${path}" ]; then
      echo "exists=${path}"
    else
      echo "missing=${path}"
      exit 2
    fi
  done

  echo
  echo "== launch plan =="
  grompp_command=(
    "${gmx_cmd}"
    grompp
    -f "${mdp_file}"
    -c "${coord_file}"
    -p "${top_file}"
    -o "${tpr_file}"
    -maxwarn "${GMX_MAXWARN:-0}"
  )
  mdrun_command=(
    srun
    "${gmx_cmd}"
    mdrun
    -s "${tpr_file}"
    -deffnm "${output_dir}/${deffnm}"
    -cpt "${GMX_CPT_MINUTES:-15}"
    -cpo "${checkpoint_file}"
    -ntomp "${OMP_NUM_THREADS:-${SLURM_CPUS_PER_TASK:-1}}"
  )
  if [ -n "${GMX_NB:-}" ]; then
    mdrun_command+=(-nb "${GMX_NB}")
  fi
  if [ -n "${GMX_PME:-}" ]; then
    mdrun_command+=(-pme "${GMX_PME}")
  fi
  if [ -n "${GMX_GPU_ID:-}" ]; then
    mdrun_command+=(-gpu_id "${GMX_GPU_ID}")
  fi
  echo "grompp_command=${grompp_command[*]}"
  echo "mdrun_command=${mdrun_command[*]}"

  if [ "${RUN_GROMACS:-0}" = "1" ]; then
    "${grompp_command[@]}"
    "${mdrun_command[@]}"
  else
    echo "dry_run=true"
    echo "Set RUN_GROMACS=1 only after loading the correct module/container and reviewing output volume."
  fi

  echo "tpr_file=${tpr_file}"
  echo "checkpoint_file=${checkpoint_file}"
  echo "log_file=${log_file}"
} 2>&1 | tee "${log_file}"
