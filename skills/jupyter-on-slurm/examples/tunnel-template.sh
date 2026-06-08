#!/usr/bin/env bash
set -euo pipefail

login_node="${1:-<login-node>}"
compute_node="${2:-<compute-node>}"
port="${3:-8888}"

echo "Run this from your laptop after the Slurm job prints its compute node:"
echo "ssh -N -L ${port}:${compute_node}:${port} <user>@${login_node}"
echo
echo "Then open the Jupyter URL from the Slurm output in your local browser."
