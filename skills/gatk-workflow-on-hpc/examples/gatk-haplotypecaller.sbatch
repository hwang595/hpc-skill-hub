#!/usr/bin/env bash
#SBATCH --job-name=gatk-haplotypecaller
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=gatk-haplotypecaller-%j.out

set -euo pipefail

script_path="${BASH_SOURCE[0]}"
script_dir="${script_path%/*}"
if [ "${script_dir}" = "${script_path}" ]; then
  script_dir="."
fi
script_dir="$(cd "${script_dir}" && pwd)"

inputs_file="${GATK_INPUTS:-${script_dir}/inputs.env}"
env_sample_name="${SAMPLE_NAME:-}"
env_aligned_bam="${ALIGNED_BAM:-}"
env_reference_fasta="${REFERENCE_FASTA:-}"
env_intervals="${INTERVALS:-}"
env_output_dir="${OUTPUT_DIR:-}"
env_java_heap="${JAVA_HEAP:-}"
env_tmp_dir="${GATK_TMPDIR:-}"
env_record_dir="${GATK_RECORD_DIR:-}"

if [ -f "${inputs_file}" ]; then
  # shellcheck disable=SC1090
  . "${inputs_file}"
fi

if [ -n "${env_sample_name}" ]; then SAMPLE_NAME="${env_sample_name}"; fi
if [ -n "${env_aligned_bam}" ]; then ALIGNED_BAM="${env_aligned_bam}"; fi
if [ -n "${env_reference_fasta}" ]; then REFERENCE_FASTA="${env_reference_fasta}"; fi
if [ -n "${env_intervals}" ]; then INTERVALS="${env_intervals}"; fi
if [ -n "${env_output_dir}" ]; then OUTPUT_DIR="${env_output_dir}"; fi
if [ -n "${env_java_heap}" ]; then JAVA_HEAP="${env_java_heap}"; fi
if [ -n "${env_tmp_dir}" ]; then GATK_TMPDIR="${env_tmp_dir}"; fi
if [ -n "${env_record_dir}" ]; then GATK_RECORD_DIR="${env_record_dir}"; fi

aligned_bam="${ALIGNED_BAM:-}"
reference_fasta="${REFERENCE_FASTA:-}"
intervals="${INTERVALS:-}"
output_dir="${OUTPUT_DIR:-gatk-output}"
sample_name="${SAMPLE_NAME:-sample}"
java_heap="${JAVA_HEAP:-12g}"
tmp_dir="${GATK_TMPDIR:-${SLURM_TMPDIR:-gatk-tmp-${SLURM_JOB_ID:-local}}}"
record_dir="${GATK_RECORD_DIR:-gatk-record}"

mkdir -p "${output_dir}" "${tmp_dir}" "${record_dir}"
log_file="${record_dir}/gatk-plan-$(date -u +%Y%m%d-%H%M%S).log"
gvcf="${output_dir}/${sample_name}.g.vcf.gz"

check_file() {
  label="$1"
  path="$2"
  if [ -z "${path}" ]; then
    echo "missing_${label}=<not set>"
    return 1
  fi
  if [ -f "${path}" ]; then
    echo "${label}=${path}"
    return 0
  fi
  echo "missing_${label}=${path}"
  return 1
}

{
  echo "created_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "RUN_GATK=${RUN_GATK:-0}"
  echo "SAMPLE_NAME=${sample_name}"
  echo "OUTPUT_DIR=${output_dir}"
  echo "GATK_TMPDIR=${tmp_dir}"
  echo "JAVA_HEAP=${java_heap}"
  echo "SLURM_MEM_PER_NODE=${SLURM_MEM_PER_NODE:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-}"

  echo
  echo "== input checks =="
  input_ok=0
  check_file aligned_bam "${aligned_bam}" || input_ok=1
  if [ -n "${aligned_bam}" ]; then
    check_file aligned_bam_index "${aligned_bam}.bai" || true
  fi
  check_file reference_fasta "${reference_fasta}" || input_ok=1
  if [ -n "${reference_fasta}" ]; then
    check_file reference_fai "${reference_fasta}.fai" || true
    reference_prefix="${reference_fasta%.*}"
    dict_path="${reference_prefix}.dict"
    check_file reference_dict "${dict_path}" || true
  fi
  if [ -n "${intervals}" ]; then
    check_file intervals "${intervals}" || input_ok=1
  fi

  echo
  echo "== launch plan =="
  interval_args=()
  if [ -n "${intervals}" ]; then
    interval_args=(-L "${intervals}")
  fi
  command=(
    gatk
    --java-options "-Djava.io.tmpdir=${tmp_dir} -Xmx${java_heap}"
    HaplotypeCaller
    -R "${reference_fasta}"
    -I "${aligned_bam}"
    -O "${gvcf}"
    -ERC GVCF
  )
  if [ "${#interval_args[@]}" -gt 0 ]; then
    command+=("${interval_args[@]}")
  fi
  echo "command=${command[*]}"

  if [ "${RUN_GATK:-0}" = "1" ]; then
    if [ "${input_ok}" != "0" ]; then
      echo "error: required inputs are missing; refusing to run GATK"
      exit 2
    fi
    "${command[@]}"
  else
    echo "dry_run=true"
    echo "Set RUN_GATK=1 only after reviewing required inputs, reference files, and interval scope."
  fi

  echo "gvcf=${gvcf}"
  echo "log_file=${log_file}"
} 2>&1 | tee "${log_file}"
