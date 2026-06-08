# Open Source Proposal

## Proposal

Adopt HPC Skill Hub as a community registry for reusable, reviewable HPC
operational knowledge.

## Problem

HPC users repeatedly solve the same tasks: submitting Slurm jobs, debugging
modules, running containers, transferring data, launching workflow engines,
checking GPUs, and triaging failed jobs. The knowledge is usually scattered
across private wikis, tickets, old scripts, and institutional memory.

## Solution

HPC Skill Hub turns those recurring tasks into portable skill packages with:

- Machine-readable metadata.
- Human-readable README files.
- Safe examples.
- Risk labels.
- Validation in CI.
- A generated registry index.
- Site adapters for public local policy.
- Curated collections for adoption paths.
- A lightweight CLI for discovery and scaffolding.

## Initial Scope

The seed registry includes 65 skills covering Slurm, PBS/OpenPBS, LSF, HTCondor, Grid Engine, modules, Apptainer, containerized MPI, Spack,
EasyBuild, Globus, CWL, WDL, Nextflow, Snakemake, MPI, GPU sanity checks, and basic
profiling, plus storage, quota, arrays, dependency chains, pending reason
triage, job efficiency review, checkpoint/restart workflows, OpenMP placement,
Jupyter notebooks, VS Code tunnels, Python/Conda environments, Ray, Dask Jobqueue, mpi4py,
Rscript, Julia, and MATLAB batch jobs, compiler/MPI compatibility,
reproducible run capture, container builds, checksum manifests, rsync transfer,
scratch staging, archive preparation, PyTorch DDP smoke testing, NCCL
diagnostics, GPU memory triage, and DeepSpeed launch checks. It also includes
nf-core, GATK, local BLAST+, LAMMPS, GROMACS, NAMD, Quantum ESPRESSO, CP2K,
OpenFOAM, and WRF on Slurm, read-only facility usage reporting, node triage,
module tree health checks, workshop preflight and reset guidance, twelve curated
collections, and one example site adapter.

## Community Model

- HPC centers contribute site adapters and reviewed operational patterns.
- Research groups contribute domain skills and smoke tests.
- Tool maintainers contribute integration skills.
- Instructors contribute teaching skills for onboarding.
- Maintainers review high-risk skills before promotion.

## Adoption Milestones

1. Publish the repository and enable validation workflows.
2. Publish GitHub Pages from the generated registry site.
3. Invite three to five HPC centers or research software teams to review the
   seed skills.
4. Add the first real site adapter from public documentation.
5. Promote reviewed skills from `seed` to `reviewed`.
6. Cut a `v0.1.0` release once schema and contribution workflows are stable.

## Success Metrics

- Number of reviewed skills.
- Number of external contributors.
- Number of public site adapters.
- Number of domain-specific skill collections.
- Reduction in repeated support questions for covered tasks.

## Stewardship

Start with lightweight maintainer ownership. Add domain maintainers when the
registry gains contributors in schedulers, containers, workflows, AI/HPC,
bioinformatics, simulation, and facility operations.
