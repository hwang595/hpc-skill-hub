#!/usr/bin/env bash
set -euo pipefail

compute_host="${1:-<compute-host>}"
remote_port="${2:-8787}"
local_port="${3:-8787}"
login_host="${LOGIN_HOST:-<login-host>}"

cat <<EOF
Run this command from your laptop only if your site requires SSH port forwarding:

ssh -N -L ${local_port}:${compute_host}:${remote_port} ${login_host}

Then open:

http://localhost:${local_port}

Close the SSH tunnel and cancel the Slurm job when finished.
EOF
