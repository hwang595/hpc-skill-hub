#!/usr/bin/env bash
set -euo pipefail

definition_file="${1:-examples/Container.def}"
output_image="${2:-hpc-skill-example.sif}"
record_dir="${BUILD_RECORD_DIR:-container-build-record}"

mkdir -p "${record_dir}"
record="${record_dir}/build-plan.txt"

if [ ! -f "${definition_file}" ]; then
  echo "usage: build-plan.sh <definition-file> <output-image>"
  echo "error: '${definition_file}' does not exist"
  exit 2
fi

if command -v apptainer >/dev/null 2>&1; then
  runtime="apptainer"
elif command -v singularity >/dev/null 2>&1; then
  runtime="singularity"
else
  runtime=""
fi

{
  echo "captured_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "definition_file=${definition_file}"
  echo "output_image=${output_image}"
  echo "runtime=${runtime:-not-found}"
  echo "BUILD_IMAGE=${BUILD_IMAGE:-0}"
  echo
  echo "planned_command=${runtime:-apptainer} build ${output_image} ${definition_file}"
} > "${record}"

if [ "${BUILD_IMAGE:-0}" = "1" ]; then
  if [ -z "${runtime}" ]; then
    echo "No apptainer or singularity command found."
    exit 2
  fi
  "${runtime}" build "${output_image}" "${definition_file}" 2>&1 | tee "${record_dir}/build.log"
else
  echo "Plan-only mode. Set BUILD_IMAGE=1 to run the recorded build command."
fi

echo "record=${record}"
