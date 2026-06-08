#!/usr/bin/env bash
#SBATCH --job-name=apptainer-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%j.out

set -euo pipefail

image="<image.sif>"
workdir="${SLURM_SUBMIT_DIR:-$PWD}"

apptainer exec \
  --cleanenv \
  --bind "${workdir}:/work" \
  --pwd /work \
  "${image}" \
  /bin/sh -lc 'hostname; id; pwd; python3 --version || true'
