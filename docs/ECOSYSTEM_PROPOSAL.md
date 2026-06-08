# Open Ecosystem Proposal

HPC Skill Hub can become a shared ecosystem for operational HPC knowledge.

## Ecosystem Roles

- HPC centers contribute site adapters and reviewed operational patterns.
- Research groups contribute domain workflows.
- Research software engineers contribute reproducible build and workflow
  practices.
- Tool vendors and open-source projects contribute integration skills.
- Instructors contribute teaching-oriented skills for onboarding.

## What Makes This Different

The project is not only a documentation site. It combines:

- Machine-readable skill manifests.
- Human-readable operating notes.
- Reviewable examples.
- Risk classification.
- CI validation.
- A path to CLI and agent integrations.

## Proposed Community Collections

- `core-hpc`: Slurm, modules, shell, storage, interactive sessions.
- `containers`: Apptainer, OCI image conversion, GPU containers.
- `software-stacks`: Spack, EasyBuild, Lmod, compiler and MPI matrices.
- `workflow-engines`: Nextflow, Snakemake, CWL, WDL.
- `ai-hpc`: PyTorch DDP, DeepSpeed, NCCL, GPU performance triage.
- `biohpc`: nf-core, GATK, BLAST, AlphaFold, single-cell workflows.
- `simulation`: LAMMPS, GROMACS, NAMD, OpenFOAM, WRF.
- `facility-ops`: read-only reporting, health checks, usage reports, portals.

## Governance Direction

Start simple with repository maintainers and CODEOWNERS. As adoption grows, add
domain maintainers and a review path for high-risk skills. Avoid centralizing
site-specific policy in the core registry; encourage adapters and clear
metadata instead.
