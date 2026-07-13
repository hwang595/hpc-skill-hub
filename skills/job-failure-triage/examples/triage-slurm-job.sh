#!/usr/bin/env bash
set -euo pipefail

job_id=""
log_file=""

case "$#" in
  1)
    log_file="$1"
    ;;
  2)
    job_id="$1"
    log_file="$2"
    ;;
  *)
    echo "usage: triage-slurm-job.sh [job-id] <log-file>" >&2
    exit 2
    ;;
esac

if [ -n "${job_id}" ]; then
  echo "== accounting =="
  if command -v sacct >/dev/null 2>&1; then
    sacct -j "${job_id}" --format=JobID,JobName%30,State,ExitCode,Elapsed,ReqMem,MaxRSS -P || true
  else
    echo "sacct unavailable; accounting evidence not collected"
  fi
  echo

  echo "== job details =="
  if command -v scontrol >/dev/null 2>&1; then
    scontrol show job "${job_id}" || true
  else
    echo "scontrol unavailable; job details not collected"
  fi
  echo
fi

if [ ! -f "${log_file}" ]; then
  echo "error: log file not found: ${log_file}" >&2
  exit 2
fi

echo "== last log lines =="
tail -n 80 "${log_file}"

echo
echo "== common failure clues =="
grep -Ein "out.of.memory|oom|killed|time.?limit|permission denied|no such file|command not found|module|cuda|rocm|mpi|segmentation fault|traceback|error" "${log_file}" || true
