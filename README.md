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
| `slurm-monitor-job` | Inspect queued, running, completed, and failed Slurm jobs. |
| `slurm-resource-estimator` | Estimate memory, wall time, and CPU needs from accounting history. |
| `job-failure-triage` | Diagnose common job failures such as OOM, time limits, and missing modules. |
| `interactive-session` | Start interactive compute sessions for shells, notebooks, and IDE tunnels. |
| `module-environment-debug` | Debug module, compiler, MPI, and library path conflicts. |
| `apptainer-run-container` | Run Apptainer/Singularity containers safely on shared HPC systems. |
| `spack-environment-create` | Create reproducible Spack environments for scientific software stacks. |
| `easybuild-install-software` | Install scientific software with EasyBuild recipes and module output. |
| `globus-transfer-dataset` | Stage and verify large research datasets with Globus transfers. |
| `nextflow-on-slurm` | Configure Nextflow pipelines for Slurm-backed execution. |
| `snakemake-on-slurm` | Configure Snakemake workflows for Slurm profiles. |
| `mpi-hello-and-benchmark` | Compile and run MPI sanity checks and simple communication benchmarks. |
| `gpu-sanity-check` | Verify GPU allocation, CUDA/ROCm visibility, and multi-GPU communication. |
| `performance-profile-basic` | Collect first-pass CPU, memory, I/O, and GPU profiling evidence. |

## Quick Start

Validate the registry:

```bash
python3 tools/validate_skills.py
python3 tools/build_index.py --check
```

Explore the registry:

```bash
python3 tools/hpc_skill.py list
python3 tools/hpc_skill.py search slurm
python3 tools/hpc_skill.py show slurm-submit-job --examples
```

Validate one skill:

```bash
python3 tools/validate_skills.py --skill slurm-submit-job
```

Create a new skill:

```bash
mkdir -p skills/my-new-skill/examples
cp docs/examples/skill.json skills/my-new-skill/skill.json
```

Then update the manifest, add `README.md`, add examples, and run the validator.

Rebuild the registry index after adding or editing skills:

```bash
python3 tools/build_index.py
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
- [Machine-readable registry index](registry/index.json)
- [CLI](docs/CLI.md)
- [Skill specification](docs/SKILL_SPEC.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Site adapters](docs/SITE_ADAPTERS.md)
- [Adoption guide](docs/ADOPTION_GUIDE.md)
- [Maintainer guide](docs/MAINTAINER_GUIDE.md)
- [Open ecosystem proposal](docs/ECOSYSTEM_PROPOSAL.md)
- [GitHub publishing guide](docs/GITHUB_PUBLISHING.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
