#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: maintenance-reservation-triage.sh [job-id]

Environment variables:
  PARTITION      Optional Slurm partition for sinfo scope.
  NODE           Optional Slurm node name for scontrol show node.
  RESERVATION    Optional Slurm reservation name for scontrol show reservation.
  SHOW_ALL_PENDING=1 to show all pending jobs instead of only the current user.

This script is read-only. It queries queue, node, and reservation state.
USAGE
}

job_id="${1:-}"
partition="${PARTITION:-}"
node_name="${NODE:-}"
reservation="${RESERVATION:-}"

if [[ "${job_id}" == "-h" || "${job_id}" == "--help" ]]; then
  usage
  exit 0
fi

for value_name in job_id partition node_name reservation; do
  value="${!value_name}"
  if [[ -n "${value}" && ! "${value}" =~ ^[A-Za-z0-9_.+@=:/,\[\]-]+$ ]]; then
    echo "ERROR: ${value_name} contains unexpected characters: ${value}" >&2
    exit 2
  fi
done

if ! command -v squeue >/dev/null 2>&1; then
  echo "ERROR: squeue is required." >&2
  exit 1
fi

if ! command -v sinfo >/dev/null 2>&1; then
  echo "ERROR: sinfo is required." >&2
  exit 1
fi

queue_format="%.18i %.12P %.40j %.12u %.10T %.10M %.10l %.6D %.8C %.12m %.20S %.30Y %.24v %R"
sinfo_format="%20P %.8a %.10l %.8D %.12t %E"

echo "Slurm maintenance and reservation triage"
echo "========================================"
echo
printf 'job_id=%s\n' "${job_id:-<current-user-pending>}"
printf 'partition=%s\n' "${partition:-<all-visible>}"
printf 'node=%s\n' "${node_name:-<not-requested>}"
printf 'reservation=%s\n' "${reservation:-<all-visible-if-scontrol-available>}"
echo

if [[ -n "${job_id}" ]]; then
  echo "== squeue snapshot for ${job_id} =="
  squeue --jobs="${job_id}" --format="${queue_format}" || true
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
else
  echo "== pending jobs =="
  if [[ "${SHOW_ALL_PENDING:-0}" == "1" ]]; then
    squeue --states=PENDING --format="${queue_format}" || true
  else
    user="${SLURM_USER:-${USER:-}}"
    if [[ -z "${user}" ]]; then
      echo "ERROR: no job id supplied and USER is not set." >&2
      exit 2
    fi
    squeue --states=PENDING --user="${user}" --format="${queue_format}" || true
  fi
  echo
fi

echo "== pending maintenance-like signals =="
if command -v grep >/dev/null 2>&1; then
  if [[ -n "${job_id}" ]]; then
    squeue --jobs="${job_id}" --format="${queue_format}" \
      | grep -Ei "ReqNodeNotAvail|PartitionDown|PartitionInactive|Reservation|Unavailable|Drain|Draining|Down|Maintenance|Maint|Reserved" \
      || true
  elif [[ "${SHOW_ALL_PENDING:-0}" == "1" ]]; then
    squeue --states=PENDING --format="${queue_format}" \
      | grep -Ei "ReqNodeNotAvail|PartitionDown|PartitionInactive|Reservation|Unavailable|Drain|Draining|Down|Maintenance|Maint|Reserved" \
      || true
  else
    squeue --states=PENDING --user="${SLURM_USER:-${USER:-}}" --format="${queue_format}" \
      | grep -Ei "ReqNodeNotAvail|PartitionDown|PartitionInactive|Reservation|Unavailable|Drain|Draining|Down|Maintenance|Maint|Reserved" \
      || true
  fi
else
  echo "grep is not available; inspect the squeue reason field manually."
fi

echo
echo "== partition and node state summary =="
if [[ -n "${partition}" ]]; then
  sinfo --partition="${partition}" --format="${sinfo_format}" || true
else
  sinfo --format="${sinfo_format}" || true
fi

echo
echo "== unavailable node reasons =="
if [[ -n "${partition}" ]]; then
  sinfo --partition="${partition}" --list-reasons || true
else
  sinfo --list-reasons || true
fi

if command -v scontrol >/dev/null 2>&1; then
  if [[ -n "${node_name}" ]]; then
    echo
    echo "== scontrol node details =="
    scontrol show node "${node_name}" || true
  fi

  echo
  echo "== scontrol reservation details =="
  if [[ -n "${reservation}" ]]; then
    scontrol show reservation "${reservation}" || true
  else
    scontrol show reservation || true
  fi
else
  echo
  echo "== scontrol details =="
  echo "scontrol is not available on this system."
fi

cat <<'PROMPTS'

== review prompts ==
- If squeue shows ReqNodeNotAvail, PartitionDown, or Reservation, compare the requested partition, nodes, features, time limit, and reservation field with sinfo and scontrol output.
- If sinfo -R lists maintenance, reservation, drain, or down reasons, check public site status pages or support notices before changing the job script.
- If only one constraint, GPU type, or node list is affected, consider whether the job is pinned to unavailable resources.
- If the job is eligible but waits for Priority or Resources without maintenance-like reasons, use the general Slurm pending reason triage skill.
- Redact private users, accounts, node names, job names, and maintenance text before posting output publicly.
PROMPTS
