#!/usr/bin/env bash
set -u

NODE_NAME="${1:-}"
DAYS="${2:-3}"
OUTPUT_DIR="${3:-node-triage-$(date +%Y%m%d-%H%M%S)}"

case "$DAYS" in
  ''|*[!0-9]*)
    echo "days must be a positive integer" >&2
    exit 2
    ;;
esac

if [ "$DAYS" -lt 1 ]; then
  echo "days must be at least 1" >&2
  exit 2
fi

start_date() {
  date -d "$DAYS days ago" +%F 2>/dev/null && return 0
  date -v-"$DAYS"d +%F 2>/dev/null && return 0
  return 1
}

START_DATE="$(start_date)"
if [ -z "$START_DATE" ]; then
  echo "could not compute start date with this system's date command" >&2
  exit 2
fi
END_DATE="$(date +%F)"

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
      printf "Skipped: %s is not available on this system.\n" "$command_name"
      return 0
    fi

    "$@"
    status=$?
    printf "\nExit status: %s\n" "$status"
  } >"$output" 2>&1
}

if [ -n "$NODE_NAME" ]; then
  SINFO_ARGS=(sinfo -N -n "$NODE_NAME" -l)
  SCONTROL_ARGS=(scontrol show node "$NODE_NAME")
  SQUEUE_ARGS=(squeue -w "$NODE_NAME" --format="%.18i %.9P %.40j %.12u %.2t %.10M %.6D %R")
  SACCT_ARGS=(
    sacct
    --starttime "$START_DATE"
    --endtime "$END_DATE"
    --nodelist "$NODE_NAME"
    --format "JobID,JobName%40,User,Account,State,Elapsed,ExitCode,NodeList"
    --parsable2
  )
else
  SINFO_ARGS=(sinfo -N -l)
  SCONTROL_ARGS=(scontrol show nodes)
  SQUEUE_ARGS=(squeue --states=RUNNING,PENDING --format="%.18i %.9P %.40j %.12u %.2t %.10M %.6D %R")
  SACCT_ARGS=(
    sacct
    --starttime "$START_DATE"
    --endtime "$END_DATE"
    --format "JobID,JobName%40,User,Account,State,Elapsed,ExitCode,NodeList"
    --parsable2
  )
fi

run_report \
  "Visible Slurm Node State" \
  "$OUTPUT_DIR/sinfo-nodes.txt" \
  "${SINFO_ARGS[@]}"

run_report \
  "Detailed Slurm Node Record" \
  "$OUTPUT_DIR/scontrol-node.txt" \
  "${SCONTROL_ARGS[@]}"

run_report \
  "Current Jobs On Node Scope" \
  "$OUTPUT_DIR/squeue-node.txt" \
  "${SQUEUE_ARGS[@]}"

run_report \
  "Recent Accounting On Node Scope" \
  "$OUTPUT_DIR/sacct-node.txt" \
  "${SACCT_ARGS[@]}"

cat >"$OUTPUT_DIR/summary.md" <<SUMMARY
# Node Health Readonly Triage

- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Node scope: ${NODE_NAME:-all visible nodes}
- Accounting window: $START_DATE through $END_DATE
- Days requested: $DAYS

## Files

- sinfo-nodes.txt
- scontrol-node.txt
- squeue-node.txt
- sacct-node.txt

## Review Before Sharing

- Check for users, accounts, job names, node names, private partitions, and
  scheduler reason strings.
- Confirm whether raw node-level evidence is approved for the intended
  audience.
- Escalate through the site's official operations process if the evidence
  suggests node, filesystem, network, or scheduler service impact.
SUMMARY

echo "Wrote read-only Slurm node triage report to $OUTPUT_DIR"
