#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: fd-limit-triage.sh [pid] [log-file]

Collect read-only file descriptor and nofile-limit evidence. If no PID is
provided, the script inspects the current shell process.
USAGE
}

pid="${1:-$$}"
log_file="${2:-}"
start_dir="$(pwd)"

if [[ "${pid}" == "-h" || "${pid}" == "--help" ]]; then
  usage
  exit 0
fi

if ! [[ "${pid}" =~ ^[0-9]+$ ]]; then
  echo "ERROR: pid must be numeric: ${pid}" >&2
  exit 2
fi

case "${log_file}" in
  ""|/*) ;;
  *) log_file="${start_dir}/${log_file}" ;;
esac

echo "File descriptor limit triage"
echo "============================"
echo
printf 'pid=%s\n' "${pid}"
printf 'log_file=%s\n' "${log_file:-<not-provided>}"

echo
echo "== current shell nofile limits =="
printf 'ulimit_soft_nofile=%s\n' "$(ulimit -n)"
printf 'ulimit_hard_nofile=%s\n' "$(ulimit -Hn 2>/dev/null || printf 'unavailable')"
echo
echo "ulimit -a:"
ulimit -a || true

echo
echo "== proc limits, if available =="
if [[ -r "/proc/${pid}/limits" ]]; then
  grep -E "Max open files|Limit|open files" "/proc/${pid}/limits" || true
else
  echo "/proc/${pid}/limits is not readable or this is not a Linux procfs system"
fi

echo
echo "== open fd count, if available =="
if [[ -d "/proc/${pid}/fd" ]]; then
  fd_count="$(ls -1 "/proc/${pid}/fd" 2>/dev/null | wc -l | tr -d ' ')"
  printf 'proc_fd_count=%s\n' "${fd_count}"
elif [[ -d "/dev/fd" && "${pid}" == "$$" ]]; then
  fd_count="$(ls -1 /dev/fd 2>/dev/null | wc -l | tr -d ' ')"
  printf 'current_shell_dev_fd_count=%s\n' "${fd_count}"
else
  echo "fd directory is not readable for pid ${pid}"
fi

echo
echo "== lsof count, if available =="
if command -v lsof >/dev/null 2>&1; then
  lsof_count="$(lsof -p "${pid}" 2>/dev/null | wc -l | tr -d ' ' || true)"
  if [[ -n "${lsof_count}" ]]; then
    printf 'lsof_line_count_including_header=%s\n' "${lsof_count}"
  else
    echo "lsof did not return data for pid ${pid}"
  fi
else
  echo "lsof command is not available on this system"
fi

if [[ -n "${log_file}" ]]; then
  echo
  echo "== recent log lines =="
  if command -v tail >/dev/null 2>&1; then
    tail -n 80 "${log_file}" || true
  else
    echo "tail command is not available on this system"
  fi

  echo
  echo "== file descriptor log clues =="
  if command -v grep >/dev/null 2>&1; then
    grep -Ein "too many open files|emfile|rlimit_nofile|nofile|file descriptor|ulimit|unable to open|failed to open|cannot open|open\\(" "${log_file}" || true
  else
    echo "grep command is not available on this system"
  fi
fi

cat <<'PROMPTS'

== review prompts ==
- Compare open fd count with the soft nofile limit. Near-limit counts point to descriptor pressure.
- Count outer fan-out: MPI ranks, workflow tasks, Python/R workers, data-loader workers, or array tasks.
- Look for one process leaking descriptors versus many processes each opening a moderate number.
- Many-small-file datasets may need batching, packing, sharding, or different staging, not only a higher limit.
- Limit changes are site policy decisions; include redacted evidence when asking support.
PROMPTS
