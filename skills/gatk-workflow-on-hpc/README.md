# GATK Workflow On HPC

Use this skill when a genomics workflow needs to run GATK on shared HPC
storage, with explicit Java memory, temporary directory, input, and reference
checks.

## Example

Create a launch plan:

```bash
bash examples/gatk-haplotypecaller.sbatch
```

After editing `examples/inputs.env` or setting the same environment variables,
run explicitly:

```bash
RUN_GATK=1 bash examples/gatk-haplotypecaller.sbatch
```

## Pattern

- Use a tiny interval first before whole-genome or cohort work.
- Keep Java temporary files on job scratch or a user-owned scratch directory.
- Record Java heap size separately from the Slurm memory request.
- Confirm BAM/CRAM indexes, reference FASTA indexes, and sequence dictionary
  are present before launching expensive work.
- Store outputs and logs on durable project storage.
- Use workflow engines such as WDL/Cromwell, Nextflow, or Snakemake when
  scaling scatter/gather and cohort analysis.

## Safety Notes

This skill is `medium` risk because GATK jobs can be CPU, memory, I/O, and
storage intensive. The example defaults to plan-only mode and runs
HaplotypeCaller only when `RUN_GATK=1` is set. Logs and manifests may contain
private sample names and dataset paths.

## Success Criteria

- The plan records reference, input, interval, output, Java heap, temporary
  directory, and GATK command.
- Required input and reference files are present before execution.
- The first run uses a small interval and completes with a reviewable log.
- Scaling plans account for scatter intervals, GenomicsDB memory, file
  descriptors, and durable output storage.
