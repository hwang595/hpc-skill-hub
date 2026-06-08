#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: capture-run.sh <command> [args...]"
  exit 2
fi

stamp="$(date -u +%Y%m%d-%H%M%S)"
outdir="${RUN_CAPTURE_DIR:-run-capture-${stamp}}"
mkdir -p "${outdir}"

printf "%q " "$@" > "${outdir}/command.txt"
printf "\n" >> "${outdir}/command.txt"

{
  echo "captured_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "hostname=$(hostname)"
  echo "cwd=$(pwd)"
  uname -a
} > "${outdir}/metadata.txt"

module list > "${outdir}/modules.txt" 2>&1 || true
env | sort > "${outdir}/environment.txt"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  {
    git rev-parse HEAD
    git status --short
  } > "${outdir}/git.txt"
fi

if [ -n "${INPUT_MANIFEST:-}" ] && [ -f "${INPUT_MANIFEST}" ]; then
  while IFS= read -r input_path; do
    case "${input_path}" in
      ""|\#*) continue ;;
    esac
    if [ -f "${input_path}" ]; then
      if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "${input_path}"
      elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "${input_path}"
      else
        cksum "${input_path}"
      fi
    else
      echo "missing ${input_path}"
    fi
  done < "${INPUT_MANIFEST}" > "${outdir}/input-checksums.txt"
fi

set +e
"$@" > "${outdir}/stdout.log" 2> "${outdir}/stderr.log"
exit_code="$?"
set -e

echo "${exit_code}" > "${outdir}/exit-code.txt"
echo "capture_dir=${outdir}"
exit "${exit_code}"
