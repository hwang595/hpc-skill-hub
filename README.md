<p align="center">
  <img src="assets/brand/hpc-skill-hub-logo.png" alt="HPC Skill Hub logo" width="176">
</p>

<h1 align="center">HPC Skill Hub</h1>

<p align="center">
  <strong>Open, validated, reusable skills for HPC workflows.</strong>
</p>

<p align="center">
  <a href="https://github.com/hwang595/hpc-skill-hub/actions/workflows/validate.yml?query=branch%3Amain"><img alt="Validate workflow" src="https://github.com/hwang595/hpc-skill-hub/actions/workflows/validate.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/hwang595/hpc-skill-hub/actions/workflows/package.yml?query=branch%3Amain"><img alt="Package workflow" src="https://github.com/hwang595/hpc-skill-hub/actions/workflows/package.yml/badge.svg?branch=main"></a>
  <a href="https://github.com/hwang595/hpc-skill-hub/actions/workflows/pages.yml?query=branch%3Amain"><img alt="Pages workflow" src="https://github.com/hwang595/hpc-skill-hub/actions/workflows/pages.yml/badge.svg?branch=main"></a>
  <img alt="Version 0.4.0" src="https://img.shields.io/badge/version-0.4.0-0f766e">
  <img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-3776ab">
  <img alt="97 skills" src="https://img.shields.io/badge/skills-97-2563eb">
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-green"></a>
</p>

<p align="center">
  <a href="https://hwang595.github.io/hpc-skill-hub/">Registry site</a>
  ·
  <a href="docs/SKILL_CATALOG.md">Skill catalog</a>
  ·
  <a href="docs/SKILL_LIFECYCLE.md">Contribute a skill</a>
  ·
  <a href="docs/OPEN_SOURCE_PROPOSAL.md">Open ecosystem proposal</a>
</p>

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
├── agent-bench/            # Agent benchmark task and result contracts
├── schemas/                # JSON Schemas for skill metadata
├── tools/                  # Local validation and maintenance scripts
├── docs/                   # Architecture, specification, and governance docs
├── assets/                 # Project logo and public brand assets
└── .github/workflows/      # CI checks for every pull request
```

## First Batch Of Skills

| Skill | Purpose |
| --- | --- |
| `slurm-submit-job` | Generate safe Slurm batch scripts for CPU, GPU, MPI, and array jobs. |
| `pbs-submit-job` | Generate safe PBS or OpenPBS batch scripts for common HPC job shapes. |
| `lsf-submit-job` | Generate safe IBM LSF bsub scripts for common HPC job shapes. |
| `htcondor-submit-job` | Generate safe HTCondor submit descriptions for high-throughput jobs. |
| `grid-engine-submit-job` | Generate safe Grid Engine qsub scripts for common HPC job shapes. |
| `slurm-job-array-patterns` | Run parameter sweeps and independent tasks with bounded Slurm arrays. |
| `slurm-array-retry-plan` | Plan safe retries for failed Slurm array tasks. |
| `slurm-job-dependency-chain` | Chain multi-stage Slurm jobs with explicit dependencies. |
| `slurm-pending-reason-triage` | Explain why Slurm jobs are pending using read-only scheduler signals. |
| `slurm-maintenance-reservation-triage` | Collect read-only Slurm evidence for maintenance windows and reservations. |
| `slurm-qos-account-limit-triage` | Collect read-only evidence for Slurm account, QOS, and fairshare limits. |
| `slurm-monitor-job` | Inspect queued, running, completed, and failed Slurm jobs. |
| `slurm-output-log-triage` | Collect read-only evidence for missing or confusing Slurm output logs. |
| `slurm-resource-estimator` | Estimate memory, wall time, and CPU needs from accounting history. |
| `slurm-oom-memory-triage` | Collect Slurm memory evidence for out-of-memory jobs. |
| `slurm-time-limit-triage` | Collect read-only evidence for Slurm time-limit failures. |
| `slurm-node-failure-triage` | Collect read-only evidence for Slurm node-related job failures. |
| `slurm-efficiency-report` | Summarize completed Slurm job efficiency from accounting data. |
| `license-aware-slurm-job` | Plan Slurm jobs that request and verify tracked software license resources. |
| `checkpoint-restart-workflow` | Structure long jobs so they can resume after limits or preemption. |
| `slurm-preemption-requeue` | Handle Slurm preemption signals and guarded requeue workflows. |
| `job-failure-triage` | Diagnose common job failures such as OOM, time limits, and missing modules. |
| `interactive-session` | Start interactive compute sessions for shells, notebooks, and IDE tunnels. |
| `open-ondemand-batch-connect` | Prepare reviewable Open OnDemand Batch Connect app templates. |
| `jupyter-on-slurm` | Launch Jupyter notebooks inside short Slurm compute allocations. |
| `rstudio-on-slurm` | Launch policy-aware RStudio or Posit sessions from Slurm allocations. |
| `vscode-tunnel-on-slurm` | Run VS Code Remote Tunnels from short Slurm compute allocations. |
| `training-cluster-reset-checklist` | Prepare and review HPC training environments before and after workshops. |
| `openmp-thread-affinity` | Align OpenMP threads with Slurm CPU allocations and affinity settings. |
| `blas-openmp-thread-control` | Align BLAS, OpenMP, and language thread pools with HPC CPU allocations. |
| `file-descriptor-limit-triage` | Collect read-only evidence for too-many-open-files failures. |
| `quota-and-filesystem-triage` | Diagnose quota, inode, capacity, and permission failures. |
| `shared-project-permissions-triage` | Collect read-only evidence for shared project directory permission and ACL failures. |
| `scratch-storage-management` | Inventory user-owned scratch, project, and workflow storage usage. |
| `node-local-scratch-staging` | Stage data through node-local scratch with guarded cleanup. |
| `ior-mdtest-storage-smoke` | Collect small IOR and MDTest storage benchmark evidence on Slurm. |
| `module-environment-debug` | Debug module, compiler, MPI, and library path conflicts. |
| `module-tree-health-check` | Collect read-only evidence about visible HPC module tree health. |
| `compiler-mpi-matrix` | Check compiler, MPI wrapper, and module compatibility before building HPC codes. |
| `cmake-hpc-build-preflight` | Plan reproducible CMake configure, build, test, and install steps on HPC systems. |
| `parallel-hdf5-netcdf-preflight` | Check parallel HDF5 and NetCDF MPI-IO build and runtime assumptions. |
| `darshan-io-profile-analysis` | Analyze Darshan logs for HPC I/O behavior and bottleneck evidence. |
| `lustre-striping-layout-planning` | Inspect and plan Lustre stripe layouts for data-intensive HPC workloads. |
| `reproducible-run-capture` | Capture command, environment, provenance, and logs for reproducible HPC runs. |
| `python-virtualenv-on-hpc` | Create lightweight Python virtual environments with explicit HPC module assumptions. |
| `tensorboard-on-slurm` | Run policy-aware TensorBoard monitors from short Slurm allocations. |
| `streamlit-on-slurm` | Run policy-aware Streamlit apps from short Slurm compute allocations. |
| `ray-on-slurm` | Launch resource-bounded Ray clusters inside Slurm allocations. |
| `dask-jobqueue-on-slurm` | Launch Dask workers through Slurm with dask-jobqueue and bounded dry-run defaults. |
| `parsl-on-slurm` | Run small Parsl workflows on Slurm with explicit provider and executor limits. |
| `mpi4py-on-slurm` | Run mpi4py Python programs on Slurm with matching MPI and Python environments. |
| `mpi-rank-binding-diagnostics` | Collect MPI rank placement and CPU binding evidence from Slurm jobs. |
| `rscript-on-slurm` | Run R scripts on Slurm with explicit package-library and output controls. |
| `julia-on-slurm` | Run Julia scripts on Slurm with explicit depot, project, and thread settings. |
| `matlab-batch-on-slurm` | Run non-interactive MATLAB workloads on Slurm with explicit logs and license notes. |
| `conda-mamba-on-hpc` | Create Conda or Mamba environments while protecting shared HPC filesystems. |
| `container-build-for-hpc` | Plan and build Apptainer-compatible images for shared HPC systems. |
| `apptainer-run-container` | Run Apptainer/Singularity containers safely on shared HPC systems. |
| `apptainer-mpi-on-slurm` | Run MPI applications from Apptainer containers inside Slurm allocations. |
| `spack-environment-create` | Create reproducible Spack environments for scientific software stacks. |
| `easybuild-install-software` | Install scientific software with EasyBuild recipes and module output. |
| `globus-transfer-dataset` | Stage and verify large research datasets with Globus transfers. |
| `rsync-data-transfer` | Transfer datasets with rsync dry-runs, resumable options, and validation hooks. |
| `object-storage-transfer` | Plan object-storage transfers between HPC filesystems and cloud remotes. |
| `checksum-manifest-create` | Create checksum manifests for transfer validation and reproducibility. |
| `dataset-staging-to-scratch` | Stage inputs to scratch, run work, and collect outputs from Slurm jobs. |
| `node-local-scratch-staging` | Stage data through node-local scratch with guarded cleanup. |
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
| `cp2k-on-slurm` | Run CP2K calculations on Slurm with MPI/OpenMP layout and restart planning. |
| `openfoam-on-slurm` | Run OpenFOAM CFD cases on Slurm with decomposition, MPI launch, and reconstruction planning. |
| `wrf-on-slurm` | Run WRF real-data jobs on Slurm with MPI sizing, real.exe staging, restart, and I/O planning. |
| `mpi-hello-and-benchmark` | Compile and run MPI sanity checks and simple communication benchmarks. |
| `mpi-fabric-diagnostics` | Collect MPI transport and fabric evidence for multi-node Slurm jobs. |
| `hybrid-mpi-openmp-slurm` | Plan and verify hybrid MPI/OpenMP task and thread layouts on Slurm. |
| `gpu-sanity-check` | Verify GPU allocation, CUDA/ROCm visibility, and multi-GPU communication. |
| `slurm-gpu-binding-diagnostics` | Collect per-task GPU binding and visibility evidence from Slurm jobs. |
| `jax-distributed-on-slurm` | Plan and smoke test distributed JAX jobs on Slurm GPU allocations. |
| `huggingface-accelerate-on-slurm` | Plan and smoke test Hugging Face Accelerate launches on Slurm. |
| `tensorflow-multiworker-on-slurm` | Plan and smoke test TensorFlow MultiWorkerMirroredStrategy jobs on Slurm. |
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
python3 tools/hpc_skill.py list --collection simulation-workflows --tool bash --json
python3 tools/hpc_skill.py search slurm
python3 tools/hpc_skill.py search simulation --scheduler slurm --risk medium
python3 tools/hpc_skill.py show slurm-submit-job --examples
python3 tools/hpc_skill.py collections
python3 tools/hpc_skill.py collection core-hpc
python3 tools/hpc_skill.py health
python3 tools/hpc_skill.py validate --skill slurm-submit-job --json
python3 tools/review_candidates.py --limit 12
```

Install the CLI during development:

```bash
python3 -m pip install .
hpc-skill list
hpc-skill collection core-hpc
hpc-skill resolve slurm-submit-job --adapter example-campus-cluster --json
```

Install the optional read-only MCP server on Python 3.10 or later:

```bash
python3 -m pip install '.[mcp]'
hpc-skill-mcp --root /path/to/hpc-skill-hub
```

Scaffold new contributions:

```bash
python3 tools/hpc_skill.py new skill my-new-skill --category education --tool bash
python3 tools/hpc_skill.py new site-adapter my-campus-cluster --name "My Campus Cluster"
```

Validate one skill:

```bash
python3 tools/hpc_skill.py check slurm-submit-job
python3 tools/hpc_skill.py check slurm-submit-job --json
```

Create a new skill:

```bash
python3 tools/hpc_skill.py new skill my-new-skill --category education --tool bash
```

Then update the manifest, add `README.md`, add examples, and run the validator.

Rebuild the registry index after adding or editing skills:

```bash
python3 tools/hpc_skill.py validate --skill my-new-skill
python3 tools/build_index.py
python3 tools/build_health.py
python3 tools/build_skill_context.py
python3 tools/build_package_data.py
python3 tools/hpc_skill.py validate
```

Run the standard local checks:

```bash
make check
```

Prepare GitHub publication commands without taking networked action:

```bash
python3 tools/launch_readiness.py --owner <owner> --run-check
python3 tools/github_publish_plan.py --owner <owner> --run-check
python3 tools/launch_evidence.py --owner <owner> --run-check
python3 tools/proposal_evidence.py --owner <owner> --run-check
python3 tools/review_candidates.py --limit 12
python3 tools/github_homepage.py --repo <owner>/hpc-skill-hub
python3 tools/github_post_launch_check.py --repo <owner>/hpc-skill-hub --dry-run
```

## Quality Gates

The repository is set up as a versioned registry, not just a documentation dump:

| Gate | What it proves |
| --- | --- |
| `Validate` workflow | Skill manifests, generated registry files, safety audit, CLI smoke tests, and unit tests pass on every push and pull request. |
| `registry/skill-quality.json` | Deterministic documentation and evidence coverage baseline that prioritizes review work without claiming maturity or correctness. |
| `hpc-skill security` | Community skill packages receive deterministic prompt-injection, command, persistence, credential, package, and risk-declaration checks before adoption. |
| `registry/skill-context.json` | Bounded registry-declared README and artifact content is bound to the index with file, skill, bundle, and security-report SHA-256 provenance. |
| `hpc-skill-mcp` | Optional stdio-only MCP surface exposes six closed-domain registry queries and verified `hpc-skill://skills/{skill_id}` resources with no execution or write tools. |
| `Package` workflow | Source and wheel distributions build cleanly, metadata passes `twine check`, and the installed wheel can read registry data outside the checkout. |
| `Publish Pages` workflow | The searchable static registry site builds and deploys from the tracked registry index. |
| `registry/releases/v0.4.0.json` | Versioned release manifest with file checksums and registry counts for reproducible snapshots. |
| `docs/REVIEW_PACKET_v0.2.0.md` | Reviewed-skill pilot queue with reviewer routing, suggested labels, and promotion gates. |
| `pyproject.toml` | Package version, Python compatibility, CLI entry point, and project metadata are tracked in source control. |

## Project Status

`v0.4.0` is the current stable registry snapshot. The registry remains
conservative about maturity: skills stay `seed` until domain review and public
evidence support promotion. This release adds bounded evidence campaigns,
machine-checkable maturity review, public review routing, and gated dashboards
without claiming measured agent lift or completed maturity promotion. The
current v0.5 focus is on trusted agent distribution:

1. Read-only MCP registry discovery, merged in P0.
2. Digest-verified packaged skill context, implemented in P1.
3. Generated Codex and Claude Code onboarding plus compatibility diagnostics.
4. Versioned community-skill trust policy and provenance receipts.
5. An MCP-enabled benchmark condition behind the existing paid-run and review gates.

See [ROADMAP.md](ROADMAP.md) for the technical roadmap.

## Documentation

- [Skill catalog](docs/SKILL_CATALOG.md)
- [Collections](docs/COLLECTIONS.md)
- [Machine-readable registry index](registry/index.json)
- [Verified skill context bundle](registry/skill-context.json)
- [Registry health](docs/REGISTRY_HEALTH.md)
- [Skill quality baseline](docs/SKILL_QUALITY.md)
- [v0.4 skill review packet](docs/REVIEW_PACKET_v0.4.0.md)
- [Skill review dashboard](docs/SKILL_REVIEW_DASHBOARD.html)
- [Compatibility tables](docs/COMPATIBILITY.md)
- [CLI](docs/CLI.md)
- [Agent integration](docs/AGENT_INTEGRATION.md)
- [Read-only MCP server](docs/MCP_SERVER.md)
- [v0.5 development plan](docs/V0_5_PLAN.md)
- [Agent benchmarks](docs/AGENT_BENCHMARKS.md)
- [Agent benchmark calibration plan](docs/AGENT_BENCHMARK_PLAN.md)
- [Agent benchmark v0.3 smoke plan](docs/AGENT_BENCHMARK_SMOKE_PLAN.md)
- [Agent benchmark v0.4 evidence plan](docs/AGENT_BENCHMARK_V0_4_PLAN.md)
- [Agent benchmark campaign operations](docs/AGENT_BENCHMARK_CAMPAIGN.md)
- [Blinded review and scoring](docs/BLINDED_REVIEW.md)
- [Agent benchmark report](docs/AGENT_BENCHMARK_REPORT.md)
- [Agent benchmark evidence dashboard](docs/AGENT_BENCHMARK_DASHBOARD.html)
- [v0.3 completion matrix](docs/V0_3_COMPLETION.md)
- [v0.4 completion matrix](docs/V0_4_COMPLETION.md)
- [Benchmarks](docs/BENCHMARKS.md)
- [Skill specification](docs/SKILL_SPEC.md)
- [Skill authoring guide](docs/SKILL_AUTHORING_GUIDE.md)
- [Skill lifecycle](docs/SKILL_LIFECYCLE.md)
- [Skill backlog](docs/SKILL_BACKLOG.md)
- [Roadmap](ROADMAP.md)
- [Release provenance](docs/RELEASE_PROVENANCE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Site adapters](docs/SITE_ADAPTERS.md)
- [Integration guide](docs/INTEGRATION_GUIDE.md)
- [Adoption guide](docs/ADOPTION_GUIDE.md)
- [Adopter playbook](docs/ADOPTER_PLAYBOOK.md)
- [Adoption pilot worksheet](docs/ADOPTION_WORKSHEET.md)
- [Safety model](docs/SAFETY_MODEL.md)
- [Community skill security](docs/SKILL_SECURITY.md)
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
- [Public launch packet](docs/PUBLIC_LAUNCH_PACKET.md)
- [GitHub owner checklist](docs/GITHUB_OWNER_CHECKLIST.md)
- [Community launch](docs/COMMUNITY_LAUNCH.md)
- [GitHub Discussions](docs/GITHUB_DISCUSSIONS.md)
- [GitHub milestones](docs/GITHUB_MILESTONES.md)
- [Release process](docs/RELEASE_PROCESS.md)
- [v0.1.0 release notes](docs/RELEASE_NOTES_v0.1.0.md)
- [v0.2.0 release notes](docs/RELEASE_NOTES_v0.2.0.md)
- [v0.3.0 release notes](docs/RELEASE_NOTES_v0.3.0.md)
- [v0.4.0 release notes](docs/RELEASE_NOTES_v0.4.0.md)
- [v0.2.0 review packet](docs/REVIEW_PACKET_v0.2.0.md)
- [Changelog](CHANGELOG.md)
- [GitHub publishing guide](docs/GITHUB_PUBLISHING.md)
- [GitHub repository setup](docs/GITHUB_REPOSITORY_SETUP.md)
- [Post-launch verification](docs/POST_LAUNCH_VERIFICATION.md)
- [Launch readiness](docs/LAUNCH_READINESS.md)
- [Support](SUPPORT.md)
- [Citation](docs/CITATION.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
