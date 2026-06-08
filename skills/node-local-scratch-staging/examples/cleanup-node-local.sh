#!/usr/bin/env bash
set -euo pipefail

run_dir="${1:-}"
marker_name=".hpc-skill-node-local-scratch"

if [ -z "${run_dir}" ]; then
  echo "Usage: CONFIRM_DELETE=1 bash cleanup-node-local.sh <node-local-run-dir>" >&2
  exit 2
fi

if [ "${CONFIRM_DELETE:-0}" != "1" ]; then
  echo "Refusing to delete without CONFIRM_DELETE=1." >&2
  exit 2
fi

if [ ! -d "${run_dir}" ]; then
  echo "Not a directory: ${run_dir}" >&2
  exit 1
fi

case "${run_dir}" in
  */hpc-skill-node-local-*)
    ;;
  *)
    echo "Refusing to delete a path outside a hpc-skill-node-local directory." >&2
    exit 1
    ;;
esac

if [ ! -f "${run_dir}/${marker_name}" ]; then
  echo "Refusing to delete because marker file is missing." >&2
  exit 1
fi

echo "Deleting marked node-local run directory: ${run_dir}"
rm -rf -- "${run_dir}"
