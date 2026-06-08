#!/usr/bin/env bash
#SBATCH --job-name=node-local-scratch
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=node-local-scratch-%j.out

set -euo pipefail

manifest="${INPUT_MANIFEST:-examples/input-manifest.txt}"
output_dir="${OUTPUT_DIR:-node-local-output}"
node_local_base="${NODE_LOCAL_BASE:-${SLURM_TMPDIR:-${TMPDIR:-}}}"
cleanup_node_local="${CLEANUP_NODE_LOCAL:-0}"
stage_out_on_exit="${STAGE_OUT_ON_EXIT:-1}"
workload_command="${WORKLOAD_COMMAND:-}"
job_id="${SLURM_JOB_ID:-local}"
work_dir=""
marker_name=".hpc-skill-node-local-scratch"

if [ -z "${node_local_base}" ]; then
  node_local_base="${PWD}/node-local-fallback-${job_id}"
  echo "NODE_LOCAL_BASE, SLURM_TMPDIR, and TMPDIR were unset; using local fallback ${node_local_base}"
fi

mkdir -p "${node_local_base}" "${output_dir}"
node_local_base="$(cd "${node_local_base}" && pwd -P)"
output_dir="$(cd "${output_dir}" && pwd -P)"
work_dir="$(mktemp -d "${node_local_base%/}/hpc-skill-node-local-${job_id}.XXXXXX")"
marker="${work_dir}/${marker_name}"
touch "${marker}"
mkdir -p "${work_dir}/inputs" "${work_dir}/outputs" "${work_dir}/logs"
report="${work_dir}/logs/node-local-report.txt"

stage_out() {
  if [ "${stage_out_on_exit}" = "1" ] && [ -d "${work_dir}" ]; then
    mkdir -p "${output_dir}/logs"
    rsync -a "${work_dir}/outputs/" "${output_dir}/" || true
    rsync -a "${work_dir}/logs/" "${output_dir}/logs/" || true
  fi
}

cleanup() {
  status=$?
  if [ -n "${work_dir}" ] && [ -d "${work_dir}" ]; then
    {
      echo
      echo "== exit =="
      echo "exit_status=${status}"
      echo "stage_out_on_exit=${stage_out_on_exit}"
      echo "cleanup_node_local=${cleanup_node_local}"
    } >> "${report}" 2>/dev/null || true
    stage_out
    if [ "${cleanup_node_local}" = "1" ]; then
      case "${work_dir}" in
        */hpc-skill-node-local-*)
          if [ -f "${marker}" ]; then
            rm -rf -- "${work_dir}"
          else
            echo "Refusing cleanup: marker missing from ${work_dir}" >&2
          fi
          ;;
        *)
          echo "Refusing cleanup: unexpected work_dir ${work_dir}" >&2
          ;;
      esac
    fi
  fi
  exit "${status}"
}
trap cleanup EXIT INT TERM

{
  echo "== environment =="
  echo "job_id=${job_id}"
  echo "host=$(hostname 2>/dev/null || echo unknown)"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unknown)"
  echo "manifest=${manifest}"
  echo "node_local_base=${node_local_base}"
  echo "work_dir=${work_dir}"
  echo "output_dir=${output_dir}"
  echo
  echo "== capacity =="
  df -h "${node_local_base}" || true
} > "${report}"

echo "== stage in ==" | tee -a "${report}"
while IFS= read -r input_path; do
  case "${input_path}" in
    ""|\#*) continue ;;
  esac
  if [ -e "${input_path}" ]; then
    echo "stage_in=${input_path}" | tee -a "${report}"
    rsync -a "${input_path}" "${work_dir}/inputs/"
  else
    echo "missing_input=${input_path}" | tee -a "${report}"
    exit 2
  fi
done < "${manifest}"

echo "== work ==" | tee -a "${report}"
cd "${work_dir}/work" 2>/dev/null || mkdir -p "${work_dir}/work" && cd "${work_dir}/work"

if [ -n "${workload_command}" ]; then
  echo "workload_command=${workload_command}" | tee -a "${report}"
  bash -lc "${workload_command}"
else
  pwd > "${work_dir}/outputs/working-directory.txt"
  find "${work_dir}/inputs" -maxdepth 2 -type f | sort > "${work_dir}/outputs/staged-input-files.txt"
fi

echo "== stage out ==" | tee -a "${report}"
stage_out
stage_out_on_exit=0

echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unknown)" | tee -a "${report}"
rsync -a "${work_dir}/logs/" "${output_dir}/logs/"

if [ "${cleanup_node_local}" = "1" ]; then
  cleanup
fi

echo "Node-local work directory kept for review: ${work_dir}"
echo "Set CLEANUP_NODE_LOCAL=1 only after confirming outputs staged out."
