#!/usr/bin/env bash
set -euo pipefail

image="${1:?usage: inspect-image.sh <image.sif>}"

apptainer inspect "${image}"
echo
apptainer exec "${image}" id
echo
apptainer exec "${image}" /bin/sh -lc 'pwd; ls -la | head'
