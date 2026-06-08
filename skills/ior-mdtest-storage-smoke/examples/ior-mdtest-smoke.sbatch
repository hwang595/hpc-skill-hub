#!/usr/bin/env bash
#SBATCH --job-name=ior-mdtest-smoke
#SBATCH --account=<account>
#SBATCH --partition=<debug-partition>
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=ior-mdtest-smoke-%j.out

set -euo pipefail

bench_root="${BENCH_ROOT:-${SCRATCH:-$PWD}/ior-mdtest-smoke}"
bench_label="${BENCH_LABEL:-${SLURM_JOB_ID:-local}-$(date +%Y%m%d-%H%M%S)}"
run_dir="${RUN_DIR:-${bench_root}/${bench_label}}"
mpi_tasks="${SLURM_NTASKS:-4}"
mpi_launcher="${MPI_LAUNCHER:-srun}"
ior_block_size="${IOR_BLOCK_SIZE:-16m}"
ior_transfer_size="${IOR_TRANSFER_SIZE:-1m}"
ior_segments="${IOR_SEGMENTS:-4}"
mdtest_items="${MDTEST_ITEMS:-32}"
mdtest_iterations="${MDTEST_ITERATIONS:-1}"
mdtest_depth="${MDTEST_DEPTH:-0}"

echo "job_id=${SLURM_JOB_ID:-local}"
echo "host=$(hostname)"
echo "pwd=${PWD}"
echo "bench_root=${bench_root}"
echo "run_dir=${run_dir}"
echo "mpi_tasks=${mpi_tasks}"
echo "mpi_launcher=${mpi_launcher}"
echo "RUN_BENCHMARK=${RUN_BENCHMARK:-0}"

for tool in "${mpi_launcher}" ior mdtest python3 mkdir tee; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "ERROR: ${tool} is not available in PATH." >&2
    exit 1
  fi
done

mkdir -p "${run_dir}/ior" "${run_dir}/mdtest"
touch "${run_dir}/.hpc-skill-ior-mdtest-smoke"

{
  echo "date=$(date -Is)"
  echo "hostname=$(hostname)"
  echo "slurm_job_id=${SLURM_JOB_ID:-local}"
  echo "slurm_nodelist=${SLURM_NODELIST:-local}"
  echo "slurm_ntasks=${SLURM_NTASKS:-${mpi_tasks}}"
  echo "bench_root=${bench_root}"
  echo "run_dir=${run_dir}"
  echo "ior_block_size=${ior_block_size}"
  echo "ior_transfer_size=${ior_transfer_size}"
  echo "ior_segments=${ior_segments}"
  echo "mdtest_items=${mdtest_items}"
  echo "mdtest_iterations=${mdtest_iterations}"
  echo "mdtest_depth=${mdtest_depth}"
} | tee "${run_dir}/run-metadata.txt"

ior_command=(
  "${mpi_launcher}" -n "${mpi_tasks}" ior
  -a POSIX
  -F
  -w
  -r
  -t "${ior_transfer_size}"
  -b "${ior_block_size}"
  -s "${ior_segments}"
  -o "${run_dir}/ior/file"
)

mdtest_command=(
  "${mpi_launcher}" -n "${mpi_tasks}" mdtest
  -d "${run_dir}/mdtest"
  -n "${mdtest_items}"
  -i "${mdtest_iterations}"
  -z "${mdtest_depth}"
  -u
  -F
)

printf "ior_command=" | tee "${run_dir}/commands.txt"
printf "%q " "${ior_command[@]}" | tee -a "${run_dir}/commands.txt"
printf "\nmdtest_command=" | tee -a "${run_dir}/commands.txt"
printf "%q " "${mdtest_command[@]}" | tee -a "${run_dir}/commands.txt"
printf "\n" | tee -a "${run_dir}/commands.txt"

echo "== tool versions =="
ior --version 2>&1 | tee "${run_dir}/ior-version.txt" || true
mdtest --version 2>&1 | tee "${run_dir}/mdtest-version.txt" || true

if [ "${RUN_BENCHMARK:-0}" != "1" ]; then
  echo "Plan-only mode. Review site policy and set RUN_BENCHMARK=1 to run."
  exit 0
fi

echo "== running ior =="
"${ior_command[@]}" 2>&1 | tee "${run_dir}/ior.out"

echo "== running mdtest =="
"${mdtest_command[@]}" 2>&1 | tee "${run_dir}/mdtest.out"

echo "== summary =="
python3 "$(dirname "${BASH_SOURCE[0]}")/summarize-results.py" "${run_dir}" | tee "${run_dir}/summary.txt"

if [ "${CLEANUP_AFTER_RUN:-0}" = "1" ]; then
  echo "CLEANUP_AFTER_RUN=1 requested; review results first, then use cleanup-run.sh."
fi
