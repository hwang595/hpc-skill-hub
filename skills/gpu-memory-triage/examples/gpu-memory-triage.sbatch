#!/usr/bin/env bash
#SBATCH --job-name=gpu-memory-triage
#SBATCH --account=<account>
#SBATCH --partition=<gpu-partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --gres=gpu:1
#SBATCH --time=00:10:00
#SBATCH --output=gpu-memory-triage-%j.out

set -euo pipefail

log_file="${JOB_LOG:-}"

echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "host=$(hostname)"
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
echo "SLURM_JOB_GPUS=${SLURM_JOB_GPUS:-}"
echo "SLURM_GPUS=${SLURM_GPUS:-}"
echo "CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-}"
echo "ROCR_VISIBLE_DEVICES=${ROCR_VISIBLE_DEVICES:-}"
echo "GPU_DEVICE_ORDINAL=${GPU_DEVICE_ORDINAL:-}"

echo
echo "== vendor memory =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu --format=csv
else
  echo "nvidia-smi not found"
fi

if command -v rocm-smi >/dev/null 2>&1; then
  rocm-smi --showmeminfo vram || true
else
  echo "rocm-smi not found"
fi

echo
echo "== framework memory =="
python3 - <<'PY' || true
try:
    import torch

    print("torch:", torch.__version__)
    print("cuda_available:", torch.cuda.is_available())
    print("cuda_device_count:", torch.cuda.device_count())
    if torch.cuda.is_available():
        for index in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(index)
            total_gib = props.total_memory / (1024 ** 3)
            print(f"device[{index}]={props.name} total_gib={total_gib:.2f}")
            print(f"device[{index}] reserved={torch.cuda.memory_reserved(index)}")
            print(f"device[{index}] allocated={torch.cuda.memory_allocated(index)}")
except Exception as exc:
    print("torch_memory_probe_error:", exc)
PY

echo
echo "== log scan =="
if [ -n "${log_file}" ] && [ -f "${log_file}" ]; then
  echo "log_file=${log_file}"
  grep -Ein "out.of.memory|cuda.*memory|cublas|cudnn|rocm|hip|oom|killed|bus error|segmentation fault|allocation|allocator|dataloader|worker" "${log_file}" || true
  echo
  echo "== log tail =="
  tail -n 80 "${log_file}"
else
  echo "No JOB_LOG file provided; set JOB_LOG=/path/to/training.log to scan logs."
fi

echo
echo "== next-action hints =="
echo "- No visible GPUs: check partition, gres/gpu request, container GPU passthrough, and module environment."
echo "- Device visible but total memory is smaller than expected: check MIG, GPU type, and requested partition."
echo "- Framework OOM: reduce batch size, sequence length, model size, activation storage, or optimizer state."
echo "- Host OOM or killed worker: inspect CPU memory request and data-loader worker count."
echo "- Fragmentation clues: rerun with a minimal reproducer and compare allocator settings."

echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
