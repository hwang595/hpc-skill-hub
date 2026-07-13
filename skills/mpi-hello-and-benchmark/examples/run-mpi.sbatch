#!/usr/bin/env bash
#SBATCH --job-name=mpi-hello
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%j.out

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mpi_module="${HPC_SKILL_HUB_MPI_MODULE:-<mpi-module>}"
if [[ "${mpi_module}" == "<mpi-module>" ]]; then
  echo "ERROR: set HPC_SKILL_HUB_MPI_MODULE or replace <mpi-module> before submitting." >&2
  exit 2
fi

if ! command -v module >/dev/null 2>&1; then
  echo "ERROR: the module command is not available in this batch environment." >&2
  exit 2
fi

module purge
# Replace <mpi-module> with a site-approved MPI module before running.
module load "${mpi_module}"

for command_name in mpicc srun; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "ERROR: ${command_name} is not available after loading ${mpi_module}." >&2
    exit 2
  fi
done

temp_root="${SLURM_TMPDIR:-${TMPDIR:-${PWD}}}"
build_dir="$(mktemp -d "${temp_root%/}/hpc-skill-mpi.XXXXXX")"
binary="${build_dir}/hello_mpi"

cleanup() {
  rm -f "${binary}"
  rmdir "${build_dir}" 2>/dev/null || true
}
trap cleanup EXIT

echo "compiler=$(command -v mpicc)"
echo "expected_tasks=${SLURM_NTASKS:-unknown}"
mpicc -Wall -Wextra -O0 "${script_dir}/hello_mpi.c" -o "${binary}"
srun "${binary}" | sort
