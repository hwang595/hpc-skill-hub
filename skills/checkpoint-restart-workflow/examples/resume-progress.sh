#!/usr/bin/env bash
set -euo pipefail

checkpoint_dir="${1:-checkpoints/demo}"
target_steps="${2:-5}"
state_file="${checkpoint_dir}/progress.txt"
complete_file="${checkpoint_dir}/complete.txt"

mkdir -p "${checkpoint_dir}"

if [ -f "${complete_file}" ]; then
  echo "already_complete=true"
  cat "${complete_file}"
  exit 0
fi

if [ -f "${state_file}" ]; then
  current_step="$(cat "${state_file}")"
  echo "resume_from_step=${current_step}"
else
  current_step="0"
  echo "resume_from_step=0"
fi

while [ "${current_step}" -lt "${target_steps}" ]; do
  current_step="$((current_step + 1))"
  echo "${current_step}" > "${state_file}"
  echo "completed_step=${current_step}"
  sleep 1
done

{
  echo "completed_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "steps=${target_steps}"
} > "${complete_file}"

echo "complete=true"
