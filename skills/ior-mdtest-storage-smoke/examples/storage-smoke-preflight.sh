#!/usr/bin/env bash
set -euo pipefail

check_tools="${CHECK_TOOLS:-1}"
if [ "${1:-}" = "--paths-only" ]; then
  check_tools=0
  shift
fi

if [ "$#" -gt 1 ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  echo "usage: storage-smoke-preflight.sh [--paths-only] [benchmark-root]"
  echo "       CREATE_BENCH_ROOT=1 storage-smoke-preflight.sh <approved-root>"
  if [ "$#" -gt 1 ]; then
    exit 2
  fi
  exit 0
fi

bench_root="${1:-${BENCH_ROOT:-${SCRATCH:-$PWD}/ior-mdtest-smoke}}"
missing_tools=0

echo "== host =="
hostname
echo "pwd=${PWD}"
echo "bench_root=${bench_root}"

echo "== slurm and benchmark tools =="
if [ "${check_tools}" = "1" ]; then
  for tool in sbatch srun ior mdtest python3; do
    if command -v "${tool}" >/dev/null 2>&1; then
      echo "${tool}=$(command -v "${tool}")"
    else
      echo "${tool}=missing"
      missing_tools=1
    fi
  done
else
  echo "tool checks skipped in --paths-only mode"
fi

echo "== target directory =="
if [ -e "${bench_root}" ]; then
  if [ ! -d "${bench_root}" ]; then
    echo "ERROR: benchmark root exists but is not a directory." >&2
    exit 2
  fi
  if [ ! -w "${bench_root}" ]; then
    echo "ERROR: benchmark root is not writable by the current user." >&2
    exit 2
  fi
  echo "exists=yes"
  echo "writable=yes"
else
  probe="${bench_root}"
  while [ ! -e "${probe}" ] && [ "${probe}" != "/" ]; do
    probe="$(dirname "${probe}")"
  done
  echo "exists=no"
  echo "nearest_existing_parent=${probe}"
  if [ ! -d "${probe}" ] || [ ! -w "${probe}" ]; then
    echo "ERROR: nearest existing parent is not a writable directory." >&2
    exit 2
  fi
  if [ "${CREATE_BENCH_ROOT:-0}" = "1" ]; then
    mkdir -p "${bench_root}"
    echo "created=yes"
  else
    echo "created=no"
    echo "No directory was created; set CREATE_BENCH_ROOT=1 only after path review."
  fi
fi

echo "== next =="
echo "Submit ior-mdtest-smoke.sbatch in plan-only mode and review its log before enabling both run gates."

if [ "${missing_tools}" -ne 0 ]; then
  exit 1
fi
