#!/usr/bin/env bash
set -euo pipefail

task_id="${SLURM_PROCID:-0}"
local_id="${SLURM_LOCALID:-0}"
node_id="${SLURM_NODEID:-0}"
host="$(hostname)"
cuda_visible="${CUDA_VISIBLE_DEVICES:-unset}"
rocr_visible="${ROCR_VISIBLE_DEVICES:-unset}"
hip_visible="${HIP_VISIBLE_DEVICES:-unset}"
slurm_step_gpus="${SLURM_STEP_GPUS:-unset}"
slurm_job_gpus="${SLURM_JOB_GPUS:-unset}"
slurm_gpus_on_node="${SLURM_GPUS_ON_NODE:-unset}"
gpu_uuid="unavailable"
gpu_name="unavailable"

if command -v nvidia-smi >/dev/null 2>&1; then
  first_visible="${cuda_visible%%,*}"
  if [ -n "${first_visible}" ] && [ "${first_visible}" != "unset" ]; then
    query_output="$(nvidia-smi --id="${first_visible}" --query-gpu=uuid,name --format=csv,noheader 2>/dev/null | head -n 1 || true)"
  else
    query_output="$(nvidia-smi --query-gpu=uuid,name --format=csv,noheader 2>/dev/null | head -n 1 || true)"
  fi
  if [ -n "${query_output:-}" ]; then
    gpu_uuid="${query_output%%,*}"
    gpu_name="${query_output#*, }"
  fi
fi

if [ "${task_id}" = "0" ]; then
  printf 'task\tlocal_task\tnode\thost\tcuda_visible\trocr_visible\thip_visible\tslurm_step_gpus\tslurm_job_gpus\tslurm_gpus_on_node\tgpu_uuid\tgpu_name\n'
fi

printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "${task_id}" \
  "${local_id}" \
  "${node_id}" \
  "${host}" \
  "${cuda_visible}" \
  "${rocr_visible}" \
  "${hip_visible}" \
  "${slurm_step_gpus}" \
  "${slurm_job_gpus}" \
  "${slurm_gpus_on_node}" \
  "${gpu_uuid}" \
  "${gpu_name}"
