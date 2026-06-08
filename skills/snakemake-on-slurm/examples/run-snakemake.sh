#!/usr/bin/env bash
set -euo pipefail

profile_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/slurm-profile" && pwd)"

snakemake \
  --profile "${profile_dir}" \
  --jobs 20 \
  --printshellcmds
