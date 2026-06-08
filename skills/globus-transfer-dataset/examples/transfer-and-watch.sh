#!/usr/bin/env bash
set -euo pipefail

src_collection="${1:?usage: transfer-and-watch.sh <src-collection> <src-path> <dst-collection> <dst-path>}"
src_path="${2:?usage: transfer-and-watch.sh <src-collection> <src-path> <dst-collection> <dst-path>}"
dst_collection="${3:?usage: transfer-and-watch.sh <src-collection> <src-path> <dst-collection> <dst-path>}"
dst_path="${4:?usage: transfer-and-watch.sh <src-collection> <src-path> <dst-collection> <dst-path>}"

task_id="$(
  globus transfer "${src_collection}:${src_path}" "${dst_collection}:${dst_path}" \
    --recursive \
    --preserve-mtime \
    --verify-checksum \
    --format unix
)"

echo "task_id=${task_id}"
globus task wait "${task_id}"
globus task show "${task_id}"
