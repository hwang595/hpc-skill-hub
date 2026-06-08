#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: pending-reason-triage.sh [job-id]

With a job id, inspect that job's pending reason, details, and priority factors.
Without a job id, list pending jobs for the current user.
USAGE
}

job_id="${1:-}"
if [[ "${job_id}" == "-h" || "${job_id}" == "--help" ]]; then
  usage
  exit 0
fi

if ! command -v squeue >/dev/null 2>&1; then
  echo "ERROR: squeue is required." >&2
  exit 1
fi

format="%.18i %.9P %.40j %.12u %.2t %.10M %.10l %.6D %.12Q %.30E %R"

echo "Slurm pending reason triage"
echo "==========================="
echo

if [[ -n "${job_id}" ]]; then
  if ! [[ "${job_id}" =~ ^[A-Za-z0-9_.+-]+$ ]]; then
    echo "ERROR: job id contains unexpected characters: ${job_id}" >&2
    exit 2
  fi

  echo "== squeue snapshot for ${job_id} =="
  squeue --jobs="${job_id}" --format="${format}" || true
  echo

  if command -v scontrol >/dev/null 2>&1; then
    echo "== scontrol job details =="
    scontrol show job "${job_id}" || true
    echo
  else
    echo "== scontrol job details =="
    echo "scontrol is not available on this system."
    echo
  fi

  if command -v sprio >/dev/null 2>&1; then
    echo "== sprio priority factors =="
    sprio --jobs="${job_id}" || true
    echo
  else
    echo "== sprio priority factors =="
    echo "sprio is not available or not enabled on this system."
    echo
  fi
else
  user="${SLURM_USER:-${USER:-}}"
  if [[ -z "${user}" ]]; then
    echo "ERROR: no job id supplied and USER is not set." >&2
    exit 2
  fi

  echo "== pending jobs for ${user} =="
  squeue --states=PENDING --user="${user}" --format="${format}" || true
  echo

  if command -v sprio >/dev/null 2>&1; then
    echo "== priority factors for ${user} pending jobs =="
    sprio --user="${user}" || true
    echo
  fi
fi

cat <<'PROMPTS'
== review prompts ==
- If Reason is Dependency, inspect the upstream job or array task.
- If Reason is Priority, check whether fairshare, QOS, age, or partition policy is expected.
- If Reason is Resources, review CPU, memory, GPU, node, feature, and time requests.
- If Reason names a partition, reservation, or unavailable node, use local public policy docs.
- Avoid posting raw queue output publicly when it includes private names, accounts, or policy.
PROMPTS
