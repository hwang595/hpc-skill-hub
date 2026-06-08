#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s <target-path> [output-dir]\n' "$0"
  printf '\n'
  printf 'Collect read-only Lustre layout evidence and write a review-only stripe plan.\n'
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ "$#" -lt 1 ]; then
  usage >&2
  exit 2
fi

target_path="$1"
output_dir="${2:-lustre-layout-report-$(date -u +%Y%m%dT%H%M%SZ)}"

if [ ! -e "${target_path}" ]; then
  printf 'Target path not found: %s\n' "${target_path}" >&2
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
    printf '\nWARN: command exited non-zero; inspect this output before relying on it.\n' >>"${output_file}"
  }
}

missing_tool() {
  local output_file="$1"
  local tool_name="$2"
  {
    printf 'MISSING: %s was not found in PATH.\n' "${tool_name}"
    printf 'Load the site Lustre client tools or run this report from a Lustre client node.\n'
  } >"${output_file}"
}

if command -v lfs >/dev/null 2>&1; then
  capture "${output_dir}/lfs-getstripe.txt" lfs getstripe "${target_path}"
  capture "${output_dir}/lfs-df.txt" lfs df -h "${target_path}"
  capture "${output_dir}/lfs-osts.txt" lfs osts "${target_path}"
  if [ -d "${target_path}" ]; then
    capture "${output_dir}/lfs-getstripe-directory-default.txt" lfs getstripe -d "${target_path}"
  fi
else
  missing_tool "${output_dir}/lfs-getstripe.txt" "lfs"
  missing_tool "${output_dir}/lfs-df.txt" "lfs"
  missing_tool "${output_dir}/lfs-osts.txt" "lfs"
  if [ -d "${target_path}" ]; then
    missing_tool "${output_dir}/lfs-getstripe-directory-default.txt" "lfs"
  fi
fi

capture "${output_dir}/df-capacity.txt" df -h "${target_path}"
capture "${output_dir}/df-inodes.txt" df -i "${target_path}"
capture "${output_dir}/stat.txt" stat "${target_path}"

if [ -d "${target_path}" ] && command -v find >/dev/null 2>&1 && command -v head >/dev/null 2>&1; then
  {
    printf '$ find %q -maxdepth 1 -type f -size +1G -print | head -n 100\n\n' "${target_path}"
    find "${target_path}" -maxdepth 1 -type f -size +1G -print | head -n 100
  } >"${output_dir}/large-file-sample.txt" 2>&1 || {
    printf '\nWARN: large-file sample failed; inspect permissions and path type.\n' >>"${output_dir}/large-file-sample.txt"
  }
fi

{
  printf '# Lustre Stripe Layout Plan\n\n'
  printf '%s\n' "- Target path: \`${target_path}\`"
  printf '%s\n\n' "- Generated at: \`$(date -u +%Y-%m-%dT%H:%M:%SZ)\`"
  printf '## Evidence To Review\n\n'
  printf '%s\n' '- `lfs-getstripe.txt`: current layout for the file or directory.'
  printf '%s\n' '- `lfs-getstripe-directory-default.txt`: default layout inherited by new files when the target is a directory.'
  printf '%s\n' '- `lfs-df.txt`: Lustre MDT and OST capacity when `lfs df` is available.'
  printf '%s\n' '- `large-file-sample.txt`: bounded sample of large files directly under the directory.'
  printf '%s\n\n' '- `df-capacity.txt`, `df-inodes.txt`, and `stat.txt`: portable filesystem context.'
  printf '## Workload Pattern\n\n'
  printf '%s\n' '- Many small files: prefer fixing file count, batching, or application output pattern before wide striping.'
  printf '%s\n' '- One or a few large shared files: consider wider striping only after site policy and evidence review.'
  printf '%s\n' '- Per-rank files: a low stripe count per file may be better than wide striping every output.'
  printf '%s\n\n' '- Mixed-size output: check whether the site supports progressive file layouts.'
  printf '## Review-Only Commands\n\n'
  printf '```bash\n'
  printf '# Inspect current defaults again immediately before making changes.\n'
  printf 'lfs getstripe -d <empty-output-directory>\n\n'
  printf '# Example only: set default stripe layout for new files in an empty output directory.\n'
  printf 'lfs setstripe -c <stripe-count> -S <stripe-size> <empty-output-directory>\n\n'
  printf '# Example only: create a new file with an explicit layout before writing data.\n'
  printf 'lfs setstripe -c <stripe-count> -S <stripe-size> <new-output-file>\n'
  printf '```\n\n'
  printf '## Guardrails\n\n'
  printf '%s\n' '- Do not apply these commands until local Lustre policy, expected file sizes, and concurrency are reviewed.'
  printf '%s\n' '- Prefer changing a new empty output directory rather than an existing shared workflow root.'
  printf '%s\n' '- Avoid explicit OST indices unless storage support asks for them.'
  printf '%s\n' '- Treat `lfs migrate` as a separate, higher-impact operation that needs its own plan.'
} >"${output_dir}/stripe-plan.md"

printf 'Lustre layout report written to %s\n' "${output_dir}"
