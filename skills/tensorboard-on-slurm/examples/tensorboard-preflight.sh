#!/usr/bin/env bash
set -euo pipefail

logdir="${1:-${TENSORBOARD_LOGDIR:-runs}}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== host =="
hostname
echo "pwd=$PWD"
echo "logdir=${logdir}"

echo "== slurm =="
command -v sbatch || true
command -v srun || true
command -v squeue || true
command -v scancel || true

echo "== python =="
command -v python3 || true
python3 --version || true

echo "== tensorboard =="
command -v tensorboard || true
tensorboard --version || true

echo "== logdir =="
python3 "${script_dir}/logdir-check.py" "${logdir}"

echo "== next =="
echo "Confirm site policy, then submit examples/tensorboard-server.sbatch in plan-only mode."
