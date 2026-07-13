#!/usr/bin/env bash
set -euo pipefail

target="${1:-.}"
log_file="${2:-}"
start_dir="$(pwd)"

if [ "$#" -gt 2 ] || [ "${target}" = "-h" ] || [ "${target}" = "--help" ]; then
  echo "usage: filesystem-triage.sh [path] [log-file]"
  if [ "$#" -gt 2 ]; then
    exit 2
  fi
  exit 0
fi

case "${log_file}" in
  ""|/*) ;;
  *) log_file="${start_dir}/${log_file}" ;;
esac

if [ ! -e "${target}" ]; then
  echo "usage: filesystem-triage.sh [path] [log-file]"
  echo "error: '${target}' does not exist"
  exit 2
fi

if [ -n "${log_file}" ] && [ ! -f "${log_file}" ]; then
  echo "error: log file does not exist or is not a regular file: ${log_file}" >&2
  exit 2
fi

echo "== target =="
ls -ld -- "${target}"
if [ -d "${target}" ]; then
  cd "${target}"
else
  cd "$(dirname "${target}")"
fi
pwd

echo
echo "== filesystem capacity =="
df -h .

echo
echo "== inode usage =="
df -ih . || true

echo
echo "== quota, if available =="
if command -v quota >/dev/null 2>&1; then
  quota -s || true
else
  echo "quota command not available on this system"
fi

echo
echo "== write permission check for current directory =="
if [ -w . ]; then
  echo "current directory is writable by this user"
else
  echo "current directory is not writable by this user"
fi

if [ -n "${log_file}" ]; then
  echo
  echo "== recent log lines =="
  tail -n 80 "${log_file}"

  echo
  echo "== storage-related log clues =="
  grep -Ein "no space left|quota|inode|permission denied|read-only file system|input/output error|stale file handle|too many open files" "${log_file}" || true
fi
