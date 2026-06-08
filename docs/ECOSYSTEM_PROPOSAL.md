# Open Ecosystem Proposal

HPC Skill Hub can become a shared ecosystem for operational HPC knowledge.

## Ecosystem Roles

- HPC centers contribute site adapters and reviewed operational patterns.
- Research groups contribute domain workflows.
- Research software engineers contribute reproducible build and workflow
  practices.
- Tool vendors and open-source projects contribute integration skills.
- Instructors contribute teaching-oriented skills for onboarding.
- HPC centers contribute site adapters that map portable skills to local policy.

## What Makes This Different

The project is not only a documentation site. It combines:

- Machine-readable skill manifests.
- Human-readable operating notes.
- Reviewable examples.
- Risk classification.
- CI validation.
- Site adapters for local cluster policy without core registry forks.
- Curated collections that help users enter the registry by workflow or role.
- A path to CLI and agent integrations.

## Proposed Community Collections

- `core-hpc`: Slurm, modules, shell, storage, interactive sessions.
- `containers`: Apptainer, OCI image conversion, GPU containers.
- `software-stacks`: Spack, EasyBuild, Lmod, compiler and MPI matrices.
- `workflow-engines`: Nextflow, Snakemake, CWL, WDL.
- `ai-hpc`: PyTorch DDP, NCCL diagnostics, GPU memory triage, DeepSpeed launch
  checks, GPU performance triage.
- `bioinformatics-workflows`: nf-core, GATK, BLAST, AlphaFold, single-cell
  workflows, and genomics data staging.
- `simulation-workflows`: LAMMPS, GROMACS, NAMD, OpenFOAM, WRF.
- `facility-ops`: read-only usage reporting, health checks, support handoffs,
  and public operational patterns.

## Governance Direction

Start simple with repository maintainers and CODEOWNERS. As adoption grows, add
domain maintainers and a review path for high-risk skills. Avoid centralizing
site-specific policy in the core registry; encourage adapters and clear
metadata instead.

## Adoption Path

The easiest first contribution from an HPC center is a public site adapter. The
easiest first contribution from a research group is a domain skill with a small
smoke test. The easiest first contribution from a tool maintainer is an
integration skill that shows safe scheduler, container, and workflow usage.
