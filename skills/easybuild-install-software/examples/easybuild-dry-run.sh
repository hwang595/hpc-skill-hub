#!/usr/bin/env bash
set -euo pipefail

easyconfig="${1:?usage: easybuild-dry-run.sh <easyconfig.eb>}"
installpath="${EASYBUILD_INSTALLPATH:-$HOME/easybuild}"

echo "Using EASYBUILD_INSTALLPATH=${installpath}"

eb "${easyconfig}" \
  --robot \
  --dry-run \
  --installpath="${installpath}"
