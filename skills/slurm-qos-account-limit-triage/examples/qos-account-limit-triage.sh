#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: qos-account-limit-triage.sh [job-id] [user] [output-dir]

Collect read-only Slurm evidence for pending jobs affected by account,
association, QOS, fairshare, or TRES-minute limits.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$#" -gt 3 ]]; then
  usage >&2
  exit 2
fi

job_id="${1:-${SLURM_JOB_ID_TO_TRIAGE:-}}"
target_user="${2:-${SLURM_TRIAGE_USER:-${USER:-}}}"
output_dir="${3:-${OUTPUT_DIR:-slurm-qos-account-limit-report}}"

if [[ -n "${job_id}" && ! "${job_id}" =~ ^[A-Za-z0-9_.+-]+$ ]]; then
  echo "ERROR: job id contains unexpected characters: ${job_id}" >&2
  exit 2
fi

if [[ -z "${target_user}" ]]; then
  echo "ERROR: no user supplied and USER is not set." >&2
  exit 2
fi

if ! command -v squeue >/dev/null 2>&1; then
  echo "ERROR: squeue is required." >&2
  exit 1
fi

if [[ -e "${output_dir}" ]]; then
  echo "ERROR: output directory already exists: ${output_dir}" >&2
  exit 2
fi

mkdir -p "${output_dir}"

timestamp() {
  date -u +%Y-%m-%dT%H:%M:%SZ
}

capture() {
  output_file="$1"
  shift
  {
    printf '# command\n'
    printf '%q ' "$@"
    printf '\n\n'
    "$@"
  } > "${output_file}" 2>&1 || {
    status="$?"
    {
      printf '\nWARN: command exited with status %s\n' "${status}"
      printf 'This may be normal if local Slurm policy hides this data.\n'
    } >> "${output_file}"
  }
}

missing() {
  output_file="$1"
  tool_name="$2"
  {
    printf '# command unavailable\n'
    printf '%s is not available or not exposed by this site.\n' "${tool_name}"
  } > "${output_file}"
}

queue_format="%.18i %.12a %.12Q %.9P %.40j %.12u %.2t %.10M %.10l %.8C %.6D %.30E %R"

if [[ -n "${job_id}" ]]; then
  capture "${output_dir}/squeue-job.txt" \
    squeue --jobs="${job_id}" --format="${queue_format}"
else
  capture "${output_dir}/squeue-user-pending.txt" \
    squeue --states=PENDING --user="${target_user}" --format="${queue_format}"
fi

if command -v scontrol >/dev/null 2>&1 && [[ -n "${job_id}" ]]; then
  capture "${output_dir}/scontrol-job.txt" scontrol show job "${job_id}"
else
  missing "${output_dir}/scontrol-job.txt" "scontrol or job-id"
fi

if command -v sacctmgr >/dev/null 2>&1; then
  capture "${output_dir}/sacctmgr-associations.txt" \
    sacctmgr --noheader --parsable2 show assoc where user="${target_user}" \
    format=Cluster,Account,User,Partition,QOS,DefaultQOS,Fairshare,GrpJobs,GrpSubmit,GrpTRES,GrpTRESMins,GrpTRESRunMins,MaxJobs,MaxSubmit,MaxTRES,MaxTRESPerNode,MaxWall

  capture "${output_dir}/sacctmgr-qos.txt" \
    sacctmgr --noheader --parsable2 show qos \
    format=Name,Priority,Flags,GraceTime,GrpJobs,GrpSubmit,GrpTRES,GrpTRESMins,GrpTRESRunMins,MaxJobsPU,MaxSubmitJobsPU,MaxTRES,MaxTRESPU,MaxTRESPerNode,MaxWall
else
  missing "${output_dir}/sacctmgr-associations.txt" "sacctmgr"
  missing "${output_dir}/sacctmgr-qos.txt" "sacctmgr"
fi

if command -v sshare >/dev/null 2>&1; then
  capture "${output_dir}/sshare-user.txt" sshare --long --users="${target_user}"
else
  missing "${output_dir}/sshare-user.txt" "sshare"
fi

if command -v sprio >/dev/null 2>&1; then
  if [[ -n "${job_id}" ]]; then
    capture "${output_dir}/sprio-job.txt" sprio --jobs="${job_id}"
  else
    capture "${output_dir}/sprio-user.txt" sprio --user="${target_user}"
  fi
else
  missing "${output_dir}/sprio.txt" "sprio"
fi

cat > "${output_dir}/summary.md" <<SUMMARY
# Slurm QOS Account Limit Triage

- Generated: $(timestamp)
- Job id: ${job_id:-not supplied}
- User: ${target_user}
- Output directory: ${output_dir}

## Review Prompts

- If the queue reason starts with \`AssocGrp\`, compare running and pending
  usage against account or user aggregate limits.
- If the queue reason starts with \`AssocMax\`, compare the job's request
  against per-job association limits.
- If the queue reason starts with \`QOSGrp\`, compare current use against the
  selected QOS aggregate limits.
- If the queue reason starts with \`QOSMax\`, compare the job request against
  per-job QOS limits.
- If the reason is \`InvalidAccount\` or \`InvalidQOS\`, verify the account,
  QOS, user, partition, and cluster association.
- If the reason is \`Priority\`, inspect fairshare and priority factors, then
  use local policy docs before promising a start time.

## Public Sharing Reminder

Review every generated file for usernames, accounts, project names, job names,
QOS names, partition names, and local policy before posting outside an approved
support channel.
SUMMARY

echo "wrote report_dir=${output_dir}"
