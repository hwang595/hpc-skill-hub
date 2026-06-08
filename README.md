# HPC Skill Hub

HPC Skill Hub is an open registry of reusable, reviewable skills for running,
debugging, optimizing, and maintaining high performance computing workflows.

The project starts with practical skills for Slurm, containers, software
environments, workflow engines, data transfer, MPI, GPUs, and performance
triage. Each skill is a small package with a machine-readable manifest,
operator notes, examples, and validation metadata.

## Why This Exists

HPC knowledge is often spread across cluster-specific wiki pages, old shell
scripts, lab notebooks, and one-off support tickets. This repository turns that
knowledge into portable, testable building blocks that can be reviewed by the
community and adapted by HPC centers, research groups, and agentic developer
tools.

## Repository Layout

```text
.
├── skills/                 # Skill packages, one directory per skill
├── collections/            # Curated groups of skills for adoption paths
├── site-adapters/          # Optional local cluster policy adapters
├── schemas/                # JSON Schemas for skill metadata
├── tools/                  # Local validation and maintenance scripts
├── docs/                   # Architecture, specification, and governance docs
└── .github/workflows/      # CI checks for every pull request
```

## First Batch Of Skills

| Skill | Purpose |
| --- | --- |
| `slurm-submit-job` | Generate safe Slurm batch scripts for CPU, GPU, MPI, and array jobs. |
| `slurm-job-array-patterns` | Run parameter sweeps and independent tasks with bounded Slurm arrays. |
| `slurm-job-dependency-chain` | Chain multi-stage Slurm jobs with explicit dependencies. |
| `slurm-pending-reason-triage` | Explain why Slurm jobs are pending using read-only scheduler signals. |
| `slurm-monitor-job` | Inspect queued, running, completed, and failed Slurm jobs. |
| `slurm-resource-estimator` | Estimate memory, wall time, and CPU needs from accounting history. |
| `slurm-efficiency-report` | Summarize completed Slurm job efficiency from accounting data. |
| `checkpoint-restart-workflow` | Structure long jobs so they can resume after limits or preemption. |
| `job-failure-triage` | Diagnose common job failures such as OOM, time limits, and missing modules. |
| `interactive-session` | Start interactive compute sessions for shells, notebooks, and IDE tunnels. |
| `jupyter-on-slurm` | Launch Jupyter notebooks inside short Slurm compute allocations. |
| `training-cluster-reset-checklist` | Prepare and review HPC training environments before and after workshops. |
| `openmp-thread-affinity` | Align OpenMP threads with Slurm CPU allocations and affinity settings. |
| `quota-and-filesystem-triage` | Diagnose quota, inode, capacity, and permission failures. |
| `scratch-storage-management` | Inventory user-owned scratch, project, and workflow storage usage. |
| `module-environment-debug` | Debug module, compiler, MPI, and library path conflicts. |
| `module-tree-health-check` | Collect read-only evidence about visible HPC module tree health. |
| `compiler-mpi-matrix` | Check compiler, MPI wrapper, and module compatibility before building HPC codes. |
| `reproducible-run-capture` | Capture command, environment, provenance, and logs for reproducible HPC runs. |
| `python-virtualenv-on-hpc` | Create lightweight Python virtual environments with explicit HPC module assumptions. |
| `ray-on-slurm` | Launch resource-bounded Ray clusters inside Slurm allocations. |
| `dask-jobqueue-on-slurm` | Launch Dask workers through Slurm with dask-jobqueue and bounded dry-run defaults. |
| `mpi4py-on-slurm` | Run mpi4py Python programs on Slurm with matching MPI and Python environments. |
| `rscript-on-slurm` | Run R scripts on Slurm with explicit package-library and output controls. |
| `julia-on-slurm` | Run Julia scripts on Slurm with explicit depot, project, and thread settings. |
| `matlab-batch-on-slurm` | Run non-interactive MATLAB workloads on Slurm with explicit logs and license notes. |
| `conda-mamba-on-hpc` | Create Conda or Mamba environments while protecting shared HPC filesystems. |
| `container-build-for-hpc` | Plan and build Apptainer-compatible images for shared HPC systems. |
| `apptainer-run-container` | Run Apptainer/Singularity containers safely on shared HPC systems. |
| `spack-environment-create` | Create reproducible Spack environments for scientific software stacks. |
| `easybuild-install-software` | Install scientific software with EasyBuild recipes and module output. |
| `globus-transfer-dataset` | Stage and verify large research datasets with Globus transfers. |
| `rsync-data-transfer` | Transfer datasets with rsync dry-runs, resumable options, and validation hooks. |
| `checksum-manifest-create` | Create checksum manifests for transfer validation and reproducibility. |
| `dataset-staging-to-scratch` | Stage inputs to scratch, run work, and collect outputs from Slurm jobs. |
| `large-file-archive-prepare` | Prepare large HPC datasets for archival, publication, or handoff. |
| `cwl-on-slurm` | Run small CWL workflows inside Slurm allocations with cwltool. |
| `wdl-on-slurm` | Run small WDL workflows inside Slurm allocations with miniwdl. |
| `nextflow-on-slurm` | Configure Nextflow pipelines for Slurm-backed execution. |
| `snakemake-on-slurm` | Configure Snakemake workflows for Slurm profiles. |
| `nf-core-on-slurm` | Run nf-core Nextflow pipelines on Slurm with conservative HPC defaults. |
| `gatk-workflow-on-hpc` | Plan and run GATK variant-calling workflows on shared HPC systems. |
| `blast-on-slurm` | Run local BLAST+ searches on Slurm with bounded smoke-test defaults. |
| `gromacs-on-slurm` | Run GROMACS molecular dynamics jobs on Slurm with MPI, OpenMP, GPU, and checkpoint planning. |
| `lammps-on-slurm` | Run LAMMPS molecular dynamics jobs on Slurm with MPI, GPU, and restart planning. |
| `namd-on-slurm` | Run NAMD molecular dynamics jobs on Slurm with CPU/GPU and restart planning. |
| `quantum-espresso-on-slurm` | Run Quantum ESPRESSO PWscf jobs on Slurm with MPI sizing and restart planning. |
| `openfoam-on-slurm` | Run OpenFOAM CFD cases on Slurm with decomposition, MPI launch, and reconstruction planning. |
| `wrf-on-slurm` | Run WRF real-data jobs on Slurm with MPI sizing, real.exe staging, restart, and I/O planning. |
| `mpi-hello-and-benchmark` | Compile and run MPI sanity checks and simple communication benchmarks. |
| `gpu-sanity-check` | Verify GPU allocation, CUDA/ROCm visibility, and multi-GPU communication. |
| `pytorch-ddp-on-slurm` | Launch and verify PyTorch distributed data parallel jobs on Slurm. |
| `nccl-diagnostics` | Collect NCCL communication evidence for multi-GPU and multi-node jobs. |
| `gpu-memory-triage` | Distinguish GPU allocation, framework, and model memory failures. |
| `deepspeed-on-slurm` | Plan and smoke test DeepSpeed launches on Slurm GPU allocations. |
| `performance-profile-basic` | Collect first-pass CPU, memory, I/O, and GPU profiling evidence. |
| `cluster-usage-report-readonly` | Collect read-only Slurm usage evidence for facility support reports. |
| `node-health-readonly-triage` | Collect read-only Slurm node evidence for support triage. |

## Quick Start

Validate the registry:

```bash
python3 tools/hpc_skill.py validate
make check
```

Explore the registry:

```bash
python3 tools/hpc_skill.py list
python3 tools/hpc_skill.py search slurm
python3 tools/hpc_skill.py show slurm-submit-job --examples
python3 tools/hpc_skill.py collections
python3 tools/hpc_skill.py collection core-hpc
python3 tools/hpc_skill.py health
```

Install the CLI during development:

```bash
python3 -m pip install .
hpc-skill list
hpc-skill collection core-hpc
```

Scaffold new contributions:

```bash
python3 tools/hpc_skill.py scaffold skill my-new-skill --category education --tool bash
python3 tools/hpc_skill.py scaffold site-adapter my-campus-cluster --name "My Campus Cluster"
```

Validate one skill:

```bash
python3 tools/validate_skills.py --skill slurm-submit-job
```

Create a new skill:

```bash
python3 tools/hpc_skill.py scaffold skill my-new-skill --category education --tool bash
```

Then update the manifest, add `README.md`, add examples, and run the validator.

Rebuild the registry index after adding or editing skills:

```bash
python3 tools/hpc_skill.py validate --skill my-new-skill
python3 tools/build_index.py
python3 tools/build_health.py
python3 tools/hpc_skill.py validate
```

Run the standard local checks:

```bash
make check
```

Prepare GitHub publication commands without taking networked action:

```bash
python3 tools/github_publish_plan.py --owner <owner> --run-check
```

## Project Status

This repository is in the seed stage. The initial focus is on:

1. A stable skill package format.
2. A curated first batch of practical HPC skills.
3. CI validation for contributions.
4. A path toward a searchable public registry and ecosystem.

See [ROADMAP.md](ROADMAP.md) for the technical roadmap.

## Documentation

- [Skill catalog](docs/SKILL_CATALOG.md)
- [Collections](docs/COLLECTIONS.md)
- [Machine-readable registry index](registry/index.json)
- [Registry health](docs/REGISTRY_HEALTH.md)
- [Compatibility tables](docs/COMPATIBILITY.md)
- [CLI](docs/CLI.md)
- [Skill specification](docs/SKILL_SPEC.md)
- [Skill authoring guide](docs/SKILL_AUTHORING_GUIDE.md)
- [Skill lifecycle](docs/SKILL_LIFECYCLE.md)
- [Skill backlog](docs/SKILL_BACKLOG.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Site adapters](docs/SITE_ADAPTERS.md)
- [Integration guide](docs/INTEGRATION_GUIDE.md)
- [Adoption guide](docs/ADOPTION_GUIDE.md)
- [Adopter playbook](docs/ADOPTER_PLAYBOOK.md)
- [Adoption pilot worksheet](docs/ADOPTION_WORKSHEET.md)
- [Safety model](docs/SAFETY_MODEL.md)
- [Governance](docs/GOVERNANCE.md)
- [Contributor ladder](docs/CONTRIBUTOR_LADDER.md)
- [Review routing](docs/REVIEW_ROUTING.md)
- [Domain reviewers](docs/DOMAIN_REVIEWERS.md)
- [Triage runbook](docs/TRIAGE_RUNBOOK.md)
- [Maturity review](docs/MATURITY_REVIEW.md)
- [RFC process](docs/RFC_PROCESS.md)
- [Maintainer guide](docs/MAINTAINER_GUIDE.md)
- [Maintainer handoff](docs/MAINTAINER_HANDOFF.md)
- [Open ecosystem proposal](docs/ECOSYSTEM_PROPOSAL.md)
- [Open source proposal](docs/OPEN_SOURCE_PROPOSAL.md)
- [Community launch](docs/COMMUNITY_LAUNCH.md)
- [GitHub Discussions](docs/GITHUB_DISCUSSIONS.md)
- [GitHub milestones](docs/GITHUB_MILESTONES.md)
- [Release process](docs/RELEASE_PROCESS.md)
- [v0.1.0 release notes](docs/RELEASE_NOTES_v0.1.0.md)
- [Changelog](CHANGELOG.md)
- [GitHub publishing guide](docs/GITHUB_PUBLISHING.md)
- [GitHub repository setup](docs/GITHUB_REPOSITORY_SETUP.md)
- [Launch readiness](docs/LAUNCH_READINESS.md)
- [Support](SUPPORT.md)
- [Citation](docs/CITATION.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
