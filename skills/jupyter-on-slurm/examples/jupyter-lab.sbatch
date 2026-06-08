#!/usr/bin/env bash
#SBATCH --job-name=jupyter-lab
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=jupyter-%j.out

set -euo pipefail

port="${JUPYTER_PORT:-8888}"
host="$(hostname -f 2>/dev/null || hostname)"

echo "host=${host}"
echo "port=${port}"
echo "job_id=${SLURM_JOB_ID:-unknown}"
echo
echo "From your laptop, adapt this tunnel command:"
echo "ssh -N -L ${port}:${host}:${port} <user>@<login-node>"
echo
echo "Keep this job running while you use the notebook, then cancel it when done."
echo

module load <python-module>

jupyter lab \
  --no-browser \
  --ip="${host}" \
  --port="${port}" \
  --ServerApp.port_retries=0
