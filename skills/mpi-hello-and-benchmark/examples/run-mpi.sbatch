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

module purge
# Replace <mpi-module> with a site-approved MPI module before running.
module load "${mpi_module}"

mpicc "${script_dir}/hello_mpi.c" -o hello_mpi
srun ./hello_mpi | sort
