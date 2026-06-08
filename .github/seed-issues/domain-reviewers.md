The seed registry needs domain reviewers before skills can move from `seed` to
`reviewed` or `field-tested`. The public reviewer area map lives in
`docs/DOMAIN_REVIEWERS.md`.

Reviewer areas we would like to cover:

- Slurm scheduling and accounting.
- Containers and Apptainer/Singularity usage.
- Spack, EasyBuild, modules, compilers, and MPI stacks.
- Data movement, Globus, rsync, checksums, and archive preparation.
- Workflow engines: Nextflow, Snakemake, CWL, and WDL.
- AI/HPC: PyTorch DDP, NCCL, DeepSpeed, and accelerator diagnostics.
- Bioinformatics workflows.
- Simulation workflows: molecular dynamics, CFD, climate, and weather.
- Read-only facility operations and support handoff workflows.

Reviewers can help by checking portability, risk labels, examples, references,
and whether a skill needs a site adapter note instead of a core registry change.
Use the maturity review template when a skill is ready to move from `seed` to
`reviewed`, `field-tested`, or `maintained`.
