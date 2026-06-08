#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: threadpool-env-report.sh [threads-per-task]

Generate a read-only report of common BLAS/OpenMP/language thread variables and
print a conservative export block. If threads-per-task is omitted, the script
uses SLURM_CPUS_PER_TASK when available, then falls back to 1.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

threads="${1:-${THREADS_PER_TASK:-${SLURM_CPUS_PER_TASK:-1}}}"

if ! [[ "${threads}" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: threads-per-task must be a positive integer: ${threads}" >&2
  exit 2
fi

thread_vars=(
  OMP_NUM_THREADS
  OMP_PLACES
  OMP_PROC_BIND
  OMP_DYNAMIC
  OMP_THREAD_LIMIT
  MKL_NUM_THREADS
  MKL_DOMAIN_NUM_THREADS
  MKL_DYNAMIC
  OPENBLAS_NUM_THREADS
  GOTO_NUM_THREADS
  BLIS_NUM_THREADS
  VECLIB_MAXIMUM_THREADS
  NUMEXPR_NUM_THREADS
  NUMEXPR_MAX_THREADS
  R_DATATABLE_NUM_THREADS
  JULIA_NUM_THREADS
  RAYON_NUM_THREADS
  TF_NUM_INTRAOP_THREADS
  TF_NUM_INTEROP_THREADS
)

scheduler_vars=(
  SLURM_JOB_ID
  SLURM_CPUS_PER_TASK
  SLURM_NTASKS
  SLURM_TASKS_PER_NODE
  SLURM_CPUS_ON_NODE
  PBS_NP
  NSLOTS
  LSB_DJOB_NUMPROC
)

echo "BLAS/OpenMP threadpool environment report"
echo "========================================="
echo
printf 'target_threads_per_process=%s\n' "${threads}"
printf 'outer_parallelism=%s\n' "${OUTER_PARALLELISM:-<not-specified>}"

echo
echo "== scheduler cpu context =="
for name in "${scheduler_vars[@]}"; do
  printf '%s=%s\n' "${name}" "${!name-<unset>}"
done

echo
echo "== current thread-related environment =="
for name in "${thread_vars[@]}"; do
  printf '%s=%s\n' "${name}" "${!name-<unset>}"
done

echo
echo "== mismatch warnings =="
for name in OMP_NUM_THREADS MKL_NUM_THREADS OPENBLAS_NUM_THREADS BLIS_NUM_THREADS VECLIB_MAXIMUM_THREADS NUMEXPR_NUM_THREADS R_DATATABLE_NUM_THREADS JULIA_NUM_THREADS; do
  value="${!name-}"
  if [[ -n "${value}" && "${value}" =~ ^[0-9]+$ && "${value}" != "${threads}" ]]; then
    printf 'WARN: %s=%s differs from target %s\n' "${name}" "${value}" "${threads}"
  fi
done

if [[ "${SLURM_NTASKS:-}" =~ ^[0-9]+$ && "${SLURM_NTASKS}" -gt 1 && "${threads}" -gt 1 ]]; then
  printf 'NOTE: %s Slurm tasks times %s inner threads can be correct for hybrid jobs, but can oversubscribe if cpus-per-task is not set.\n' "${SLURM_NTASKS}" "${threads}"
fi

echo
echo "== optional python threadpool metadata =="
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY'
import json
import os
import sys

print(f"python={sys.executable}")

try:
    import threadpoolctl
except Exception as exc:
    print(f"threadpoolctl=unavailable ({exc.__class__.__name__})")
else:
    try:
        print("threadpoolctl_info=" + json.dumps(threadpoolctl.threadpool_info(), sort_keys=True))
    except Exception as exc:
        print(f"threadpoolctl_info_error={exc.__class__.__name__}: {exc}")

try:
    import numpy
except Exception as exc:
    print(f"numpy=unavailable ({exc.__class__.__name__})")
else:
    print(f"numpy_version={numpy.__version__}")

try:
    import numexpr
except Exception as exc:
    print(f"numexpr=unavailable ({exc.__class__.__name__})")
else:
    try:
        print(f"numexpr_threads={numexpr.get_num_threads()}")
    except Exception as exc:
        print(f"numexpr_threads_error={exc.__class__.__name__}: {exc}")

for name in (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "BLIS_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    print(f"python_env_{name}={os.environ.get(name, '<unset>')}")
PY
else
  echo "python3 is not available on this system"
fi

cat <<EXPORTS

== recommended export block ==
# Review this block against your outer parallelism before copying it.
export OMP_NUM_THREADS="${threads}"
export OMP_PLACES="cores"
export OMP_PROC_BIND="close"
export OMP_DYNAMIC="FALSE"
export MKL_NUM_THREADS="\${OMP_NUM_THREADS}"
export MKL_DYNAMIC="FALSE"
export OPENBLAS_NUM_THREADS="\${OMP_NUM_THREADS}"
export GOTO_NUM_THREADS="\${OMP_NUM_THREADS}"
export BLIS_NUM_THREADS="\${OMP_NUM_THREADS}"
export VECLIB_MAXIMUM_THREADS="\${OMP_NUM_THREADS}"
export NUMEXPR_NUM_THREADS="\${OMP_NUM_THREADS}"
export R_DATATABLE_NUM_THREADS="\${OMP_NUM_THREADS}"
export JULIA_NUM_THREADS="\${OMP_NUM_THREADS}"
EXPORTS

cat <<'PROMPTS'

== review prompts ==
- Count outer parallelism first: MPI ranks, workers, array tasks, Python processes, data-loader workers, or job steps.
- Set inner BLAS/OpenMP threads to cpus-per-task for one threaded process, or to 1 for many single-core workers.
- Avoid comparing performance across different partitions, node types, inputs, or process counts.
- If a package overrides these variables after startup, use that package's documented runtime controls.
PROMPTS
