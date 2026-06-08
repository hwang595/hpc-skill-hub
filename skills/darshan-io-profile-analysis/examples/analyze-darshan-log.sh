#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s <darshan-log> [output-dir]\n' "$0"
  printf '\n'
  printf 'Analyze an existing Darshan log with darshan-util commands.\n'
  printf 'Optional summaries are disabled unless RUN_DARSHAN_JOB_SUMMARY=1,\n'
  printf 'RUN_DARSHAN_PER_FILE=1, or RUN_DARSHAN_DXT=1 is set.\n'
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ "$#" -lt 1 ]; then
  usage >&2
  exit 2
fi

darshan_log="$1"
output_dir="${2:-darshan-io-analysis-$(date -u +%Y%m%dT%H%M%SZ)}"

if [ ! -f "${darshan_log}" ]; then
  printf 'Darshan log not found: %s\n' "${darshan_log}" >&2
  exit 1
fi

mkdir -p "${output_dir}"

capture() {
  local output_file="$1"
  shift
  {
    printf '$'
    printf ' %q' "$@"
    printf '\n\n'
    "$@"
  } >"${output_file}" 2>&1 || {
    printf '\nWARN: command exited non-zero; inspect the log above before relying on this output.\n' >>"${output_file}"
  }
}

record_missing() {
  local output_file="$1"
  local tool_name="$2"
  {
    printf 'MISSING: %s was not found in PATH.\n' "${tool_name}"
    printf 'Load a Darshan/darshan-util module or install darshan-util, then rerun this script.\n'
  } >"${output_file}"
}

if command -v darshan-parser >/dev/null 2>&1; then
  capture "${output_dir}/darshan-parser.txt" darshan-parser "${darshan_log}"
  capture "${output_dir}/darshan-parser-perf.txt" darshan-parser --perf "${darshan_log}"
  capture "${output_dir}/darshan-parser-file.txt" darshan-parser --file "${darshan_log}"
  capture "${output_dir}/darshan-parser-total.txt" darshan-parser --total "${darshan_log}"
else
  record_missing "${output_dir}/darshan-parser.txt" "darshan-parser"
fi

if command -v darshan-config >/dev/null 2>&1; then
  capture "${output_dir}/darshan-config-version.txt" darshan-config --version
  capture "${output_dir}/darshan-config-log-path.txt" darshan-config --log-path
else
  record_missing "${output_dir}/darshan-config.txt" "darshan-config"
fi

if [ "${RUN_DARSHAN_JOB_SUMMARY:-0}" = "1" ]; then
  if command -v darshan-job-summary.pl >/dev/null 2>&1; then
    capture "${output_dir}/darshan-job-summary.log" \
      darshan-job-summary.pl "${darshan_log}" --output "${output_dir}/darshan-job-summary.pdf"
  else
    record_missing "${output_dir}/darshan-job-summary.log" "darshan-job-summary.pl"
  fi
fi

if [ "${RUN_DARSHAN_PER_FILE:-0}" = "1" ]; then
  if command -v darshan-summary-per-file.sh >/dev/null 2>&1; then
    capture "${output_dir}/darshan-summary-per-file.log" \
      darshan-summary-per-file.sh "${darshan_log}" "${output_dir}/per-file-summaries"
  else
    record_missing "${output_dir}/darshan-summary-per-file.log" "darshan-summary-per-file.sh"
  fi
fi

if [ "${RUN_DARSHAN_DXT:-0}" = "1" ]; then
  if command -v darshan-dxt-parser >/dev/null 2>&1; then
    capture "${output_dir}/darshan-dxt-parser.txt" darshan-dxt-parser "${darshan_log}"
  else
    record_missing "${output_dir}/darshan-dxt-parser.txt" "darshan-dxt-parser"
  fi
fi

{
  printf '# Darshan I/O Review Notes\n\n'
  printf '%s\n' "- Log analyzed: \`${darshan_log}\`"
  printf '%s\n' "- Output directory: \`${output_dir}\`"
  printf '%s\n\n' "- Generated at: \`$(date -u +%Y-%m-%dT%H:%M:%SZ)\`"
  printf '## First Questions\n\n'
  printf '%s\n' '- Does the log match the intended job, executable, scale, and filesystem?'
  printf '%s\n' '- Are POSIX, MPI-IO, HDF5, or PnetCDF modules present for the expected I/O path?'
  printf '%s\n' '- Is the job dominated by a few shared files, many small files, metadata calls, or rank imbalance?'
  printf '%s\n' '- Are reads and writes aligned with the application phase being investigated?'
  printf '%s\n\n' '- Do paths, user ids, job ids, executable names, or filenames need redaction before sharing?'
  printf '## Evidence To Compare\n\n'
  printf '%s\n' '- `darshan-parser.txt`: full text dump when `darshan-parser` is available.'
  printf '%s\n' '- `darshan-parser-perf.txt`: high-level performance counters when supported.'
  printf '%s\n' '- `darshan-parser-file.txt`: file-oriented summary when supported.'
  printf '%s\n' '- `darshan-parser-total.txt`: aggregate totals when supported.'
  printf '%s\n\n' '- `darshan-config-log-path.txt`: default runtime log path when `darshan-config` exposes it.'
  printf '## Interpretation Guardrails\n\n'
  printf '%s\n' '- Treat this as workload characterization, not a filesystem benchmark.'
  printf '%s\n' '- Compare against application expectations before changing striping, buffering, or I/O libraries.'
  printf '%s\n' '- Review site policy before enabling new instrumentation, DXT tracing, or collecting production logs.'
} >"${output_dir}/review-notes.md"

{
  printf '# Optional Darshan Summary Commands\n\n'
  printf '# Review before running. These commands may create PDFs, many per-file outputs, or detailed traces.\n'
  printf 'RUN_DARSHAN_JOB_SUMMARY=1 bash %q %q %q\n' "$0" "${darshan_log}" "${output_dir}/job-summary-run"
  printf 'RUN_DARSHAN_PER_FILE=1 bash %q %q %q\n' "$0" "${darshan_log}" "${output_dir}/per-file-run"
  printf 'RUN_DARSHAN_DXT=1 bash %q %q %q\n' "$0" "${darshan_log}" "${output_dir}/dxt-run"
} >"${output_dir}/optional-commands.sh"

printf 'Darshan analysis report written to %s\n' "${output_dir}"
