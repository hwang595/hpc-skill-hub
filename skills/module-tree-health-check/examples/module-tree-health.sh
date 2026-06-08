#!/usr/bin/env bash
set -u

MODULE_QUERY="${1:-}"
OUTPUT_DIR="${2:-module-tree-health-$(date +%Y%m%d-%H%M%S)}"

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

  {
    printf "# %s\n\n" "$title"
    printf "Generated: %s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf "Command: "
    command_line "$@"
    printf "\n"

    "$@"
    status=$?
    printf "\nExit status: %s\n" "$status"
  } >"$output" 2>&1
}

if ! command -v module >/dev/null 2>&1; then
  {
    printf "# Module Command Check\n\n"
    printf "Generated: %s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf "The module command is not available in this shell.\n"
    printf "On many systems, run this from an initialized login shell.\n"
  } >"$OUTPUT_DIR/module-command.txt"
else
  run_report "Module Version" "$OUTPUT_DIR/module-version.txt" module --version
  run_report "Currently Loaded Modules" "$OUTPUT_DIR/module-list.txt" module list
  run_report "Visible Module Tree" "$OUTPUT_DIR/module-avail.txt" module avail

  if [ -n "$MODULE_QUERY" ]; then
    run_report "Module Spider Query" "$OUTPUT_DIR/module-spider.txt" module spider "$MODULE_QUERY"
    run_report "Module Whatis Query" "$OUTPUT_DIR/module-whatis.txt" module whatis "$MODULE_QUERY"
  fi
fi

{
  printf "# MODULEPATH\n\n"
  printf "Generated: %s\n\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  if [ -n "${MODULEPATH:-}" ]; then
    printf "%s\n" "$MODULEPATH" | tr ':' '\n'
  else
    printf "MODULEPATH is empty or unset.\n"
  fi
} >"$OUTPUT_DIR/modulepath.txt"

{
  printf "# Common Tool Paths\n\n"
  printf "Generated: %s\n\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  for tool in gcc g++ gfortran cc c++ mpicc mpicxx mpifort mpirun srun python python3 pip conda mamba cmake make nvcc hipcc; do
    if command -v "$tool" >/dev/null 2>&1; then
      printf "%-10s %s\n" "$tool" "$(command -v "$tool")"
    else
      printf "%-10s %s\n" "$tool" "not found"
    fi
  done
} >"$OUTPUT_DIR/tool-paths.txt"

cat >"$OUTPUT_DIR/summary.md" <<SUMMARY
# Module Tree Health Check

- Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Module query: ${MODULE_QUERY:-none}

## Files

- module-command.txt, when the module command is unavailable
- module-version.txt
- module-list.txt
- module-avail.txt
- module-spider.txt, when a module query is provided
- module-whatis.txt, when a module query is provided
- modulepath.txt
- tool-paths.txt

## Review Before Sharing

- Check for private install paths, licensed software names, internal module
  tree layout, and site-specific naming policy.
- Compare visible modules against public documentation or support tickets.
- Escalate to software-stack maintainers if module visibility differs between
  login nodes, compute nodes, or user groups.
SUMMARY

echo "Wrote read-only module tree health report to $OUTPUT_DIR"
