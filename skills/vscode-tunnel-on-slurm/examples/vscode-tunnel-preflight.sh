#!/usr/bin/env bash
set -euo pipefail

project_dir="${1:-${VSCODE_PROJECT_DIR:-$PWD}}"
code_cli="${VSCODE_CODE_CLI:-code}"

echo "== host =="
hostname
echo "pwd=$PWD"
echo "project_dir=${project_dir}"

echo "== slurm =="
command -v sbatch || true
command -v squeue || true
command -v scancel || true

echo "== vscode cli =="
if command -v "${code_cli}" >/dev/null 2>&1; then
  "${code_cli}" --version | sed -n '1,3p' || true
  "${code_cli}" tunnel --help >/dev/null
  echo "code-tunnel-command=available"
else
  echo "code-tunnel-command=missing"
fi

echo "== project =="
if [ -d "${project_dir}" ]; then
  find "${project_dir}" -maxdepth 1 -mindepth 1 | sed -n '1,10p'
else
  echo "ERROR: project directory does not exist: ${project_dir}" >&2
  exit 1
fi

echo "== next =="
echo "Confirm site policy allows VS Code Remote Tunnels before setting RUN_VSCODE_TUNNEL=1."
