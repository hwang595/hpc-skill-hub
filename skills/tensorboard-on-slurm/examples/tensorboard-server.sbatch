#!/usr/bin/env bash
#SBATCH --job-name=tensorboard
#SBATCH --account=<account>
#SBATCH --partition=<debug-partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --output=tensorboard-%j.out

set -euo pipefail

logdir="${TENSORBOARD_LOGDIR:-runs}"
port="${TENSORBOARD_PORT:-6006}"
host="${TENSORBOARD_HOST:-127.0.0.1}"
reload_interval="${TENSORBOARD_RELOAD_INTERVAL:-30}"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "job_id=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "logdir=${logdir}"
echo "bind_host=${host}"
echo "port=${port}"
echo "reload_interval=${reload_interval}"
echo "RUN_TENSORBOARD=${RUN_TENSORBOARD:-0}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is not available in PATH." >&2
  exit 1
fi

if ! command -v tensorboard >/dev/null 2>&1; then
  echo "ERROR: tensorboard is not available in PATH. Activate the site-approved environment first." >&2
  exit 1
fi

python3 --version
tensorboard --version || true
python3 "${script_dir}/logdir-check.py" "${logdir}"

if [ "${RUN_TENSORBOARD:-0}" != "1" ]; then
  echo "Plan-only mode. Review site policy and set RUN_TENSORBOARD=1 to launch."
  echo "Planned command:"
  echo "tensorboard --logdir '${logdir}' --host '${host}' --port '${port}' --reload_interval '${reload_interval}'"
  exit 0
fi

exec tensorboard \
  --logdir "${logdir}" \
  --host "${host}" \
  --port "${port}" \
  --reload_interval "${reload_interval}"
