#!/usr/bin/env bash
set -euo pipefail

file_manifest="${1:-examples/files.txt}"
output_manifest="${2:-checksums/sha256-manifest.txt}"

if [ ! -f "${file_manifest}" ]; then
  echo "usage: create-checksums.sh <file-list> [output-manifest]"
  echo "error: '${file_manifest}' does not exist"
  exit 2
fi

mkdir -p "$(dirname "${output_manifest}")"

if command -v sha256sum >/dev/null 2>&1; then
  checksum_cmd="sha256sum"
  algorithm="sha256"
elif command -v shasum >/dev/null 2>&1; then
  checksum_cmd="shasum -a 256"
  algorithm="sha256"
else
  checksum_cmd="cksum"
  algorithm="cksum"
fi

{
  echo "# created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# algorithm=${algorithm}"
  echo "# source_manifest=${file_manifest}"
} > "${output_manifest}"

while IFS= read -r path; do
  case "${path}" in
    ""|\#*) continue ;;
  esac
  if [ -f "${path}" ]; then
    ${checksum_cmd} "${path}" >> "${output_manifest}"
  else
    echo "MISSING  ${path}" >> "${output_manifest}"
  fi
done < "${file_manifest}"

echo "checksum_manifest=${output_manifest}"
