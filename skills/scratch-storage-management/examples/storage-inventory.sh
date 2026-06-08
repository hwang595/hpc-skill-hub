#!/usr/bin/env bash
set -euo pipefail

target="${1:-.}"

if [ ! -d "${target}" ]; then
  echo "usage: storage-inventory.sh [directory]"
  echo "error: '${target}' is not a directory"
  exit 2
fi

echo "== target =="
cd "${target}"
pwd

echo
echo "== filesystem capacity =="
df -h .

echo
echo "== top-level usage, KiB =="
find . -mindepth 1 -maxdepth 1 -exec du -sk {} + 2>/dev/null \
  | sort -n \
  | tail -n 20

echo
echo "== large file candidates =="
find . -type f -size +1G -print 2>/dev/null | head -n 50

echo
echo "Review candidates before moving, archiving, or deleting anything."
