#!/usr/bin/env bash
set -u

WORKSHOP_ID="${1:-training}"
PARTITION="${2:-}"
OUTPUT_DIR="${3:-training-preflight-$(date +%Y%m%d-%H%M%S)}"

mkdir -p "$OUTPUT_DIR"

command_line() {
  printf "%s" "$1"
  shift
  for part in "$@"; do
    printf " %s" "$part"
  done
  printf "\n"
}

run_report() {
  title="$1"
  output="$2"
  shift 2
  command_name="$1"

  {
    printf "# %s\n\n" "$title"
    printf "Generated: %s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf "Command: "
    command_line "$@"
    printf "\n"

    if ! command -v "$command_name" >/dev/null 2>&1; then
      printf "Skipped: %s is not available in this shell.\n" "$command_name"
      return 0
    fi

    "$@"
    status=$?
    printf "\nExit status: %s\n" "$status"
  } >"$output" 2>&1
}

if [ -n "$PARTITION" ]; then
  SINFO_ARGS=(sinfo --partition "$PARTITION" -l)
  SQUEUE_ARGS=(squeue --partition "$PARTITION" --format="%.18i %.9P %.40j %.12u %.2t %.10M %.6D %R")
else
  SINFO_ARGS=(sinfo -l)
  SQUEUE_ARGS=(squeue --format="%.18i %.9P %.40j %.12u %.2t %.10M %.6D %R")
fi

run_report "Training Partition Snapshot" "$OUTPUT_DIR/sinfo-training.txt" "${SINFO_ARGS[@]}"
run_report "Current Training Queue Snapshot" "$OUTPUT_DIR/squeue-training.txt" "${SQUEUE_ARGS[@]}"
run_report \
  "Recent Visible Training Accounting" \
  "$OUTPUT_DIR/sacct-recent.txt" \
  sacct --starttime "$(date -u +%F)" --format "JobID,JobName%40,User,Account,Partition,State,Elapsed,ExitCode" --parsable2

if command -v module >/dev/null 2>&1; then
  run_report "Currently Loaded Modules" "$OUTPUT_DIR/module-list.txt" module list
  run_report "Visible Modules" "$OUTPUT_DIR/module-avail.txt" module avail
else
  {
    printf "# Module Check\n\n"
    printf "Generated: %s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf "The module command is not available in this shell.\n"
  } >"$OUTPUT_DIR/module-check.txt"
fi

run_report "Filesystem Capacity Snapshot" "$OUTPUT_DIR/df-current-directory.txt" df -h .

{
  printf "# Common Teaching Tool Paths\n\n"
  printf "Generated: %s\n\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  for tool in bash git python python3 pip conda mamba apptainer singularity sbatch srun snakemake nextflow; do
    if command -v "$tool" >/dev/null 2>&1; then
      printf "%-12s %s\n" "$tool" "$(command -v "$tool")"
    else
      printf "%-12s %s\n" "$tool" "not found"
    fi
  done
} >"$OUTPUT_DIR/tool-paths.txt"

cat >"$OUTPUT_DIR/summary.md" <<SUMMARY
# Training Cluster Preflight

- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Workshop id: $WORKSHOP_ID
- Partition scope: ${PARTITION:-all visible partitions}

## Files

- sinfo-training.txt
- squeue-training.txt
- sacct-recent.txt
- module-list.txt or module-check.txt
- module-avail.txt, when module is available
- df-current-directory.txt
- tool-paths.txt

## Review Before Workshop

- Confirm the training partition, reservation, or queue policy is visible.
- Confirm short jobs can start before learners arrive.
- Confirm teaching modules, Python tools, containers, and workflow tools are
  visible from the instructor environment.
- Check filesystem capacity in the working directory used for examples.
- Keep cleanup and reset actions in a site-approved checklist or runbook.
SUMMARY

echo "Wrote read-only training preflight report to $OUTPUT_DIR"
