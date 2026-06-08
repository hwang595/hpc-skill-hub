#!/usr/bin/env bash
#SBATCH --job-name=openfoam-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=openfoam-smoke-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

solver="${OPENFOAM_SOLVER:-icoFoam}"
case_template="${OPENFOAM_CASE_TEMPLATE:-${script_dir}/cavity-smoke}"
case_name="${OPENFOAM_CASE_NAME:-cavity-smoke}"
output_dir="${OPENFOAM_OUTPUT_DIR:-openfoam-output}"
record_dir="${OPENFOAM_RECORD_DIR:-openfoam-record}"
case_workdir="${output_dir}/${case_name}"
ntasks="${OPENFOAM_NTASKS:-${SLURM_NTASKS:-2}}"
decomp_n="${OPENFOAM_DECOMP_N:-(${ntasks} 1 1)}"
log_file="${record_dir}/openfoam-launch-$(date -u +%Y%m%d-%H%M%S).log"
decompose_dict="${case_workdir}/system/decomposeParDict"

write_decompose_dict() {
  cat > "${decompose_dict}" <<EOF
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}

numberOfSubdomains ${ntasks};

method          simple;

simpleCoeffs
{
    n               ${decomp_n};
    delta           0.001;
}

distributed     no;

roots           ();
EOF
}

mkdir -p "${output_dir}" "${record_dir}"

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_OPENFOAM=${RUN_OPENFOAM:-0}"
  echo "OPENFOAM_SOLVER=${solver}"
  echo "OPENFOAM_CASE_TEMPLATE=${case_template}"
  echo "OPENFOAM_OUTPUT_DIR=${output_dir}"
  echo "OPENFOAM_CASE_WORKDIR=${case_workdir}"
  echo "OPENFOAM_NTASKS=${ntasks}"
  echo "OPENFOAM_DECOMP_N=${decomp_n}"
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-}"

  echo
  echo "== case checks =="
  for path in "${case_template}/0" "${case_template}/constant" "${case_template}/system"; do
    if [ -d "${path}" ]; then
      echo "exists=${path}"
    else
      echo "missing=${path}"
      exit 2
    fi
  done

  echo
  echo "== launch plan =="
  blockmesh_command=(blockMesh -case "${case_workdir}")
  decompose_command=(decomposePar -case "${case_workdir}")
  solver_command=(srun "${solver}" -case "${case_workdir}" -parallel)
  reconstruct_command=(reconstructPar -case "${case_workdir}" -latestTime)
  echo "stage_command=cp -R ${case_template} ${case_workdir}"
  echo "decomposeParDict=${decompose_dict}"
  echo "blockMesh_command=${blockmesh_command[*]}"
  echo "decompose_command=${decompose_command[*]}"
  echo "solver_command=${solver_command[*]}"
  echo "reconstruct_command=${reconstruct_command[*]}"

  if [ "${RUN_OPENFOAM:-0}" = "1" ]; then
    if [ -e "${case_workdir}" ]; then
      echo "case_workdir_already_exists=${case_workdir}"
      echo "Choose a fresh OPENFOAM_OUTPUT_DIR or OPENFOAM_CASE_NAME before running."
      exit 2
    fi
    cp -R "${case_template}" "${case_workdir}"
    write_decompose_dict
    "${blockmesh_command[@]}"
    "${decompose_command[@]}"
    "${solver_command[@]}"
    "${reconstruct_command[@]}"
  else
    echo "dry_run=true"
    echo "Set RUN_OPENFOAM=1 only after loading the correct module/container and reviewing output volume."
  fi

  echo "staged_case=${case_workdir}"
  echo "log_file=${log_file}"
} 2>&1 | tee "${log_file}"
