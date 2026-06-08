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

The seed registry includes 79 skills covering Slurm, PBS/OpenPBS, LSF, HTCondor, Grid Engine, modules, Apptainer, containerized MPI, Spack,
EasyBuild, Globus, CWL, WDL, Nextflow, Snakemake, MPI, GPU sanity checks, and basic
profiling, GPU binding diagnostics, MPI rank binding diagnostics, hybrid MPI/OpenMP layout checks, license-aware Slurm jobs, plus storage, quota, arrays, dependency chains, pending reason
triage, job efficiency review, checkpoint/restart workflows, OpenMP placement,
Open OnDemand Batch Connect templates, Jupyter notebooks, TensorBoard monitors, Streamlit apps, RStudio sessions, VS Code tunnels, Python/Conda environments, Ray, Dask Jobqueue, Parsl, JAX, Hugging Face Accelerate, TensorFlow, mpi4py,
Rscript, Julia, and MATLAB batch jobs, compiler/MPI compatibility,
reproducible run capture, container builds, checksum manifests, rsync transfer,
object storage transfer, scratch staging, archive preparation, IOR/MDTest storage smoke benchmarks,
PyTorch DDP smoke testing, NCCL diagnostics, GPU memory triage, and DeepSpeed launch checks. It also includes
nf-core, GATK, local BLAST+, LAMMPS, GROMACS, NAMD, Quantum ESPRESSO, CP2K,
OpenFOAM, and WRF on Slurm, read-only facility usage reporting, node triage,
module tree health checks, workshop preflight and reset guidance, 12 curated collections,
and 2 site adapters: one example adapter and one public-doc-backed NERSC
Perlmutter draft adapter.

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
4. Review and refine the first public-doc-backed site adapter.
5. Promote reviewed skills from `seed` to `reviewed`.
6. Cut a `v0.1.0` release once schema and contribution workflows are stable.

## Proposal Evidence

Generate a current evidence report before sharing this proposal with a
repository owner, sponsoring organization, OSPO, or community steering group:

```bash
python3 tools/proposal_evidence.py --owner <owner> --run-check
```

The report summarizes registry coverage, community launch assets, release
manifest state, readiness checks, and the first reviewed-skill pilot queue
without taking networked GitHub actions.

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
