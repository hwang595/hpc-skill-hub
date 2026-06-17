#!/usr/bin/env bash
#SBATCH --job-name=mpi-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%j.out

set -euo pipefail

module purge
# Replace <mpi-module> with a site-approved MPI module before running.
module load "<mpi-module>"

echo "job=${SLURM_JOB_ID}"
echo "nodes=${SLURM_JOB_NODELIST}"

# Replace with the real MPI executable.
srun hostname | sort
