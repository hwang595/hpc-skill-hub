#!/usr/bin/env bash
#SBATCH --job-name=blast-smoke
#SBATCH --account=<account>
#SBATCH --partition=<partition>
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=blast-smoke-%j.out

set -euo pipefail

record_dir="${BLAST_RECORD_DIR:-blast-record-${SLURM_JOB_ID:-local}}"
query_fasta="${BLAST_QUERY_FASTA:-examples/query.fasta}"
reference_fasta="${BLAST_REFERENCE_FASTA:-examples/reference.fasta}"
db_dir="${BLAST_DB_DIR:-${record_dir}/db}"
out_dir="${BLAST_OUT_DIR:-${record_dir}/out}"
db_name="${BLAST_DB_NAME:-smoke-reference}"
blast_program="${BLAST_PROGRAM:-blastn}"
blast_db_type="${BLAST_DB_TYPE:-nucl}"
num_threads="${BLAST_NUM_THREADS:-${SLURM_CPUS_PER_TASK:-1}}"
max_target_seqs="${BLAST_MAX_TARGET_SEQS:-5}"
evalue="${BLAST_EVALUE:-1e-5}"
outfmt="${BLAST_OUTFMT:-6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore}"
db_path="${db_dir}/${db_name}"
result_file="${out_dir}/blast-results.tsv"
log_file="${record_dir}/blast-smoke.log"

mkdir -p "${record_dir}" "${db_dir}" "${out_dir}"

{
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "record_dir=${record_dir}"
  echo "RUN_BLAST=${RUN_BLAST:-0}"
  echo
  echo "== scheduler layout =="
  echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
  echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
  echo "SLURM_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK:-1}"
  echo
  echo "== inputs and outputs =="
  echo "query_fasta=${query_fasta}"
  echo "reference_fasta=${reference_fasta}"
  echo "blast_program=${blast_program}"
  echo "blast_db_type=${blast_db_type}"
  echo "db_path=${db_path}"
  echo "result_file=${result_file}"
  echo "num_threads=${num_threads}"
  echo "max_target_seqs=${max_target_seqs}"
  echo "evalue=${evalue}"
  echo "outfmt=${outfmt}"

  if [ ! -s "${query_fasta}" ]; then
    echo "ERROR: query FASTA is missing or empty: ${query_fasta}" >&2
    exit 1
  fi
  if [ ! -s "${reference_fasta}" ]; then
    echo "ERROR: reference FASTA is missing or empty: ${reference_fasta}" >&2
    exit 1
  fi

  echo
  echo "== selected environment =="
  if command -v makeblastdb >/dev/null 2>&1; then
    echo "makeblastdb=$(command -v makeblastdb)"
    makeblastdb -version || true
  else
    echo "makeblastdb=not_found"
  fi
  if command -v "${blast_program}" >/dev/null 2>&1; then
    echo "${blast_program}=$(command -v "${blast_program}")"
    "${blast_program}" -version || true
  else
    echo "${blast_program}=not_found"
  fi

  echo
  echo "== launch command =="
  cat <<PLAN
makeblastdb -in "${reference_fasta}" -dbtype "${blast_db_type}" -out "${db_path}" -parse_seqids
${blast_program} -query "${query_fasta}" -db "${db_path}" -out "${result_file}" \\
  -outfmt "${outfmt}" -num_threads "${num_threads}" \\
  -max_target_seqs "${max_target_seqs}" -evalue "${evalue}"
PLAN

  if [ "${RUN_BLAST:-0}" = "1" ]; then
    command -v makeblastdb >/dev/null 2>&1
    command -v "${blast_program}" >/dev/null 2>&1

    makeblastdb -in "${reference_fasta}" \
      -dbtype "${blast_db_type}" \
      -out "${db_path}" \
      -parse_seqids

    "${blast_program}" \
      -query "${query_fasta}" \
      -db "${db_path}" \
      -out "${result_file}" \
      -outfmt "${outfmt}" \
      -num_threads "${num_threads}" \
      -max_target_seqs "${max_target_seqs}" \
      -evalue "${evalue}"

    echo "result_lines=$(wc -l < "${result_file}")"
  else
    echo "dry_run=true"
    echo "Set RUN_BLAST=1 only after reviewing paths, resources, and BLAST+ environment."
  fi

  echo "finished_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "log_file=${log_file}"
} 2>&1 | tee -a "${log_file}"
