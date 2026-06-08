#!/usr/bin/env bash
set -euo pipefail

SIM_SOFTWARE="${SIM_SOFTWARE:-generic-simulation}"
SIM_EXECUTABLE="${SIM_EXECUTABLE:-}"
SIM_INPUTS="${SIM_INPUTS:-}"
SIM_COMMAND="${SIM_COMMAND:-}"
SCHEDULER_TEMPLATE="${SCHEDULER_TEMPLATE:-}"
POSTPROCESS_COMMAND="${POSTPROCESS_COMMAND:-}"
OUTPUT_DIR="${OUTPUT_DIR:-simulation-run-plan}"
RUN_SIMULATION="${RUN_SIMULATION:-0}"
RUN_POSTPROCESS="${RUN_POSTPROCESS:-0}"

mkdir -p "${OUTPUT_DIR}"

PLAN_FILE="${OUTPUT_DIR}/run-plan.md"
INPUT_REPORT="${OUTPUT_DIR}/input-checks.txt"
REPRO_FILE="${OUTPUT_DIR}/reproducibility-notes.txt"
COMMAND_LOG="${OUTPUT_DIR}/command-log.txt"

detect_scheduler() {
  if [ -n "${SLURM_JOB_ID:-}" ]; then
    printf "slurm"
  elif [ -n "${PBS_JOBID:-}" ]; then
    printf "pbs"
  elif [ -n "${LSB_JOBID:-}" ]; then
    printf "lsf"
  else
    printf "not-in-batch-job"
  fi
}

command_name() {
  if [ -n "${SIM_EXECUTABLE}" ]; then
    printf "%s" "${SIM_EXECUTABLE%% *}"
  elif [ -n "${SIM_COMMAND}" ]; then
    printf "%s" "${SIM_COMMAND%% *}"
  else
    printf ""
  fi
}

SCHEDULER_NAME="$(detect_scheduler)"
EXECUTABLE_NAME="$(command_name)"

{
  printf "Simulation software: %s\n" "${SIM_SOFTWARE}"
  printf "Checked at: %s\n" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  printf "Working directory: %s\n" "$(pwd)"
  printf "Output directory: %s\n" "${OUTPUT_DIR}"
  printf "\n"
  if [ -z "${SIM_INPUTS}" ]; then
    printf "No SIM_INPUTS were provided.\n"
  else
    for input_path in ${SIM_INPUTS}; do
      if [ -e "${input_path}" ]; then
        if [ -d "${input_path}" ]; then
          printf "%s: present directory\n" "${input_path}"
        else
          printf "%s: present file\n" "${input_path}"
        fi
      else
        printf "%s: missing\n" "${input_path}"
      fi
    done
  fi
} > "${INPUT_REPORT}"

{
  printf "# Scientific Simulation Run Plan\n\n"
  printf -- '- Software: `%s`\n' "${SIM_SOFTWARE}"
  printf -- '- Created: `%s`\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  printf -- '- Host: `%s`\n' "$(hostname)"
  printf -- '- Working directory: `%s`\n' "$(pwd)"
  printf -- '- Output directory: `%s`\n' "${OUTPUT_DIR}"
  printf -- '- Detected scheduler context: `%s`\n' "${SCHEDULER_NAME}"
  if [ -n "${SCHEDULER_TEMPLATE}" ]; then
    printf -- '- Scheduler template: `%s`\n' "${SCHEDULER_TEMPLATE}"
  else
    printf -- "- Scheduler template: not provided\n"
  fi
  if [ -n "${EXECUTABLE_NAME}" ]; then
    if command -v "${EXECUTABLE_NAME}" >/dev/null 2>&1; then
      printf -- '- Executable check: `%s` found\n' "${EXECUTABLE_NAME}"
    else
      printf -- '- Executable check: `%s` not found in PATH\n' "${EXECUTABLE_NAME}"
    fi
  else
    printf -- "- Executable check: no executable provided\n"
  fi
  if [ -n "${SIM_COMMAND}" ]; then
    printf -- '- Simulation command: `%s`\n' "${SIM_COMMAND}"
  else
    printf -- "- Simulation command: not provided\n"
  fi
  if [ -n "${POSTPROCESS_COMMAND}" ]; then
    printf -- '- Post-process command: `%s`\n' "${POSTPROCESS_COMMAND}"
  else
    printf -- "- Post-process command: not provided\n"
  fi
  printf "\n## Input Checks\n\n"
  sed 's/^/- /' "${INPUT_REPORT}"
  printf "\n## Suggested Launch Notes\n\n"
  printf -- "- Review the domain-specific skill for this software before production scale.\n"
  printf -- "- Run a short smoke case before full input data or long walltimes.\n"
  printf -- "- Keep launch, simulation output, and post-processing logs in separate files.\n"
  if [ -n "${SCHEDULER_TEMPLATE}" ]; then
    printf -- '- Slurm suggestion: `sbatch %s`\n' "${SCHEDULER_TEMPLATE}"
    printf -- '- PBS suggestion: `qsub %s`\n' "${SCHEDULER_TEMPLATE}"
    printf -- '- LSF suggestion: `bsub < %s`\n' "${SCHEDULER_TEMPLATE}"
  fi
  printf "\n## Execution Guard\n\n"
  printf -- '- RUN_SIMULATION: `%s`\n' "${RUN_SIMULATION}"
  printf -- '- RUN_POSTPROCESS: `%s`\n' "${RUN_POSTPROCESS}"
} > "${PLAN_FILE}"

{
  printf "Scientific simulation reproducibility notes\n"
  printf "Created: %s\n" "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  printf "Host: %s\n" "$(hostname)"
  printf "Kernel: %s\n" "$(uname -a)"
  printf "Working directory: %s\n" "$(pwd)"
  printf "Scheduler context: %s\n" "${SCHEDULER_NAME}"
  printf "\nSelected runtime environment variables:\n"
  env | LC_ALL=C sort | grep -E '^(SLURM|PBS|LSB|OMP|MKL|OPENBLAS|BLIS|VECLIB|CUDA|HIP|ROCR|I_MPI|OMPI|MPICH|PMI|PMIX|UCX|FI_|NCCL|GMX|LAMMPS|QE|CP2K|WRF|WM_)' || true
  if command -v module >/dev/null 2>&1; then
    printf "\nModule command detected. Capture site module list inside the target job if needed.\n"
  else
    printf "\nModule command not detected in this shell.\n"
  fi
} > "${REPRO_FILE}"

{
  printf "RUN_SIMULATION=%s\n" "${RUN_SIMULATION}"
  if [ "${RUN_SIMULATION}" = "1" ]; then
    if [ -z "${SIM_COMMAND}" ]; then
      printf "No SIM_COMMAND provided; nothing to run.\n"
    else
      printf "Running SIM_COMMAND: %s\n" "${SIM_COMMAND}"
      bash -lc "${SIM_COMMAND}" 2>&1
      printf "SIM_COMMAND completed with exit code 0.\n"
    fi
  else
    printf "Plan-only mode. SIM_COMMAND was not executed.\n"
  fi

  printf "\nRUN_POSTPROCESS=%s\n" "${RUN_POSTPROCESS}"
  if [ "${RUN_POSTPROCESS}" = "1" ]; then
    if [ -z "${POSTPROCESS_COMMAND}" ]; then
      printf "No POSTPROCESS_COMMAND provided; nothing to run.\n"
    else
      printf "Running POSTPROCESS_COMMAND: %s\n" "${POSTPROCESS_COMMAND}"
      bash -lc "${POSTPROCESS_COMMAND}" 2>&1
      printf "POSTPROCESS_COMMAND completed with exit code 0.\n"
    fi
  else
    printf "Post-process plan-only mode. POSTPROCESS_COMMAND was not executed.\n"
  fi
} > "${COMMAND_LOG}"

printf "Wrote %s, %s, %s, and %s\n" \
  "${PLAN_FILE}" \
  "${INPUT_REPORT}" \
  "${REPRO_FILE}" \
  "${COMMAND_LOG}"
