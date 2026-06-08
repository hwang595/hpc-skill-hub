#!/usr/bin/env bash
set -euo pipefail

env_name="${1:-my-hpc-env}"
manifest_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

spack env create "${env_name}" "${manifest_dir}/spack.yaml"
spack env activate "${env_name}"
spack concretize

echo "Review the concrete specs. Install with:"
echo "spack install"
