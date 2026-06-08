#!/usr/bin/env bash
set -euo pipefail

source_path="${1:-}"
archive_stem="${2:-hpc-archive-$(date -u +%Y%m%d-%H%M%S)}"
record_dir="${ARCHIVE_RECORD_DIR:-archive-record}"
archive_path="${ARCHIVE_PATH:-${archive_stem}.tar.gz}"

if [ -z "${source_path}" ] || [ ! -e "${source_path}" ]; then
  echo "usage: prepare-archive.sh <source-path> [archive-stem]"
  echo "error: source path must exist"
  exit 2
fi

case "${archive_stem}" in
  */*)
    echo "error: archive-stem must not contain '/'; set ARCHIVE_PATH for custom output paths"
    exit 2
    ;;
esac

mkdir -p "${record_dir}"
record_dir_abs="$(cd "${record_dir}" && pwd)"
source_parent="$(cd "$(dirname "${source_path}")" && pwd)"
source_base="$(basename "${source_path}")"

manifest="${record_dir_abs}/${archive_stem}-files.txt"
summary="${record_dir_abs}/${archive_stem}-summary.txt"
plan="${record_dir_abs}/${archive_stem}-archive-plan.txt"

(
  cd "${source_parent}"
  if [ -f "${source_base}" ]; then
    printf '%s\n' "${source_base}" > "${manifest}"
  else
    find "${source_base}" -type f | sort > "${manifest}"
  fi
)

file_count="$(wc -l < "${manifest}" | tr -d ' ')"
size_summary="$(du -sh "${source_path}" | awk '{print $1}')"

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "source_path=${source_path}"
  echo "source_parent=${source_parent}"
  echo "source_base=${source_base}"
  echo "file_manifest=${manifest}"
  echo "file_count=${file_count}"
  echo "size_summary=${size_summary}"
  echo "archive_path=${archive_path}"
  echo "CREATE_ARCHIVE=${CREATE_ARCHIVE:-0}"
} | tee "${summary}"

{
  echo "# Review this plan before creating an archive."
  echo "# Exclude scratch files, caches, private data, and intermediate outputs first."
  echo "tar -czf \"${archive_path}\" -C \"${source_parent}\" -T \"${manifest}\""
  echo
  echo "Recommended next step:"
  echo "CREATE_ARCHIVE=1 bash examples/prepare-archive.sh \"${source_path}\" \"${archive_stem}\""
} > "${plan}"

if [ "${CREATE_ARCHIVE:-0}" = "1" ]; then
  tar -czf "${archive_path}" -C "${source_parent}" -T "${manifest}"
  echo "archive_created=${archive_path}"
else
  echo "dry_run=true"
  echo "archive_plan=${plan}"
  echo "Set CREATE_ARCHIVE=1 only after reviewing the manifest and plan."
fi
