#!/usr/bin/env bash
set -euo pipefail

echo "== slurm cpu settings =="
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-local}"
echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-unset}"
echo "SLURM_TASKS_PER_NODE=${SLURM_TASKS_PER_NODE:-unset}"

echo
echo "== openmp settings =="
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS:-unset}"
echo "OMP_PLACES=${OMP_PLACES:-unset}"
echo "OMP_PROC_BIND=${OMP_PROC_BIND:-unset}"

echo
echo "== visible cpu count =="
if command -v nproc >/dev/null 2>&1; then
  nproc
else
  echo "nproc not available"
fi

echo
echo "== cpu topology, if available =="
if command -v lscpu >/dev/null 2>&1; then
  lscpu | grep -E "CPU\\(s\\)|Core\\(s\\)|Thread\\(s\\)|Socket\\(s\\)|NUMA" || true
else
  echo "lscpu not available"
fi

echo
echo "Replace this script with the real threaded application after validation."
