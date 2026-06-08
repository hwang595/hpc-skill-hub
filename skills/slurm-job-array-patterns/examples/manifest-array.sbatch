#!/usr/bin/env bash
#SBATCH --job-name=manifest-array
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:05:00
#SBATCH --output=logs/%x-%A_%a.out

set -euo pipefail

manifest="${MANIFEST:-examples/array-manifest.tsv}"
task_id="${SLURM_ARRAY_TASK_ID:?submit with sbatch --array=1-N%limit}"

mkdir -p logs results

line="$(sed -n "${task_id}p" "${manifest}")"
if [ -z "${line}" ]; then
  echo "No manifest line for task ${task_id}"
  exit 2
fi

sample_id="$(printf "%s\n" "${line}" | awk -F '\t' '{print $1}')"
input_path="$(printf "%s\n" "${line}" | awk -F '\t' '{print $2}')"
output_path="$(printf "%s\n" "${line}" | awk -F '\t' '{print $3}')"

echo "array_job=${SLURM_ARRAY_JOB_ID:-unknown}"
echo "task_id=${task_id}"
echo "sample_id=${sample_id}"
echo "input_path=${input_path}"
echo "output_path=${output_path}"
echo "host=$(hostname)"

# Replace this section with the real per-task command.
printf "processed\t%s\t%s\n" "${sample_id}" "${input_path}" > "${output_path}"
