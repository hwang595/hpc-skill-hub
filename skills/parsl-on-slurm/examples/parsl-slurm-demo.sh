#!/usr/bin/env bash

set -euo pipefail

export RUN_PARSL="${RUN_PARSL:-0}"
export PARSL_ACCOUNT="${PARSL_ACCOUNT:-<account>}"
export PARSL_PARTITION="${PARSL_PARTITION:-<partition>}"
export PARSL_BLOCKS="${PARSL_BLOCKS:-1}"
export PARSL_NODES_PER_BLOCK="${PARSL_NODES_PER_BLOCK:-1}"
export PARSL_CORES_PER_NODE="${PARSL_CORES_PER_NODE:-2}"
export PARSL_MAX_WORKERS_PER_NODE="${PARSL_MAX_WORKERS_PER_NODE:-2}"
export PARSL_WALLTIME="${PARSL_WALLTIME:-00:10:00}"
export PARSL_RUN_DIR="${PARSL_RUN_DIR:-runs/parsl}"
export OUTPUT_DIR="${OUTPUT_DIR:-results}"

mkdir -p "${PARSL_RUN_DIR}" "${OUTPUT_DIR}"

if [ -n "${PYTHON_ENV:-}" ]; then
  # shellcheck disable=SC1090
  . "${PYTHON_ENV}/bin/activate"
fi

echo "RUN_PARSL=${RUN_PARSL}"
echo "PARSL_ACCOUNT=${PARSL_ACCOUNT}"
echo "PARSL_PARTITION=${PARSL_PARTITION}"
echo "PARSL_BLOCKS=${PARSL_BLOCKS}"
echo "PARSL_NODES_PER_BLOCK=${PARSL_NODES_PER_BLOCK}"
echo "PARSL_CORES_PER_NODE=${PARSL_CORES_PER_NODE}"
echo "PARSL_MAX_WORKERS_PER_NODE=${PARSL_MAX_WORKERS_PER_NODE}"
echo "PARSL_WALLTIME=${PARSL_WALLTIME}"
echo "PARSL_RUN_DIR=${PARSL_RUN_DIR}"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
echo "python=$(command -v python)"
python --version

python examples/parsl_smoke.py
