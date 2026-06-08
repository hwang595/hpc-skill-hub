#!/usr/bin/env bash
set -euo pipefail

run_dir="${1:-}"

if [ -z "${run_dir}" ]; then
  echo "Usage: CONFIRM_DELETE=1 bash cleanup-run.sh <run-dir>" >&2
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
  */ior-mdtest-smoke/*|*/ior-mdtest-smoke)
    ;;
  *)
    echo "Refusing to delete a path outside an ior-mdtest-smoke directory." >&2
    exit 1
    ;;
esac

if [ ! -f "${run_dir}/.hpc-skill-ior-mdtest-smoke" ]; then
  echo "Refusing to delete because marker file is missing." >&2
  exit 1
fi

echo "Deleting marked benchmark run directory: ${run_dir}"
rm -rf -- "${run_dir}"
