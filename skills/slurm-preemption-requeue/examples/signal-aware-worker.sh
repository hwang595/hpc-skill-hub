#!/usr/bin/env bash
set -euo pipefail

output_dir="${OUTPUT_DIR:-preemption-requeue-manual}"
checkpoint_file="${output_dir}/checkpoint.env"
complete_file="${output_dir}/complete.txt"
stop_file="${STOP_FILE:-${output_dir}/stop.requested}"
max_steps="${MAX_STEPS:-5}"
sleep_seconds="${SLEEP_SECONDS:-1}"
stop_requested=0

mkdir -p "${output_dir}"

save_checkpoint() {
  step="$1"
  reason="$2"
  tmp_file="${checkpoint_file}.tmp"
  {
    printf 'step=%s\n' "${step}"
    printf 'reason=%s\n' "${reason}"
    printf 'recorded_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'slurm_job_id=%s\n' "${SLURM_JOB_ID:-manual}"
    printf 'slurm_restart_count=%s\n' "${SLURM_RESTART_COUNT:-0}"
  } > "${tmp_file}"
  mv "${tmp_file}" "${checkpoint_file}"
}

handle_signal() {
  signal_name="$1"
  stop_requested=1
  : > "${stop_file}"
  current_step="${current_step:-0}"
  save_checkpoint "${current_step}" "${signal_name}"
  printf 'received %s; checkpointed step %s\n' "${signal_name}" "${current_step}"
}

trap 'handle_signal USR1' USR1
trap 'handle_signal TERM' TERM
trap 'handle_signal INT' INT

last_step=0
if [ -f "${checkpoint_file}" ]; then
  last_step="$(sed -n 's/^step=//p' "${checkpoint_file}" | tail -n 1)"
fi

case "${last_step}" in
  ''|*[!0-9]*)
    printf 'checkpoint step was not numeric; starting from 0\n'
    last_step=0
    ;;
esac

current_step=$((last_step + 1))
printf 'starting_from_step=%s\n' "${current_step}"
printf 'max_steps=%s\n' "${max_steps}"
printf 'checkpoint_file=%s\n' "${checkpoint_file}"

while [ "${current_step}" -le "${max_steps}" ]; do
  if [ -f "${stop_file}" ] || [ "${stop_requested}" -eq 1 ]; then
    save_checkpoint "${current_step}" "stop-requested"
    printf 'stop requested before step %s completed\n' "${current_step}"
    exit 75
  fi

  printf 'running_step=%s\n' "${current_step}"
  sleep "${sleep_seconds}"
  save_checkpoint "${current_step}" "completed-step"
  current_step=$((current_step + 1))
done

printf 'completed_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "${complete_file}"
printf 'completed_steps=%s\n' "${max_steps}"
