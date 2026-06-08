#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: slurm-efficiency-report.sh <job-id>

Collect read-only Slurm accounting evidence for one completed job.
The job id may be a plain job id, array task id, or job step id.
USAGE
}

job_id="${1:-}"
if [[ -z "${job_id}" || "${job_id}" == "-h" || "${job_id}" == "--help" ]]; then
  usage
  exit 2
fi

if ! [[ "${job_id}" =~ ^[A-Za-z0-9_.+-]+$ ]]; then
  echo "ERROR: job id contains unexpected characters: ${job_id}" >&2
  exit 2
fi

echo "Slurm efficiency report"
echo "======================="
echo "Job id: ${job_id}"
echo

if command -v seff >/dev/null 2>&1; then
  echo "== seff summary =="
  if ! seff "${job_id}"; then
    echo "WARN: seff did not return a report for ${job_id}." >&2
  fi
  echo
else
  echo "== seff summary =="
  echo "seff is not available on this system; using sacct only."
  echo
fi

if ! command -v sacct >/dev/null 2>&1; then
  echo "ERROR: sacct is required for the accounting table." >&2
  exit 1
fi

echo "== sacct accounting table =="
sacct \
  --jobs="${job_id}" \
  --format=JobID,JobName%40,State,ExitCode,Elapsed,Timelimit,AllocCPUS,ReqMem,MaxRSS,TotalCPU,NCPUS,NNodes \
  --units=M \
  --parsable2

cat <<'NOTES'

== review prompts ==
- Compare Elapsed with Timelimit before increasing or decreasing wall time.
- Compare MaxRSS with ReqMem before changing memory requests.
- Compare TotalCPU with Elapsed * AllocCPUS when judging CPU efficiency.
- Review failed, timed out, or out-of-memory states before reusing requests.
- Use application logs or site GPU telemetry for GPU utilization questions.
NOTES
