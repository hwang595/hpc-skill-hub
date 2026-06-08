#!/usr/bin/env bash
set -euo pipefail

source_uri="${1:-}"
destination_uri="${2:-}"
record_dir="${AWS_S3_SYNC_RECORD_DIR:-aws-s3-sync-record}"

if [ -z "${source_uri}" ] || [ -z "${destination_uri}" ]; then
  echo "usage: aws-s3-sync-plan.sh <source-uri> <destination-uri>"
  exit 2
fi

mkdir -p "${record_dir}"
timestamp="$(date -u +%Y%m%d-%H%M%S)"
log_file="${record_dir}/aws-s3-sync-${timestamp}.log"

aws_args=(
  s3
  sync
  "${source_uri}"
  "${destination_uri}"
  --no-progress
)

if [ "${RUN_AWS_S3_SYNC:-0}" != "1" ]; then
  aws_args+=(--dryrun)
fi

if [ -n "${AWS_S3_EXCLUDE:-}" ]; then
  aws_args+=(--exclude "${AWS_S3_EXCLUDE}")
fi

if [ -n "${AWS_S3_INCLUDE:-}" ]; then
  aws_args+=(--include "${AWS_S3_INCLUDE}")
fi

if [ -n "${AWS_PROFILE:-}" ]; then
  aws_args+=(--profile "${AWS_PROFILE}")
fi

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "source_uri=${source_uri}"
  echo "destination_uri=${destination_uri}"
  echo "RUN_AWS_S3_SYNC=${RUN_AWS_S3_SYNC:-0}"
  echo "AWS_PROFILE=${AWS_PROFILE:-}"
  echo "AWS_S3_EXCLUDE=${AWS_S3_EXCLUDE:-}"
  echo "AWS_S3_INCLUDE=${AWS_S3_INCLUDE:-}"
  echo
  aws --version || true
  echo
  printf 'command='
  printf '%q ' aws "${aws_args[@]}"
  echo
  echo
} > "${log_file}"

aws "${aws_args[@]}" 2>&1 | tee -a "${log_file}"

echo "log=${log_file}"
if [ "${RUN_AWS_S3_SYNC:-0}" != "1" ]; then
  echo "dry_run=true"
  echo "Set RUN_AWS_S3_SYNC=1 only after reviewing the log."
fi
