#!/usr/bin/env bash
#SBATCH --job-name=mpi4py-demo
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail

export MPI_MODULE="${MPI_MODULE:-<mpi-module>}"
export PYTHON_SCRIPT="${PYTHON_SCRIPT:-examples/hello_mpi4py.py}"
export OUTPUT_DIR="${OUTPUT_DIR:-results}"
export MPI_LAUNCHER="${MPI_LAUNCHER:-srun}"

module purge
module load "${MPI_MODULE}"

mkdir -p logs "${OUTPUT_DIR}"

if [ -n "${PYTHON_ENV:-}" ]; then
  # shellcheck disable=SC1090
  . "${PYTHON_ENV}/bin/activate"
fi

echo "job=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "start=$(date -Iseconds)"
echo "PYTHON_SCRIPT=${PYTHON_SCRIPT}"
echo "OUTPUT_DIR=${OUTPUT_DIR}"
echo "MPI_MODULE=${MPI_MODULE}"
echo "MPI_LAUNCHER=${MPI_LAUNCHER}"
echo "SLURM_NTASKS=${SLURM_NTASKS:-unset}"
echo "SLURM_NTASKS_PER_NODE=${SLURM_NTASKS_PER_NODE:-unset}"
echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-unset}"
echo "python=$(command -v python)"
python --version

python - <<'PY'
import sys
from mpi4py import MPI

print("mpi4py import: ok")
print("python executable:", sys.executable)
print("mpi4py version:", __import__("mpi4py").__version__)
print("MPI version:", MPI.Get_version())
print("MPI library version:")
print(MPI.Get_library_version())
PY

if [ "${MPI_LAUNCHER}" = "srun" ]; then
  srun python "${PYTHON_SCRIPT}" "${OUTPUT_DIR}"
else
  "${MPI_LAUNCHER}" -n "${SLURM_NTASKS:-4}" python "${PYTHON_SCRIPT}" "${OUTPUT_DIR}"
fi

echo "end=$(date -Iseconds)"
