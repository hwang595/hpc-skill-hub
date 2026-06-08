#!/usr/bin/env bash
#SBATCH --job-name=ray-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=ray-smoke-%j.out

set -euo pipefail

record_dir="${RAY_RECORD_DIR:-ray-record-${SLURM_JOB_ID:-local}}"
ray_script="${RAY_SCRIPT:-examples/ray_smoke.py}"
ray_port="${RAY_PORT:-6379}"
ray_temp_dir="${RAY_TEMP_DIR:-${PWD}/${record_dir}/tmp}"

mkdir -p "${record_dir}" "${ray_temp_dir}"
log_file="${record_dir}/ray-slurm.log"

if [ -n "${PYTHON_ENV:-}" ]; then
  # shellcheck disable=SC1090
  . "${PYTHON_ENV}/bin/activate"
fi

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "ray_script=${ray_script}"
  echo "RUN_RAY_SMOKE=${RUN_RAY_SMOKE:-0}"
  echo
  echo "== scheduler layout =="
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
  echo "SLURM_JOB_NUM_NODES=${SLURM_JOB_NUM_NODES:-1}"
  echo "SLURM_NTASKS=${SLURM_NTASKS:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-1}"
  echo "SLURM_GPUS_PER_TASK=${SLURM_GPUS_PER_TASK:-0}"
  echo "SLURM_GPUS_ON_NODE=${SLURM_GPUS_ON_NODE:-0}"

  if [ -n "${SLURM_JOB_NODELIST:-}" ] && command -v scontrol >/dev/null 2>&1; then
    mapfile -t nodes < <(scontrol show hostnames "${SLURM_JOB_NODELIST}")
  else
    nodes=("$(hostname)")
  fi
  head_node="${nodes[0]}"
  ip_head="${head_node}:${ray_port}"
  export RAY_ADDRESS="${ip_head}"

  if [ -n "${SLURM_GPUS_PER_TASK:-}" ]; then
    ray_num_gpus="${SLURM_GPUS_PER_TASK}"
  elif [ -n "${SLURM_GPUS_ON_NODE:-}" ]; then
    ray_num_gpus="${SLURM_GPUS_ON_NODE}"
  else
    ray_num_gpus="${RAY_NUM_GPUS:-0}"
  fi

  echo
  echo "== ray launch plan =="
  echo "head_node=${head_node}"
  echo "ip_head=${ip_head}"
  echo "ray_num_cpus=${SLURM_CPUS_PER_TASK:-1}"
  echo "ray_num_gpus=${ray_num_gpus}"
  echo "ray_port=${ray_port}"
  echo "ray_temp_dir=${ray_temp_dir}"
  echo "manual_port_policy=${RAY_PORT_POLICY:-not_set}"

  echo
  echo "== selected environment =="
  echo "python=$(command -v python)"
  python --version
  ray --version || true

  echo
  echo "== launch command =="
  cat <<PLAN
srun --nodes="${SLURM_JOB_NUM_NODES:-1}" --ntasks="${SLURM_JOB_NUM_NODES:-1}" \\
  ray symmetric-run \\
  --address "${ip_head}" \\
  --min-nodes "${SLURM_JOB_NUM_NODES:-1}" \\
  --num-cpus "${SLURM_CPUS_PER_TASK:-1}" \\
  --num-gpus "${ray_num_gpus}" \\
  --temp-dir "${ray_temp_dir}" \\
  -- \\
  python -u "${ray_script}" "${record_dir}"
PLAN

  if [ "${RUN_RAY_SMOKE:-0}" = "1" ]; then
    srun --nodes="${SLURM_JOB_NUM_NODES:-1}" --ntasks="${SLURM_JOB_NUM_NODES:-1}" \
      ray symmetric-run \
      --address "${ip_head}" \
      --min-nodes "${SLURM_JOB_NUM_NODES:-1}" \
      --num-cpus "${SLURM_CPUS_PER_TASK:-1}" \
      --num-gpus "${ray_num_gpus}" \
      --temp-dir "${ray_temp_dir}" \
      -- \
      python -u "${ray_script}" "${record_dir}"
  else
    echo "dry_run=true"
    echo "Set RUN_RAY_SMOKE=1 only after reviewing the launch plan."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
