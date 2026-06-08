#!/usr/bin/env bash
set -euo pipefail

source_path="${1:-}"
destination_path="${2:-}"
record_dir="${RSYNC_RECORD_DIR:-rsync-record}"

if [ -z "${source_path}" ] || [ -z "${destination_path}" ]; then
  echo "usage: rsync-plan.sh <source-path> <destination-path>"
  exit 2
fi

mkdir -p "${record_dir}"
log_file="${record_dir}/rsync-$(date -u +%Y%m%d-%H%M%S).log"

rsync_args=(
  -avh
  --partial
  --info=progress2
)

if [ "${RUN_TRANSFER:-0}" != "1" ]; then
  rsync_args+=(--dry-run)
fi

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "source_path=${source_path}"
  echo "destination_path=${destination_path}"
  echo "RUN_TRANSFER=${RUN_TRANSFER:-0}"
  echo "command=rsync ${rsync_args[*]} ${source_path} ${destination_path}"
  echo
} > "${log_file}"

rsync "${rsync_args[@]}" "${source_path}" "${destination_path}" 2>&1 | tee -a "${log_file}"

echo "log=${log_file}"
if [ "${RUN_TRANSFER:-0}" != "1" ]; then
  echo "dry_run=true"
  echo "Set RUN_TRANSFER=1 only after reviewing the log."
fi
