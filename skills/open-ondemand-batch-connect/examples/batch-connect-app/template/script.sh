#!/usr/bin/env bash
set -euo pipefail

echo "ood_skill_batch_connect=${OOD_SKILL_BATCH_CONNECT:-0}"
echo "host=$(hostname)"
echo "pwd=${PWD}"
echo "date=$(date -Is)"
echo "tasks=${OOD_SKILL_TASKS:-1}"

if [ -n "${environment_setup:-}" ]; then
  echo "== requested environment setup =="
  printf "%s\n" "${environment_setup}"
fi

if [ "${RUN_PORTAL_APP:-0}" != "1" ]; then
  echo "Review-only skeleton. Replace template/script.sh with a site-approved launcher."
  echo "Set RUN_PORTAL_APP=1 only in a development app after portal review."
  sleep 5
  exit 0
fi

echo "No production service is defined in this skeleton."
echo "Replace this block with an approved command such as Jupyter, RStudio, or a custom web app."
sleep 30
