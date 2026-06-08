#!/usr/bin/env bash
set -euo pipefail

port="${PORT:-8888}"

echo "Request an interactive allocation first, then run this on the compute node."
echo "host=$(hostname)"
echo "port=${port}"
echo
echo "From your laptop, adapt this tunnel command:"
echo "ssh -N -L ${port}:\$(hostname):${port} <user>@<login-node>"
echo

module load <python-module>
jupyter lab --no-browser --ip=0.0.0.0 --port="${port}"
