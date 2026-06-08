#!/usr/bin/env bash
set -euo pipefail

export ACCOUNT="${ACCOUNT:-<account>}"
export PARTITION="${PARTITION:-<partition>}"
export LICENSE_RESOURCE="${LICENSE_RESOURCE:-<license-resource>}"
export LICENSE_COUNT="${LICENSE_COUNT:-1}"
export SLURM_LICENSE_REQUEST="${SLURM_LICENSE_REQUEST:-${LICENSE_RESOURCE}:${LICENSE_COUNT}}"
export APP_MODULE="${APP_MODULE:-}"
export APP_COMMAND="${APP_COMMAND:-hostname}"
export RUN_LICENSED_APP="${RUN_LICENSED_APP:-0}"
export SUBMIT_LICENSED_JOB="${SUBMIT_LICENSED_JOB:-0}"
export OUTPUT_DIR="${OUTPUT_DIR:-license-aware-slurm-plan}"
export LMUTIL_LICENSE_SPEC="${LMUTIL_LICENSE_SPEC:-}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
job_template="${JOB_TEMPLATE:-${script_dir}/licensed-software-template.sbatch}"
status_report="${OUTPUT_DIR}/license-status.txt"
plan_report="${OUTPUT_DIR}/submission-plan.txt"

mkdir -p "${OUTPUT_DIR}"

{
  echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "ACCOUNT=${ACCOUNT}"
  echo "PARTITION=${PARTITION}"
  echo "SLURM_LICENSE_REQUEST=${SLURM_LICENSE_REQUEST}"
  echo "APP_MODULE=${APP_MODULE}"
  echo "APP_COMMAND=${APP_COMMAND}"
  echo "RUN_LICENSED_APP=${RUN_LICENSED_APP}"
  echo
  echo "== slurm licenses =="
  if command -v scontrol >/dev/null 2>&1; then
    scontrol show lic 2>&1 || true
  else
    echo "scontrol is not available in this environment."
  fi
  echo
  echo "== optional lmutil status =="
  if [ -n "${LMUTIL_LICENSE_SPEC}" ]; then
    if command -v lmutil >/dev/null 2>&1; then
      lmutil lmstat -a -c "${LMUTIL_LICENSE_SPEC}" 2>&1 || true
    else
      echo "LMUTIL_LICENSE_SPEC was set, but lmutil is not available."
    fi
  else
    echo "LMUTIL_LICENSE_SPEC is unset; skipping external license-manager check."
  fi
} > "${status_report}"

submit_command=(
  sbatch
  --account "${ACCOUNT}"
  --partition "${PARTITION}"
  --licenses "${SLURM_LICENSE_REQUEST}"
  --export "ALL,RUN_LICENSED_APP=${RUN_LICENSED_APP},APP_MODULE=${APP_MODULE},APP_COMMAND=${APP_COMMAND},OUTPUT_DIR=${OUTPUT_DIR}"
  "${job_template}"
)

{
  echo "status_report=${status_report}"
  echo "job_template=${job_template}"
  printf 'submit_command='
  printf '%q ' "${submit_command[@]}"
  printf '\n'
  echo "SUBMIT_LICENSED_JOB=${SUBMIT_LICENSED_JOB}"
} > "${plan_report}"

cat "${plan_report}"

if [ "${SUBMIT_LICENSED_JOB}" != "1" ]; then
  echo "Dry-run complete. Set SUBMIT_LICENSED_JOB=1 to submit the template."
  exit 0
fi

"${submit_command[@]}"
