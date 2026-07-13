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
run_benchmark="${RUN_BENCHMARK:-0}"

validate_integer() {
  name="$1"
  value="$2"
  minimum="$3"
  maximum="$4"
  if ! [[ "${value}" =~ ^[0-9]+$ ]] || [ "${value}" -lt "${minimum}" ] || [ "${value}" -gt "${maximum}" ]; then
    echo "ERROR: ${name} must be an integer from ${minimum} through ${maximum}; got ${value}." >&2
    exit 2
  fi
}

validate_size() {
  name="$1"
  value="$2"
  max_mib="$3"
  if ! [[ "${value}" =~ ^([1-9][0-9]*)([kKmMgG]?)$ ]]; then
    echo "ERROR: ${name} must be a positive integer with optional k, m, or g suffix." >&2
    exit 2
  fi
  amount="${BASH_REMATCH[1]}"
  unit="${BASH_REMATCH[2]}"
  case "${unit}" in
    k|K) limit=$((max_mib * 1024)) ;;
    m|M) limit="${max_mib}" ;;
    g|G) limit=$((max_mib / 1024)) ;;
    "") limit=$((max_mib * 1024 * 1024)) ;;
  esac
  if [ "${limit}" -lt 1 ] || [ "${amount}" -gt "${limit}" ]; then
    echo "ERROR: ${name}=${value} exceeds the ${max_mib} MiB smoke-test cap." >&2
    exit 2
  fi
}

emit_metadata() {
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
}

validate_integer "SLURM_NTASKS" "${mpi_tasks}" 1 8
validate_integer "IOR_SEGMENTS" "${ior_segments}" 1 8
validate_integer "MDTEST_ITEMS" "${mdtest_items}" 1 256
validate_integer "MDTEST_ITERATIONS" "${mdtest_iterations}" 1 3
validate_integer "MDTEST_DEPTH" "${mdtest_depth}" 0 2
validate_size "IOR_BLOCK_SIZE" "${ior_block_size}" 64
validate_size "IOR_TRANSFER_SIZE" "${ior_transfer_size}" 8

if [ "${run_benchmark}" != "0" ] && [ "${run_benchmark}" != "1" ]; then
  echo "ERROR: RUN_BENCHMARK must be 0 or 1." >&2
  exit 2
fi

for tool in "${mpi_launcher}" ior mdtest python3 mkdir tee; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    echo "ERROR: ${tool} is not available in PATH." >&2
    exit 1
  fi
done

ior_command=(
  "${mpi_launcher}" -n "${mpi_tasks}" ior
  -a POSIX -F -w -r
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
  -u -F
)

echo "== metadata =="
emit_metadata
echo "RUN_BENCHMARK=${run_benchmark}"
echo "CONFIRM_STORAGE_POLICY=${CONFIRM_STORAGE_POLICY:-0}"

echo "== exact commands =="
printf "ior_command="
printf "%q " "${ior_command[@]}"
printf "\nmdtest_command="
printf "%q " "${mdtest_command[@]}"
printf "\n"

echo "== tool versions =="
ior --version 2>&1 || true
mdtest --version 2>&1 || true

if [ "${run_benchmark}" = "0" ]; then
  echo "Plan-only mode. No directories or files were created."
  exit 0
fi

if [ "${CONFIRM_STORAGE_POLICY:-0}" != "1" ]; then
  echo "ERROR: set CONFIRM_STORAGE_POLICY=1 only after local benchmark policy review." >&2
  exit 2
fi
if [ ! -d "${bench_root}" ] || [ ! -w "${bench_root}" ]; then
  echo "ERROR: BENCH_ROOT must be an existing writable directory." >&2
  exit 2
fi
if [ -e "${run_dir}" ]; then
  echo "ERROR: run directory already exists: ${run_dir}" >&2
  exit 2
fi

mkdir -p "${run_dir}/ior" "${run_dir}/mdtest"
touch "${run_dir}/.hpc-skill-ior-mdtest-smoke"
emit_metadata > "${run_dir}/run-metadata.txt"
{
  printf "ior_command="
  printf "%q " "${ior_command[@]}"
  printf "\nmdtest_command="
  printf "%q " "${mdtest_command[@]}"
  printf "\n"
} > "${run_dir}/commands.txt"

ior --version > "${run_dir}/ior-version.txt" 2>&1 || true
mdtest --version > "${run_dir}/mdtest-version.txt" 2>&1 || true

echo "== running ior =="
"${ior_command[@]}" 2>&1 | tee "${run_dir}/ior.out"

echo "== running mdtest =="
"${mdtest_command[@]}" 2>&1 | tee "${run_dir}/mdtest.out"

echo "== summary =="
python3 "$(dirname "${BASH_SOURCE[0]}")/summarize-results.py" "${run_dir}" | tee "${run_dir}/summary.txt"
