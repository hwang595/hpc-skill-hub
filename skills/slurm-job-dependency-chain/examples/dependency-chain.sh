#!/usr/bin/env bash
set -euo pipefail

mode="plan"
workdir="dependency-chain-demo"

usage() {
  cat <<'USAGE'
Usage: dependency-chain.sh [--plan|--submit] [work-dir]

Create a three-stage Slurm dependency-chain demo.
Default mode is --plan, which writes scripts and prints sbatch commands.
Use --submit only on a cluster where submitting three tiny jobs is acceptable.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --plan)
      mode="plan"
      shift
      ;;
    --submit)
      mode="submit"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      workdir="$1"
      shift
      ;;
  esac
done

if [[ "${mode}" != "plan" && "${mode}" != "submit" ]]; then
  echo "ERROR: mode must be --plan or --submit." >&2
  exit 2
fi

mkdir -p "${workdir}/logs"
workdir="$(cd "${workdir}" && pwd)"

write_stage() {
  local path="$1"
  local name="$2"
  local message="$3"

  cat > "${path}" <<SCRIPT
#!/usr/bin/env bash
#SBATCH --job-name=${name}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=512M
#SBATCH --time=00:02:00
#SBATCH --output=${workdir}/logs/%x-%j.out

set -euo pipefail

echo "stage=${name}"
echo "message=${message}"
echo "job_id=\${SLURM_JOB_ID:-not-submitted}"
echo "host=\$(hostname)"
date
sleep 5
SCRIPT

  chmod +x "${path}"
}

preprocess="${workdir}/01-preprocess.sbatch"
analysis="${workdir}/02-analysis.sbatch"
postprocess="${workdir}/03-postprocess.sbatch"

write_stage "${preprocess}" "dependency-preprocess" "Prepare small inputs"
write_stage "${analysis}" "dependency-analysis" "Run the main analysis"
write_stage "${postprocess}" "dependency-postprocess" "Collect logs and summarize"

echo "Dependency chain workspace: ${workdir}"
echo

if [[ "${mode}" == "plan" ]]; then
  cat <<PLAN
Plan only. No jobs were submitted.

Review these commands before using them on a cluster:

preprocess_id=\$(sbatch --parsable "${preprocess}")
analysis_id=\$(sbatch --parsable --dependency=afterok:\${preprocess_id} "${analysis}")
postprocess_id=\$(sbatch --parsable --dependency=afterany:\${analysis_id} "${postprocess}")

Optional singleton pattern for serializing jobs with the same name:

sbatch --parsable --dependency=singleton --job-name=dependency-preprocess "${preprocess}"
PLAN
  exit 0
fi

if ! command -v sbatch >/dev/null 2>&1; then
  echo "ERROR: sbatch is required for --submit mode." >&2
  exit 1
fi

preprocess_id="$(sbatch --parsable "${preprocess}")"
analysis_id="$(sbatch --parsable --dependency=afterok:"${preprocess_id}" "${analysis}")"
postprocess_id="$(sbatch --parsable --dependency=afterany:"${analysis_id}" "${postprocess}")"

cat <<SUBMITTED
Submitted dependency chain:

preprocess_id=${preprocess_id}
analysis_id=${analysis_id}   dependency=afterok:${preprocess_id}
postprocess_id=${postprocess_id} dependency=afterany:${analysis_id}

Logs will be written under:
${workdir}/logs
SUBMITTED

if command -v squeue >/dev/null 2>&1; then
  squeue --jobs="${preprocess_id},${analysis_id},${postprocess_id}"
fi
