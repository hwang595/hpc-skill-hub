#!/usr/bin/env bash
set -euo pipefail

days="${1:-30}"
start_date="$(date -v-"${days}"d +%Y-%m-%d 2>/dev/null || date -d "${days} days ago" +%Y-%m-%d)"

sacct \
  --starttime="${start_date}" \
  --format=JobID,JobName%30,State,ExitCode,Elapsed,Timelimit,AllocCPUS,ReqMem,MaxRSS \
  --parsable2
