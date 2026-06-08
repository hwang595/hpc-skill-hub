#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: profile-command.sh <command> [args...]"
  exit 2
fi

stamp="$(date +%Y%m%d-%H%M%S)"
outdir="${PROFILE_DIR:-profile-${stamp}}"
mkdir -p "${outdir}"

printf "%q " "$@" > "${outdir}/command.txt"
printf "\n" >> "${outdir}/command.txt"
env | sort > "${outdir}/environment.txt"

if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=timestamp,index,name,utilization.gpu,memory.used,memory.total --format=csv -l 5 > "${outdir}/nvidia-smi.csv" &
  gpu_pid="$!"
else
  gpu_pid=""
fi

set +e
if [ -x /usr/bin/time ]; then
  /usr/bin/time -v "$@" > "${outdir}/stdout.log" 2> "${outdir}/stderr-and-time.log"
else
  time "$@" > "${outdir}/stdout.log" 2> "${outdir}/stderr-and-time.log"
fi
exit_code="$?"
set -e

if [ -n "${gpu_pid}" ]; then
  kill "${gpu_pid}" >/dev/null 2>&1 || true
fi

echo "${exit_code}" > "${outdir}/exit-code.txt"
echo "profile_dir=${outdir}"
exit "${exit_code}"
