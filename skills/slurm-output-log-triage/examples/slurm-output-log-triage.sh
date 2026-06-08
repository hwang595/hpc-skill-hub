#!/usr/bin/env bash
set -euo pipefail

job_id="${1:-${JOB_ID:-}}"
log_file="${2:-${JOB_LOG:-${OUTPUT_PATH:-}}}"
error_file="${ERROR_FILE:-}"
timestamp="$(date +%Y%m%d-%H%M%S 2>/dev/null || printf unknown-time)"
safe_job_id="${job_id:-manual}"
report_dir="${REPORT_DIR:-slurm-output-log-triage-${safe_job_id}-${timestamp}}"

if [ -z "${job_id}" ] && [ -z "${log_file}" ] && [ -z "${error_file}" ]; then
  echo "usage: slurm-output-log-triage.sh [job-id] [log-file]"
  echo "       JOB_ID=<job-id> JOB_LOG=<path> ERROR_FILE=<path> REPORT_DIR=<dir> slurm-output-log-triage.sh"
  exit 2
fi

mkdir -p "${report_dir}"

summary="${report_dir}/summary.md"
accounting="${report_dir}/sacct-accounting.txt"
job_record="${report_dir}/scontrol-job.txt"
queue_record="${report_dir}/squeue-job.txt"
path_hints="${report_dir}/path-hints.txt"
path_checks="${report_dir}/path-checks.txt"
log_tail="${report_dir}/log-tail.txt"
log_signals="${report_dir}/log-signals.txt"

record_path() {
  label="$1"
  path="$2"

  {
    echo "## ${label}"
    echo "path=${path}"

    if [ -z "${path}" ]; then
      echo "status=not-provided"
      echo
      return 0
    fi

    parent="$(dirname "${path}")"
    if [ -d "${parent}" ]; then
      echo "parent_exists=yes"
      if command -v ls >/dev/null 2>&1; then
        ls -ld "${parent}" 2>&1 || true
      fi
    else
      echo "parent_exists=no"
      echo "parent=${parent}"
    fi

    if [ -e "${path}" ]; then
      echo "path_exists=yes"
      if command -v ls >/dev/null 2>&1; then
        ls -l "${path}" 2>&1 || true
      fi
      if command -v stat >/dev/null 2>&1; then
        stat "${path}" 2>&1 || true
      fi
      if command -v wc >/dev/null 2>&1; then
        wc -c "${path}" 2>&1 || true
        wc -l "${path}" 2>&1 || true
      fi
    else
      echo "path_exists=no"
    fi
    echo
  } >> "${path_checks}"
}

{
  echo "# Slurm Output Log Triage"
  echo
  echo "- Job id: ${job_id:-not provided}"
  echo "- Log file: ${log_file:-not provided}"
  echo "- Error file: ${error_file:-not provided}"
  echo "- Current directory: $(pwd)"
  echo "- Report directory: ${report_dir}"
  echo "- Created: ${timestamp}"
  echo
  echo "## Evidence Files"
  echo
  echo "- sacct accounting: $(basename "${accounting}")"
  echo "- scontrol job record: $(basename "${job_record}")"
  echo "- squeue job record: $(basename "${queue_record}")"
  echo "- path hints: $(basename "${path_hints}")"
  echo "- path checks: $(basename "${path_checks}")"
  echo "- log tail: $(basename "${log_tail}")"
  echo "- log signals: $(basename "${log_signals}")"
  echo
  echo "## Review Prompts"
  echo
  echo "- Compare StdOut, StdErr, WorkDir, SubmitLine, and the directory where the user searched."
  echo "- Remember that relative output paths are relative to the job working directory."
  echo "- Check whether the parent log directory existed before job launch."
  echo "- If the log exists but is empty, inspect job state, exit code, and whether the script reached the workload command."
  echo "- If stdout and stderr were split, review both paths before deciding the log is missing."
  echo "- Redact private paths, project names, commands, and dataset identifiers before public sharing."
} > "${summary}"

if [ -n "${job_id}" ]; then
  if command -v sacct >/dev/null 2>&1; then
    sacct -j "${job_id}" \
      --format=JobID,JobName%40,State,ExitCode,Submit,Start,End,Elapsed,StdOut%80,StdErr%80,SubmitLine%120 \
      --parsable2 > "${accounting}" 2>&1 || true
  else
    echo "sacct command not found on PATH." > "${accounting}"
  fi

  if command -v scontrol >/dev/null 2>&1; then
    scontrol show job "${job_id}" > "${job_record}" 2>&1 || true
  else
    echo "scontrol command not found on PATH." > "${job_record}"
  fi

  if command -v squeue >/dev/null 2>&1; then
    squeue -j "${job_id}" --format="%.18i %.9P %.40j %.12u %.2t %.10M %.6D %R" > "${queue_record}" 2>&1 || true
  else
    echo "squeue command not found on PATH." > "${queue_record}"
  fi
else
  echo "No job id provided." > "${accounting}"
  echo "No job id provided." > "${job_record}"
  echo "No job id provided." > "${queue_record}"
fi

{
  echo "# Output Path Hints"
  echo
  echo "Current directory: $(pwd)"
  echo "Provided log file: ${log_file:-not provided}"
  echo "Provided error file: ${error_file:-not provided}"
  if [ -n "${job_id}" ]; then
    echo "Default ordinary-job candidate: slurm-${job_id}.out"
    echo "Array default pattern reminder: slurm-%A_%a.out"
  else
    echo "No job id provided, so no default slurm-<jobid>.out candidate was generated."
  fi
  echo
  echo "Accounting and job-record snippets:"
  if command -v grep >/dev/null 2>&1; then
    grep -E "StdOut|StdErr|WorkDir|Command=|SubmitLine|JobState|ExitCode" "${accounting}" "${job_record}" 2>/dev/null || true
  else
    echo "grep command not found on PATH."
  fi
} > "${path_hints}"

: > "${path_checks}"
record_path "provided stdout/log path" "${log_file}"
record_path "provided stderr path" "${error_file}"
if [ -n "${job_id}" ]; then
  record_path "default ordinary-job output candidate" "slurm-${job_id}.out"
fi

if [ -n "${log_file}" ] && [ -f "${log_file}" ]; then
  if command -v tail >/dev/null 2>&1; then
    tail -n 160 "${log_file}" > "${log_tail}" 2>&1 || true
  else
    echo "tail command not found on PATH." > "${log_tail}"
  fi

  if command -v grep >/dev/null 2>&1; then
    grep -Ein \
      "error|failed|no such file|permission denied|quota|disk quota|cannot open|unable to open|directory nonexistent|not found|command not found|module.*not|traceback|segmentation fault|killed|cancelled|canceled|timeout|out.of.memory|oom|input/output error|stale file" \
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
Slurm output-log triage report written to ${report_dir}

Start with:
  ${summary}

Evidence files:
  ${accounting}
  ${job_record}
  ${queue_record}
  ${path_hints}
  ${path_checks}
  ${log_tail}
  ${log_signals}
EOF
