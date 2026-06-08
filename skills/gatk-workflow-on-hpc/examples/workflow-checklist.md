# GATK Workflow Checklist

- Confirm BAM/CRAM inputs are analysis-ready and use the same reference build.
- Confirm `.bai` or `.crai`, `.fai`, and sequence dictionary files are present.
- Start with a small interval before whole-genome or cohort execution.
- Put `java.io.tmpdir` on job scratch or user-owned scratch, not shared `/tmp`.
- Keep Java heap below the Slurm memory request with room for native memory.
- Record known-sites resources, reference version, interval list, and GATK version.
- For cohort work, plan scatter intervals and GenomicsDB workspace storage before scaling.
