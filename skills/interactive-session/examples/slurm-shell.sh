#!/usr/bin/env bash
set -euo pipefail

srun \
  --account=<account> \
  --partition=<debug-partition> \
  --nodes=1 \
  --ntasks=1 \
  --cpus-per-task=4 \
  --mem=8G \
  --time=00:30:00 \
  --pty bash -l
