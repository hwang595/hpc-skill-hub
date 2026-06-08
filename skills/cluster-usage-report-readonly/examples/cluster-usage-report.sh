#!/usr/bin/env bash
set -u

DAYS="${1:-14}"
ACCOUNT="${2:-}"
OUTPUT_DIR="${3:-usage-report-$(date +%Y%m%d-%H%M%S)}"

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

SACCT_ARGS=(
  sacct
  --starttime "$START_DATE"
  --endtime "$END_DATE"
  --format "User,Account,JobID,JobName%40,Partition,State,Elapsed,TotalCPU,AllocCPUS,ReqMem,MaxRSS"
  --parsable2
)

if [ -n "$ACCOUNT" ]; then
  SACCT_ARGS+=(--account "$ACCOUNT")
fi

run_report \
  "Visible Slurm Accounting Records" \
  "$OUTPUT_DIR/sacct-jobs.txt" \
  "${SACCT_ARGS[@]}"

run_report \
  "Slurm Cluster Utilization Summary" \
  "$OUTPUT_DIR/sreport-utilization.txt" \
  sreport cluster Utilization Start="$START_DATE" End="$END_DATE" --tres=cpu

run_report \
  "Current Queue Snapshot" \
  "$OUTPUT_DIR/squeue-current.txt" \
  squeue --states=RUNNING,PENDING --format="%.18i %.9P %.40j %.12u %.2t %.10M %.6D %R"

run_report \
  "Partition And Node-State Snapshot" \
  "$OUTPUT_DIR/sinfo-partitions.txt" \
  sinfo --format="%20P %10a %8l %10D %10t %N"

cat >"$OUTPUT_DIR/summary.md" <<SUMMARY
# Cluster Usage Report

- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Window: $START_DATE through $END_DATE
- Days requested: $DAYS
- Account filter: ${ACCOUNT:-none}

## Files

- sacct-jobs.txt
- sreport-utilization.txt
- squeue-current.txt
- sinfo-partitions.txt

## Review Before Sharing

- Check for usernames, account names, project names, job names, hostnames, and
  non-public partition details.
- Confirm that any cluster-wide or account-wide data is approved for the
  intended audience.
- Summarize or redact sensitive fields before public release.
SUMMARY

echo "Wrote read-only Slurm usage report to $OUTPUT_DIR"
