#!/usr/bin/env bash
set -euo pipefail

script_path="${1:-}"

if [ -z "${script_path}" ] || [ ! -f "${script_path}" ]; then
  echo "usage: review-sbatch.sh <sbatch-script>" >&2
  exit 2
fi

echo "== shell syntax =="
bash -n "${script_path}"
echo "pass"

echo
echo "== Slurm directives =="
grep -En '^#SBATCH[[:space:]]' "${script_path}" || {
  echo "error: no #SBATCH directives found" >&2
  exit 2
}

echo
echo "== unresolved placeholders =="
if grep -En '<[^>]+>' "${script_path}"; then
  echo "review blocked: replace every placeholder with an approved local value" >&2
  exit 3
fi

echo "none"
echo "static review passed; no job was submitted"
