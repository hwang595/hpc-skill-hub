#!/usr/bin/env bash

set -euo pipefail

export RUN_DASK="${RUN_DASK:-0}"
export DASK_ACCOUNT="${DASK_ACCOUNT:-<account>}"
export DASK_QUEUE="${DASK_QUEUE:-<partition>}"
export DASK_JOBS="${DASK_JOBS:-1}"
export DASK_CORES="${DASK_CORES:-2}"
export DASK_PROCESSES="${DASK_PROCESSES:-1}"
export DASK_MEMORY="${DASK_MEMORY:-4GB}"
export DASK_WALLTIME="${DASK_WALLTIME:-00:10:00}"
export DASK_LOG_DIR="${DASK_LOG_DIR:-logs/dask}"
export DASK_LOCAL_DIR="${DASK_LOCAL_DIR:-${PWD}/dask-worker-space}"
export OUTPUT_DIR="${OUTPUT_DIR:-results}"

mkdir -p "${DASK_LOG_DIR}" "${DASK_LOCAL_DIR}" "${OUTPUT_DIR}"

if [ -n "${PYTHON_ENV:-}" ]; then
  # shellcheck disable=SC1090
  . "${PYTHON_ENV}/bin/activate"
fi

echo "RUN_DASK=${RUN_DASK}"
echo "DASK_ACCOUNT=${DASK_ACCOUNT}"
echo "DASK_QUEUE=${DASK_QUEUE}"
echo "DASK_JOBS=${DASK_JOBS}"
echo "DASK_CORES=${DASK_CORES}"
echo "DASK_PROCESSES=${DASK_PROCESSES}"
echo "DASK_MEMORY=${DASK_MEMORY}"
echo "DASK_WALLTIME=${DASK_WALLTIME}"
echo "DASK_LOG_DIR=${DASK_LOG_DIR}"
echo "DASK_LOCAL_DIR=${DASK_LOCAL_DIR}"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
echo "python=$(command -v python)"
python --version

python examples/dask_jobqueue_demo.py
