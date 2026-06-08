#!/usr/bin/env bash
#SBATCH --job-name=apptainer-mpi-bind
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --output=slurm-%j.out

set -euo pipefail

module purge
module load <mpi-module>

image="<image.sif>"
container_app="<container-app>"
mpi_dir="<mpi-install-prefix>"
workdir="${SLURM_SUBMIT_DIR:-$PWD}"
scratch="${TMPDIR:-$workdir}"
ranks="${SLURM_NTASKS:-1}"

echo "job_id=${SLURM_JOB_ID:-local}"
echo "nodes=${SLURM_JOB_NODELIST:-local}"
echo "ranks=${ranks}"
echo "mpi_dir=${mpi_dir}"
echo "image=${image}"

mpirun --version || true
apptainer exec --cleanenv --bind "${mpi_dir}:${mpi_dir}:ro" "${image}" /bin/sh -lc 'hostname; command -v mpirun || true'

mpirun -np "${ranks}" \
  apptainer exec \
    --cleanenv \
    --bind "${mpi_dir}:${mpi_dir}:ro" \
    --bind "${workdir}:/work" \
    --bind "${scratch}:/scratch" \
    --pwd /work \
    "${image}" \
    "${container_app}" --version
