#!/usr/bin/env bash
set -euo pipefail

job_id="${1:-${JOB_ID:-}}"
log_file="${2:-${JOB_LOG:-}}"
node_name="${NODE_NAME:-}"
timestamp="$(date +%Y%m%d-%H%M%S 2>/dev/null || printf unknown-time)"
safe_job_id="${job_id:-manual}"
report_dir="${REPORT_DIR:-slurm-node-failure-triage-${safe_job_id}-${timestamp}}"

if [ -z "${job_id}" ] && [ -z "${node_name}" ] && [ -z "${log_file}" ]; then
  echo "usage: slurm-node-failure-triage.sh [job-id] [log-file]"
  echo "       JOB_ID=<job-id> NODE_NAME=<node> JOB_LOG=<log-file> REPORT_DIR=<dir> slurm-node-failure-triage.sh"
  exit 2
fi

mkdir -p "${report_dir}"

summary="${report_dir}/summary.md"
accounting="${report_dir}/sacct-accounting.txt"
job_record="${report_dir}/scontrol-job.txt"
queue_record="${report_dir}/squeue-job.txt"
node_reasons="${report_dir}/sinfo-node-reasons.txt"
node_state="${report_dir}/sinfo-node-state.txt"
node_record="${report_dir}/scontrol-node.txt"
log_tail="${report_dir}/log-tail.txt"
log_signals="${report_dir}/log-node-signals.txt"

{
  echo "# Slurm Node Failure Triage"
  echo
  echo "- Job id: ${job_id:-not provided}"
  echo "- Node scope: ${node_name:-not provided}"
  echo "- Log file: ${log_file:-not provided}"
  echo "- Report directory: ${report_dir}"
  echo "- Created: ${timestamp}"
  echo
  echo "## Evidence Files"
  echo
  echo "- sacct accounting: $(basename "${accounting}")"
  echo "- scontrol job record: $(basename "${job_record}")"
  echo "- squeue job record: $(basename "${queue_record}")"
  echo "- sinfo node reasons: $(basename "${node_reasons}")"
  echo "- sinfo node state: $(basename "${node_state}")"
  echo "- scontrol node record: $(basename "${node_record}")"
  echo "- log tail: $(basename "${log_tail}")"
  echo "- log node-failure signals: $(basename "${log_signals}")"
  echo
  echo "## Review Prompts"
  echo
  echo "- Check all job steps, not only the top-level job row."
  echo "- Compare State, ExitCode, NodeList, NNodes, Partition, BatchHost, and elapsed time."
  echo "- Treat NODE_FAIL and BOOT_FAIL as support-handoff evidence unless the site documents a user action."
  echo "- For arrays, compare failed task ids, node lists, input sizes, and retry history."
  echo "- If multiple jobs failed on the same node or reason, avoid repeated large retries until support reviews it."
  echo "- Redact node names, user names, accounts, paths, and scheduler reason strings before public sharing."
} > "${summary}"

if [ -n "${job_id}" ]; then
  if command -v sacct >/dev/null 2>&1; then
    sacct -j "${job_id}" \
      --format=JobID,JobName%40,Partition,State,ExitCode,Elapsed,Timelimit,Submit,Start,End,NNodes,NodeList%60,ReqTRES,AllocTRES \
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

if command -v sinfo >/dev/null 2>&1; then
  sinfo --list-reasons > "${node_reasons}" 2>&1 || true
  if [ -n "${node_name}" ]; then
    sinfo -N -n "${node_name}" -l > "${node_state}" 2>&1 || true
  else
    sinfo -N -l > "${node_state}" 2>&1 || true
  fi
else
  echo "sinfo command not found on PATH." > "${node_reasons}"
  echo "sinfo command not found on PATH." > "${node_state}"
fi

if [ -n "${node_name}" ]; then
  if command -v scontrol >/dev/null 2>&1; then
    scontrol show node "${node_name}" > "${node_record}" 2>&1 || true
  else
    echo "scontrol command not found on PATH." > "${node_record}"
  fi
else
  echo "No node name provided. Use NODE_NAME=<node> for a scoped node record." > "${node_record}"
fi

if [ -n "${log_file}" ] && [ -f "${log_file}" ]; then
  if command -v tail >/dev/null 2>&1; then
    tail -n 200 "${log_file}" > "${log_tail}" 2>&1 || true
  else
    echo "tail command not found on PATH." > "${log_tail}"
  fi

  if command -v grep >/dev/null 2>&1; then
    grep -Ein \
      "node.?fail|node failure|boot.?fail|launch failed|batch host|nodelist|not responding|unreachable|lost|terminated on node|task.*failed|slurmstepd|slurmd|communication|connection|network|fabric|mpi.*abort|pmix|ucx|ofi|filesystem|i/o error|input/output error|stale file|gpu.*lost|xid|requeue" \
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
Slurm node-failure triage report written to ${report_dir}

Start with:
  ${summary}

Evidence files:
  ${accounting}
  ${job_record}
  ${queue_record}
  ${node_reasons}
  ${node_state}
  ${node_record}
  ${log_tail}
  ${log_signals}
EOF
