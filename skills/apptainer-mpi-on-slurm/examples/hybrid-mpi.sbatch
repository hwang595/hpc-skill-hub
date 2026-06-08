#!/usr/bin/env bash
#SBATCH --job-name=apptainer-mpi-hybrid
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%j.out

set -euo pipefail

image="<image.sif>"
container_app="<container-app>"
workdir="${SLURM_SUBMIT_DIR:-$PWD}"
scratch="${TMPDIR:-$workdir}"

echo "job_id=${SLURM_JOB_ID:-local}"
echo "nodes=${SLURM_JOB_NODELIST:-local}"
echo "ntasks=${SLURM_NTASKS:-1}"
echo "image=${image}"
echo "container_app=${container_app}"

apptainer exec --cleanenv "${image}" /bin/sh -lc 'hostname; command -v mpirun || true; command -v mpiexec || true'

srun \
  --ntasks="${SLURM_NTASKS:-1}" \
  apptainer exec \
    --cleanenv \
    --bind "${workdir}:/work" \
    --bind "${scratch}:/scratch" \
    --pwd /work \
    "${image}" \
    "${container_app}" --version
