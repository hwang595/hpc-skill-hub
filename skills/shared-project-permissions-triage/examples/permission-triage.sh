#!/usr/bin/env bash
set -euo pipefail

target="${1:-.}"
log_file="${2:-}"
start_dir="$(pwd)"

case "${target}" in
  /*) ;;
  *) target="${start_dir}/${target}" ;;
esac

case "${log_file}" in
  ""|/*) ;;
  *) log_file="${start_dir}/${log_file}" ;;
esac

if [ -e "${target}" ]; then
  inspect_path="${target}"
elif [ -e "$(dirname "${target}")" ]; then
  inspect_path="$(dirname "${target}")"
else
  echo "usage: permission-triage.sh [path] [log-file]"
  echo "error: neither '${target}' nor its parent exists"
  exit 2
fi

echo "== identity =="
id
echo
echo "groups:"
id -nG 2>/dev/null || true
echo
echo "umask:"
umask

echo
echo "== requested target =="
printf 'target=%s\n' "${target}"
if [ -e "${target}" ]; then
  printf 'target_exists=yes\n'
else
  printf 'target_exists=no\n'
  printf 'inspecting_parent=%s\n' "${inspect_path}"
fi

echo
echo "== target metadata =="
ls -ld "${inspect_path}"
stat "${inspect_path}" || true

if [ "${inspect_path}" != "/" ]; then
  parent="$(dirname "${inspect_path}")"
  echo
  echo "== parent metadata =="
  ls -ld "${parent}" || true
  stat "${parent}" || true
fi

echo
echo "== access tests for current user =="
for mode in read write execute; do
  case "${mode}" in
    read)
      flag="-r"
      ;;
    write)
      flag="-w"
      ;;
    execute)
      flag="-x"
      ;;
  esac

  if [ "${flag}" "${inspect_path}" ]; then
    printf '%s=yes\n' "${mode}"
  else
    printf '%s=no\n' "${mode}"
  fi
done

echo
echo "== path traversal =="
if command -v namei >/dev/null 2>&1; then
  namei -l "${target}" || true
else
  echo "namei command not available on this system"
fi

echo
echo "== acl, if available =="
if command -v getfacl >/dev/null 2>&1; then
  getfacl -p "${inspect_path}" || true
else
  echo "getfacl command not available on this system"
fi

echo
echo "== filesystem context, if available =="
if command -v df >/dev/null 2>&1; then
  df -h "${inspect_path}" || true
else
  echo "df command not available on this system"
fi

if [ -n "${log_file}" ]; then
  echo
  echo "== recent log lines =="
  if command -v tail >/dev/null 2>&1; then
    tail -n 80 "${log_file}" || true
  else
    echo "tail command not available on this system"
  fi

  echo
  echo "== permission-related log clues =="
  if command -v grep >/dev/null 2>&1; then
    grep -Ein "permission denied|operation not permitted|read-only file system|access denied|acl|group|owner|ownership|chmod|chgrp|setfacl|stale file handle|quota|no space left" "${log_file}" || true
  else
    echo "grep command not available on this system"
  fi
fi
