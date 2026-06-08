# BLAST On Slurm

Use this skill when a bioinformatics workflow needs local BLAST+ searches on a
Slurm-backed HPC system with explicit input, database, CPU, output, and run
record controls.

## Example

Create a dry-run launch plan with the tiny bundled FASTA files:

```bash
sbatch examples/blast-smoke.sbatch
```

After loading a site-approved BLAST+ module or environment, run the smoke test:

```bash
RUN_BLAST=1 sbatch examples/blast-smoke.sbatch
```

Adapt it to real inputs by setting explicit paths:

```bash
RUN_BLAST=1 \
BLAST_QUERY_FASTA=/path/to/query.fasta \
BLAST_REFERENCE_FASTA=/path/to/reference.fasta \
BLAST_OUT_DIR=/path/to/results \
  sbatch examples/blast-smoke.sbatch
```

## Pattern

- Use local BLAST+ searches for batch HPC workloads; avoid launching many
  remote BLAST jobs from Slurm arrays.
- Stage large query files and BLAST databases on scratch or project storage
  designed for the expected read load.
- Build or point to a versioned database and keep the database path in the run
  record.
- Match `BLAST_NUM_THREADS` to `SLURM_CPUS_PER_TASK`.
- Bound result size with explicit `BLAST_MAX_TARGET_SEQS`, `BLAST_EVALUE`, and
  `BLAST_OUTFMT`.
- Start with the tiny smoke test before using large production FASTA files.

## Safety Notes

This skill is `medium` risk because BLAST searches can use substantial CPU,
read large database files repeatedly, and create large output files. The Slurm
wrapper defaults to dry-run mode and runs BLAST only when `RUN_BLAST=1` is set.
Use short allocations for smoke tests, keep database reads off fragile home
filesystems, and follow site policy before using public NCBI databases.

## Success Criteria

- The dry-run log records the query, reference, local database path, BLAST
  program, CPU count, output format, and result path.
- With `RUN_BLAST=1`, `makeblastdb` creates a local database for the reference
  FASTA.
- The selected BLAST+ program writes a bounded result table.
- The run record is preserved with command, host, BLAST version, and Slurm
  allocation details.
