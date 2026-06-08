#!/usr/bin/env bash
#SBATCH --job-name=stage-scratch
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=stage-scratch-%j.out

set -euo pipefail

manifest="${INPUT_MANIFEST:-examples/input-manifest.txt}"
scratch_root="${SCRATCH_ROOT:-${SLURM_TMPDIR:-scratch-${SLURM_JOB_ID:-local}}}"
output_dir="${OUTPUT_DIR:-staged-output}"
work_dir="${scratch_root}/work"

mkdir -p "${work_dir}" "${output_dir}"

echo "job_id=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "manifest=${manifest}"
echo "scratch_root=${scratch_root}"
echo "output_dir=${output_dir}"

echo
echo "== stage in =="
while IFS= read -r input_path; do
  case "${input_path}" in
    ""|\#*) continue ;;
  esac
  if [ -e "${input_path}" ]; then
    rsync -a "${input_path}" "${work_dir}/"
  else
    echo "missing ${input_path}"
    exit 2
  fi
done < "${manifest}"

echo
echo "== work =="
cd "${work_dir}"
pwd > result.txt
find . -maxdepth 2 -type f | sort > staged-files.txt

echo
echo "== stage out =="
rsync -a result.txt staged-files.txt "${output_dir}/"

echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
