#!/usr/bin/env bash
set -euo pipefail

job_id="${1:-${JOB_ID:-}}"
log_file="${2:-${JOB_LOG:-}}"
timestamp="$(date +%Y%m%d-%H%M%S 2>/dev/null || printf unknown-time)"
safe_job_id="${job_id:-manual}"
report_dir="${REPORT_DIR:-slurm-time-limit-triage-${safe_job_id}-${timestamp}}"

if [ -z "${job_id}" ] && [ -z "${log_file}" ]; then
  echo "usage: slurm-time-limit-triage.sh [job-id] [log-file]"
  echo "       JOB_ID=<job-id> JOB_LOG=<log-file> REPORT_DIR=<dir> slurm-time-limit-triage.sh"
  exit 2
fi

mkdir -p "${report_dir}"

summary="${report_dir}/summary.md"
accounting="${report_dir}/sacct-accounting.txt"
job_record="${report_dir}/scontrol-job.txt"
efficiency="${report_dir}/seff.txt"
log_tail="${report_dir}/log-tail.txt"
log_signals="${report_dir}/log-time-signals.txt"

{
  echo "# Slurm Time Limit Triage"
  echo
  echo "- Job id: ${job_id:-not provided}"
  echo "- Log file: ${log_file:-not provided}"
  echo "- Report directory: ${report_dir}"
  echo "- Created: ${timestamp}"
  echo
  echo "## Evidence Files"
  echo
  echo "- sacct accounting: $(basename "${accounting}")"
  echo "- scontrol job record: $(basename "${job_record}")"
  echo "- seff summary: $(basename "${efficiency}")"
  echo "- log tail: $(basename "${log_tail}")"
  echo "- log time-limit signals: $(basename "${log_signals}")"
  echo
  echo "## Review Prompts"
  echo
  echo "- Compare Elapsed with Timelimit for the job and each visible step."
  echo "- Inspect State and ExitCode together; TIMEOUT may be paired with termination signals."
  echo "- Compare Submit, Start, and End before attributing delays to application runtime."
  echo "- For arrays, compare timed-out task ids with input sizes and completed task runtimes."
  echo "- Look for checkpoint, restart, signal, cleanup, flush, or partial-output messages in logs."
  echo "- Treat changing TimeLimit as a site-policy and queue-choice decision, not only a script edit."
} > "${summary}"

if [ -n "${job_id}" ]; then
  if command -v sacct >/dev/null 2>&1; then
    sacct -j "${job_id}" \
      --format=JobID,JobName%40,Partition,State,ExitCode,Elapsed,Timelimit,Submit,Start,End,AllocCPUS,NTasks,NNodes,NodeList%40,ReqTRES,AllocTRES \
      --parsable2 > "${accounting}" 2>&1 || true
  else
    echo "sacct command not found on PATH." > "${accounting}"
  fi

  if command -v scontrol >/dev/null 2>&1; then
    scontrol show job "${job_id}" > "${job_record}" 2>&1 || true
  else
    echo "scontrol command not found on PATH." > "${job_record}"
  fi

  if command -v seff >/dev/null 2>&1; then
    seff "${job_id}" > "${efficiency}" 2>&1 || true
  else
    echo "seff command not found on PATH." > "${efficiency}"
  fi
else
  echo "No job id provided." > "${accounting}"
  echo "No job id provided." > "${job_record}"
  echo "No job id provided." > "${efficiency}"
fi

if [ -n "${log_file}" ] && [ -f "${log_file}" ]; then
  if command -v tail >/dev/null 2>&1; then
    tail -n 200 "${log_file}" > "${log_tail}" 2>&1 || true
  else
    echo "tail command not found on PATH." > "${log_tail}"
  fi

  if command -v grep >/dev/null 2>&1; then
    grep -Ein \
      "time.?limit|wall.?time|timeout|timed out|cancelled|canceled|signal|sigterm|sigkill|term|kill|checkpoint|restart|requeue|cleanup|graceful|flush|partial|preempt|deadline|stopping|shutting down" \
      "${log_file}" > "${log_signals}" 2>&1 || true
  else
    echo "grep command not found on PATH." > "${log_signals}"
  fi
elif [ -n "${log_file}" ]; then
  echo "Log file not found: ${log_file}" > "${log_tail}"
  echo "Log file not found: ${log_file}" > "${log_signals}"
else
  echo "No log file provided." > "${log_tail}"
  echo "No log file provided." > "${log_signals}"
fi

cat <<EOF
Slurm time-limit triage report written to ${report_dir}

Start with:
  ${summary}

Evidence files:
  ${accounting}
  ${job_record}
  ${efficiency}
  ${log_tail}
  ${log_signals}
EOF
