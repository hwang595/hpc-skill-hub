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

module purge
module load <mpi-module>

mpicc examples/hello_mpi.c -o hello_mpi
srun ./hello_mpi | sort
