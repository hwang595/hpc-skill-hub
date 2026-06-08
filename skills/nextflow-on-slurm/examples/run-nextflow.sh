#!/usr/bin/env bash
set -euo pipefail

pipeline="${1:-hello}"

nextflow run "${pipeline}" \
  -profile slurm \
  -with-trace \
  -with-report \
  -with-timeline
