#!/usr/bin/env bash
set -euo pipefail

job_id="${1:?usage: monitor-job.sh <job-id>}"

echo "== queue =="
squeue -j "${job_id}" -o "%.18i %.9P %.30j %.8u %.2t %.10M %.10l %.6D %R" || true

echo
echo "== accounting =="
sacct -j "${job_id}" --format=JobID,JobName%30,State,ExitCode,Elapsed,Timelimit,AllocCPUS,ReqMem,MaxRSS -P || true

echo
echo "== controller =="
scontrol show job "${job_id}" || true
