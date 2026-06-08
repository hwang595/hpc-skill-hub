#!/usr/bin/env bash
set -euo pipefail

array_job_id="${1:-${ARRAY_JOB_ID:-}}"
sbatch_script="${2:-${SBATCH_SCRIPT:-}}"
task_manifest="${TASK_MANIFEST:-}"
manifest_first_task_id="${MANIFEST_FIRST_TASK_ID:-1}"
retry_states="${RETRY_STATES:-FAILED,TIMEOUT,OUT_OF_MEMORY,NODE_FAIL,PREEMPTED,BOOT_FAIL,DEADLINE,CANCELLED}"
retry_concurrency="${RETRY_CONCURRENCY:-}"
sacct_file="${SACCT_FILE:-}"
run_sbatch_retry="${RUN_SBATCH_RETRY:-0}"
timestamp="$(date +%Y%m%d-%H%M%S 2>/dev/null || printf unknown-time)"
report_dir="${REPORT_DIR:-slurm-array-retry-${array_job_id:-manual}-${timestamp}}"

if [ -z "${array_job_id}" ] && [ -z "${sacct_file}" ]; then
  echo "usage: array-retry-plan.sh <array-job-id> [sbatch-script]"
  echo "       SACCT_FILE=<exported-sacct.txt> array-retry-plan.sh <array-job-id> [sbatch-script]"
  exit 2
fi

mkdir -p "${report_dir}"

accounting="${report_dir}/sacct-array.txt"
failed_ids="${report_dir}/failed-task-ids.txt"
array_range_file="${report_dir}/failed-array-range.txt"
failed_manifest="${report_dir}/failed-manifest-lines.tsv"
plan="${report_dir}/retry-plan.md"
submit_log="${report_dir}/sbatch-submit.txt"

if [ -n "${sacct_file}" ]; then
  cp "${sacct_file}" "${accounting}"
elif command -v sacct >/dev/null 2>&1; then
  sacct -j "${array_job_id}" \
    --format=JobID,State,ExitCode,Elapsed,ReqMem,MaxRSS \
    --parsable2 > "${accounting}" 2>&1 || true
else
  echo "sacct command not found and SACCT_FILE was not provided." > "${accounting}"
fi

awk -F'|' -v states="${retry_states}" '
function state_matches(state, parts, count, i) {
  count = split(states, parts, ",")
  for (i = 1; i <= count; i++) {
    if (parts[i] != "" && index(state, parts[i]) > 0) {
      return 1
    }
  }
  return 0
}
function task_id(job, clean, pieces) {
  clean = job
  sub(/\..*/, "", clean)
  if (clean ~ /^[0-9]+_[0-9]+$/) {
    split(clean, pieces, "_")
    return pieces[2]
  }
  return ""
}
NR == 1 && $1 ~ /^JobID/ { next }
{
  task = task_id($1)
  if (task != "" && state_matches($2)) {
    print task
  }
}
' "${accounting}" | sort -n -u > "${failed_ids}"

awk '
BEGIN {
  first = ""
  prev = ""
  sep = ""
}
{
  if ($1 == "") {
    next
  }
  if (first == "") {
    first = $1
    prev = $1
    next
  }
  if ($1 == prev + 1) {
    prev = $1
    next
  }
  printf "%s%s", sep, (first == prev ? first : first "-" prev)
  sep = ","
  first = $1
  prev = $1
}
END {
  if (first != "") {
    printf "%s%s\n", sep, (first == prev ? first : first "-" prev)
  } else {
    printf "\n"
  }
}
' "${failed_ids}" > "${array_range_file}"

array_range="$(cat "${array_range_file}")"

if [ -n "${task_manifest}" ] && [ -f "${task_manifest}" ]; then
  awk -v first_task="${manifest_first_task_id}" '
    NR == FNR {
      line = $1 - first_task + 1
      if (line > 0) {
        wanted[line] = $1
      }
      next
    }
    FNR in wanted {
      print wanted[FNR] "\t" $0
    }
  ' "${failed_ids}" "${task_manifest}" > "${failed_manifest}"
else
  {
    if [ -n "${task_manifest}" ]; then
      echo "Manifest not found: ${task_manifest}"
    else
      echo "No TASK_MANIFEST provided."
    fi
  } > "${failed_manifest}"
fi

cap=""
if [ -n "${retry_concurrency}" ]; then
  case "${retry_concurrency}" in
    %*) cap="${retry_concurrency}" ;;
    *) cap="%${retry_concurrency}" ;;
  esac
fi

retry_array_arg=""
retry_command=""
if [ -n "${array_range}" ] && [ -n "${sbatch_script}" ]; then
  retry_array_arg="${array_range}${cap}"
  retry_command="sbatch --array=${retry_array_arg} ${sbatch_script}"
fi

{
  echo "# Slurm Array Retry Plan"
  echo
  echo "- Original array job id: ${array_job_id:-not provided}"
  echo "- Retry states: ${retry_states}"
  echo "- Retry concurrency cap: ${retry_concurrency:-not set}"
  echo "- Sbatch script: ${sbatch_script:-not provided}"
  echo "- Task manifest: ${task_manifest:-not provided}"
  echo "- Report directory: ${report_dir}"
  echo
  echo "## Evidence Files"
  echo
  echo "- Accounting: $(basename "${accounting}")"
  echo "- Failed task ids: $(basename "${failed_ids}")"
  echo "- Failed array range: $(basename "${array_range_file}")"
  echo "- Failed manifest lines: $(basename "${failed_manifest}")"
  echo
  echo "## Failed Array Range"
  echo
  if [ -n "${array_range}" ]; then
    echo "\`${array_range}${cap}\`"
  else
    echo "No failed array tasks matched the configured retry states."
  fi
  echo
  echo "## Retry Command"
  echo
  if [ -n "${retry_command}" ]; then
    echo "\`\`\`bash"
    echo "${retry_command}"
    echo "\`\`\`"
  else
    echo "No retry command generated. Provide an sbatch script and confirm failed tasks exist."
  fi
  echo
  echo "## Review Before Submit"
  echo
  echo "- Confirm the failed task ids are actual array elements, not job steps."
  echo "- Confirm rerunning tasks will not overwrite successful outputs."
  echo "- Confirm concurrency cap and resource requests are safe for the site."
  echo "- Confirm failure causes have been addressed before retrying at scale."
} > "${plan}"

if [ "${run_sbatch_retry}" = "1" ]; then
  if [ -z "${retry_command}" ]; then
    echo "No retry command generated; refusing to submit." | tee "${submit_log}"
    exit 3
  fi
  if ! command -v sbatch >/dev/null 2>&1; then
    echo "sbatch command not found; refusing to submit." | tee "${submit_log}"
    exit 3
  fi
  sbatch --array="${retry_array_arg}" "${sbatch_script}" > "${submit_log}" 2>&1
else
  echo "Plan-only mode. Set RUN_SBATCH_RETRY=1 only after review." > "${submit_log}"
fi

cat <<EOF
Slurm array retry plan written to ${report_dir}

Start with:
  ${plan}

Failed task ids:
  ${failed_ids}

Failed array range:
  ${array_range_file}
EOF
