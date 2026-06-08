#!/usr/bin/env bash
set -euo pipefail

bench_root="${1:-${BENCH_ROOT:-${SCRATCH:-$PWD}/ior-mdtest-smoke}}"

echo "== host =="
hostname
echo "pwd=${PWD}"
echo "bench_root=${bench_root}"

echo "== slurm =="
command -v sbatch || true
command -v srun || true
command -v squeue || true

echo "== benchmark tools =="
command -v ior || true
ior --version || true
command -v mdtest || true
mdtest --version || true

echo "== target directory =="
mkdir -p "${bench_root}"
test -d "${bench_root}"
test -w "${bench_root}"
echo "writable=yes"

echo "== next =="
echo "Submit examples/ior-mdtest-smoke.sbatch in plan-only mode, then review site policy before RUN_BENCHMARK=1."
