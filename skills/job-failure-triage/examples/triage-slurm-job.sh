#!/usr/bin/env bash
set -euo pipefail

job_id="${1:-}"
log_file="${2:-}"

if [ -n "${job_id}" ]; then
  echo "== accounting =="
  sacct -j "${job_id}" --format=JobID,JobName%30,State,ExitCode,Elapsed,ReqMem,MaxRSS -P || true
  echo
fi

if [ -z "${log_file}" ] || [ ! -f "${log_file}" ]; then
  echo "usage: triage-slurm-job.sh [job-id] <log-file>"
  exit 2
fi

echo "== last log lines =="
tail -n 80 "${log_file}"

echo
echo "== common failure clues =="
grep -Ein "out.of.memory|oom|killed|time.?limit|permission denied|no such file|command not found|module|cuda|rocm|mpi|segmentation fault|traceback|error" "${log_file}" || true
