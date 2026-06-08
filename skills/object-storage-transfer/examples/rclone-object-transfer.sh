#!/usr/bin/env bash
set -euo pipefail

source_uri="${1:-}"
destination_uri="${2:-}"
record_dir="${OBJECT_TRANSFER_RECORD_DIR:-object-transfer-record}"
mode="${OBJECT_TRANSFER_MODE:-copy}"

if [ -z "${source_uri}" ] || [ -z "${destination_uri}" ]; then
  echo "usage: rclone-object-transfer.sh <source-uri> <destination-uri>"
  exit 2
fi

case "${mode}" in
  copy|sync)
    ;;
  *)
    echo "OBJECT_TRANSFER_MODE must be copy or sync"
    exit 2
    ;;
esac

if [ "${mode}" = "sync" ] && [ "${RUN_OBJECT_TRANSFER:-0}" = "1" ] && [ "${ALLOW_OBJECT_SYNC_DELETE:-0}" != "1" ]; then
  echo "sync can delete destination objects; set ALLOW_OBJECT_SYNC_DELETE=1 after reviewing the dry run"
  exit 2
fi

mkdir -p "${record_dir}"
timestamp="$(date -u +%Y%m%d-%H%M%S)"
log_file="${record_dir}/rclone-${mode}-${timestamp}.log"
combined_report="${record_dir}/rclone-${mode}-${timestamp}.combined"
error_report="${record_dir}/rclone-${mode}-${timestamp}.errors"
check_log="${record_dir}/rclone-check-${timestamp}.log"

rclone_args=(
  "${mode}"
  "${source_uri}"
  "${destination_uri}"
  --stats=30s
  --stats-one-line
  --transfers "${RCLONE_TRANSFERS:-4}"
  --checkers "${RCLONE_CHECKERS:-8}"
  --combined "${combined_report}"
  --error "${error_report}"
)

if [ "${RUN_OBJECT_TRANSFER:-0}" != "1" ]; then
  rclone_args+=(--dry-run)
fi

if [ "${RCLONE_CHECKSUM:-0}" = "1" ]; then
  rclone_args+=(--checksum)
fi

if [ -n "${RCLONE_BWLIMIT:-}" ]; then
  rclone_args+=(--bwlimit "${RCLONE_BWLIMIT}")
fi

if [ -n "${RCLONE_MAX_TRANSFER:-}" ]; then
  rclone_args+=(--max-transfer "${RCLONE_MAX_TRANSFER}")
fi

if [ -n "${RCLONE_FILTER_FILE:-}" ]; then
  rclone_args+=(--filter-from "${RCLONE_FILTER_FILE}")
fi

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "source_uri=${source_uri}"
  echo "destination_uri=${destination_uri}"
  echo "OBJECT_TRANSFER_MODE=${mode}"
  echo "RUN_OBJECT_TRANSFER=${RUN_OBJECT_TRANSFER:-0}"
  echo "ALLOW_OBJECT_SYNC_DELETE=${ALLOW_OBJECT_SYNC_DELETE:-0}"
  echo "RCLONE_TRANSFERS=${RCLONE_TRANSFERS:-4}"
  echo "RCLONE_CHECKERS=${RCLONE_CHECKERS:-8}"
  echo "RCLONE_BWLIMIT=${RCLONE_BWLIMIT:-}"
  echo "RCLONE_MAX_TRANSFER=${RCLONE_MAX_TRANSFER:-}"
  echo "RCLONE_FILTER_FILE=${RCLONE_FILTER_FILE:-}"
  echo "combined_report=${combined_report}"
  echo "error_report=${error_report}"
  echo
  rclone version || true
  echo
  printf 'command='
  printf '%q ' rclone "${rclone_args[@]}"
  echo
  echo
} > "${log_file}"

rclone "${rclone_args[@]}" 2>&1 | tee -a "${log_file}"

if [ "${RUN_OBJECT_TRANSFER:-0}" = "1" ] && [ "${RUN_OBJECT_CHECK:-0}" = "1" ]; then
  {
    echo
    echo "== rclone check =="
    printf 'command='
    printf '%q ' rclone check "${source_uri}" "${destination_uri}"
    echo
    rclone check "${source_uri}" "${destination_uri}"
  } 2>&1 | tee -a "${check_log}"
fi

echo "log=${log_file}"
echo "combined_report=${combined_report}"
echo "error_report=${error_report}"
if [ "${RUN_OBJECT_TRANSFER:-0}" != "1" ]; then
  echo "dry_run=true"
  echo "Set RUN_OBJECT_TRANSFER=1 only after reviewing the log."
fi
if [ "${RUN_OBJECT_TRANSFER:-0}" = "1" ] && [ "${RUN_OBJECT_CHECK:-0}" = "1" ]; then
  echo "check_log=${check_log}"
fi
