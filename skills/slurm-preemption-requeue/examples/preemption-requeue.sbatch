#!/usr/bin/env bash
#SBATCH --job-name=preempt-requeue-demo
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:10:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@120
#SBATCH --output=preempt-requeue-%j.out

set -euo pipefail

run_worker="${RUN_REQUEUE_WORKER:-0}"
output_dir="${OUTPUT_DIR:-preemption-requeue-${SLURM_JOB_ID:-manual}}"
stop_file="${output_dir}/stop.requested"
signal_file="${output_dir}/slurm-signal.env"
worker_pid=""

record_signal() {
  signal_name="$1"
  mkdir -p "${output_dir}"
  {
    printf 'signal=%s\n' "${signal_name}"
    printf 'recorded_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'slurm_job_id=%s\n' "${SLURM_JOB_ID:-manual}"
    printf 'slurm_restart_count=%s\n' "${SLURM_RESTART_COUNT:-0}"
  } > "${signal_file}"
  : > "${stop_file}"
  printf 'recorded %s stop request in %s\n' "${signal_name}" "${output_dir}"
}

trap 'record_signal USR1' USR1
trap 'record_signal TERM' TERM

mkdir -p "${output_dir}"

printf 'job_id=%s\n' "${SLURM_JOB_ID:-manual}"
printf 'restart_count=%s\n' "${SLURM_RESTART_COUNT:-0}"
printf 'output_dir=%s\n' "${output_dir}"
printf 'signal_policy=%s\n' 'B:USR1@120'
printf 'requeue_policy=%s\n' 'SBATCH --requeue; no automatic scontrol requeue'

if [ "${run_worker}" != "1" ]; then
  printf 'RUN_REQUEUE_WORKER is not 1; review mode only, no workload started.\n'
  exit 0
fi

export OUTPUT_DIR="${output_dir}"
export STOP_FILE="${stop_file}"
export MAX_STEPS="${MAX_STEPS:-5}"
export SLEEP_SECONDS="${SLEEP_SECONDS:-5}"

bash examples/signal-aware-worker.sh &
worker_pid="$!"
worker_status=0

while kill -0 "${worker_pid}" 2>/dev/null; do
  if wait "${worker_pid}"; then
    worker_status=0
    break
  fi
  worker_status="$?"
  if [ "${worker_status}" -ge 128 ] && kill -0 "${worker_pid}" 2>/dev/null; then
    continue
  fi
  break
done

printf 'worker_exit_status=%s\n' "${worker_status}"
exit "${worker_status}"
