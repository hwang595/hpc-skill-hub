# nf-core On Slurm

Use this skill when a bioinformatics team wants to run an nf-core pipeline on a
Slurm-backed HPC system with reviewed work, cache, container, and reporting
paths.

## Example

Create a launch plan:

```bash
bash examples/run-nfcore.sh nf-core/rnaseq examples/samplesheet.csv results/rnaseq scratch/nf-work
```

After reviewing the plan and adapting the sample sheet and config, run a small
test profile explicitly:

```bash
RUN_NFCORE=1 NFCORE_REVISION=<release> bash examples/run-nfcore.sh nf-core/rnaseq examples/samplesheet.csv results/rnaseq scratch/nf-work
```

## Pattern

- Pin the nf-core pipeline revision before production runs.
- Use `-profile test,singularity` or a site-specific profile for smoke tests.
- Store the Nextflow work directory on scratch or project storage designed for
  many task directories.
- Put container cache directories on durable project storage, not a shared home
  directory.
- Keep Nextflow report, trace, timeline, DAG, and logs with the run record.
- Use `-resume` only after confirming the same pipeline revision, inputs, and
  configuration should be reused.

## Safety Notes

This skill is `medium` risk because nf-core pipelines can launch many Slurm
jobs and can read or write large biological datasets. The launch wrapper
defaults to plan-only mode and runs only when `RUN_NFCORE=1` is set. Start with
the pipeline's test profile and site-approved container settings.

## Success Criteria

- The launch plan records pipeline name, revision, profiles, config, sample
  sheet, output directory, work directory, and container cache.
- The test profile completes before production inputs are used.
- Final outputs are written to durable storage, while work directories stay on
  scratch or project storage.
- Nextflow reports are preserved for provenance and support.
