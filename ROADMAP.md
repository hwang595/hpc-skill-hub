# Technical Roadmap

This roadmap turns HPC Skill Hub from a seed repository into a public,
reviewable ecosystem for reusable HPC operational knowledge.

## Current Baseline

The seed repository currently includes:

- 83 seed skills.
- 12 curated collections.
- 2 site adapters: 1 example adapter and 1 public-doc-backed draft adapter.
- JSON schemas for skills, collections, site adapters, registry health, and
  release manifests.
- An installable `hpc-skill` CLI for discovery, validation, scaffolding,
  collection browsing, site adapter browsing, and registry health.
- Generated catalog, compatibility, registry health, package data, static site,
  and deterministic release manifest artifacts.
- GitHub metadata for labels, issue templates, discussion templates,
  milestones, workflows, starter rulesets, and seed community issues.

The remaining external launch prerequisites are a public GitHub remote, an
authenticated GitHub CLI environment, and maintainer-owned repository settings.

## Phase 0: Seed Repository

Status: largely complete locally.

Technical gates:

- Define the skill package format and JSON schema.
- Add the first curated batch of practical HPC skills.
- Add safety, validation, release, and generated-registry checks.
- Add contribution, security, support, governance, review, and release docs.
- Keep examples portable, bounded, and directly adaptable on real clusters.
- Keep `make check` as the local release gate.

Exit evidence:

- `python3 tools/launch_readiness.py --owner <owner> --run-check` reports only
  external GitHub setup warnings.
- `registry/index.json`, `docs/SKILL_CATALOG.md`,
  `docs/REGISTRY_HEALTH.md`, `docs/COMPATIBILITY.md`, package registry data,
  and `registry/releases/v0.1.0.json` are current.

## Phase 1: Public GitHub Launch

Status: ready for an authenticated GitHub environment.

Technical gates:

- Create the public GitHub repository.
- Push `main` and confirm `Validate` and `Package` workflows pass.
- Apply repository metadata, labels, branch ruleset, and milestones from
  `.github/`.
- Enable GitHub Pages from Actions and publish the generated registry site.
- Enable Discussions and create the categories that match
  `.github/DISCUSSION_TEMPLATE/`.
- Open the seed community issues for domain reviewers, next-wave skills, public
  site adapters, and community calls.

Exit evidence:

- `origin` points at the public repository.
- GitHub Actions are green on `main`.
- Pages is reachable.
- Launch issue queue is visible.
- CODEOWNERS has real maintainer handles or documented placeholders.

## Phase 2: Usable Registry

Status: local foundation exists; public feedback is needed.

Technical gates:

- Improve search over skill manifests, tags, categories, schedulers, tools, and
  risk metadata.
- Keep generated compatibility tables for schedulers, containers, workflow
  engines, software stacks, and domain collections.
- Expand site adapters so HPC centers can publish public policy mappings
  without forking core skills.
- Add field evidence to selected seed skills through adoption reports.
- Promote selected skills from `seed` to `reviewed` only after domain review.

Exit evidence:

- At least three external adoption reports are filed.
- At least one public site adapter is reviewed or contributed by a real site or
  training environment.
- At least five skills complete maturity review and move to `reviewed`.

## Phase 3: CLI And Developer Experience

Status: basic CLI exists.

Technical gates:

- Extend `hpc-skill validate` with optional JSON reporting for downstream
  portals, assistants, and CI dashboards.
- Add template rendering for common scheduler scripts and config files without
  hiding resource impact.
- Add local dry-run checks for commands that may be expensive or risky on
  shared systems.
- Add contributor tooling for skill request intake, reviewer routing, and
  release-note generation.
- Keep registry artifacts stable enough for external consumers.

Exit evidence:

- Downstream tools can consume `registry/index.json` without scraping Markdown.
- Contributors can scaffold, validate, and preview a new skill with one local
  workflow.
- Release owners can cut a deterministic release from a clean checkout.

## Phase 4: Integrations

Status: skill coverage exists; deeper integrations are future work.

Priority integration tracks:

- Slurm: batch scripts, accounting, queue inspection, dependency chains,
  QOS/account limit evidence, license-aware jobs, preemption/requeue handling,
  and optional REST integration.
- Open OnDemand: Batch Connect app templates and user-facing interactive
  workflows.
- Apptainer: image execution, bind mounts, GPU pass-through, MPI launch, and
  reproducibility.
- Spack and EasyBuild: scientific software stack creation and module generation.
- HDF5 and NetCDF: parallel I/O build preflight, wrapper evidence, and tiny
  MPI-IO smoke tests.
- Globus and data lifecycle tools: reliable transfer, checksums, staging,
  archival, and publication handoff.
- Workflow engines: Nextflow, Snakemake, CWL, WDL, Dask, Parsl, and Ray.
- Observability: failure triage, QOS/account limit evidence, efficiency review,
  profiling, storage smoke evidence, preemption/requeue evidence, GPU binding
  diagnostics, MPI fabric diagnostics, MPI rank binding diagnostics, hybrid
  MPI/OpenMP layout checks, utilization reports, and training reset checks.

Exit evidence:

- Integration requests can cite a stable manifest contract.
- Each integration track has at least one maintainer or reviewer.
- High-risk integrations have explicit safety review before implementation.

## Phase 5: Open Ecosystem

Status: proposal and governance docs exist; public participation is pending.

Technical gates:

- Recruit maintainership areas for schedulers, storage, containers,
  workflow engines, AI/HPC, bioinformatics, simulation, facility operations,
  training, and registry tooling.
- Publish adapter contribution examples for training clusters, campus clusters,
  national facilities, and cloud HPC environments.
- Add signed releases and provenance for reviewed skills.
- Create a lightweight review board for high-risk or facility-operation skills.
- Encourage public site adapters instead of private forks.

Exit evidence:

- The project has recurring external contributors.
- Reviewed skills cite public evidence and reviewer ownership.
- Site adapters document public local policy without exposing private details.
- The registry is useful both as documentation and as machine-readable input for
  portals, assistants, and workflow tools.

## Skill Coverage Direction

The first wave emphasizes recurring support and onboarding workflows:

- Scheduler basics across Slurm, PBS/OpenPBS, LSF, HTCondor, and Grid Engine.
- Storage and data movement: scratch, quota, staging, checksums, rsync, Globus,
  object storage, archive preparation, and IOR/MDTest smoke evidence.
- Software stacks: modules, compiler/MPI matrices, Conda, virtualenv, Spack,
  EasyBuild, parallel HDF5/NetCDF preflight, containers, and reproducible run
  capture.
- Interactive and teaching workflows: Open OnDemand Batch Connect templates,
  Jupyter, TensorBoard, Streamlit, RStudio, VS Code tunnels, workshop reset
  checks, and language-specific batch jobs.
- AI/HPC: GPU sanity checks, PyTorch DDP, NCCL, DeepSpeed, Ray, Dask, JAX,
  Hugging Face Accelerate, TensorFlow, and monitoring.
- Domain workflows: bioinformatics, molecular dynamics, electronic structure,
  CFD, weather, workflow engines including Parsl, MPI, OpenMP, and performance
  evidence, including parallel HDF5/NetCDF preflight for data-heavy codes.
- Facility support: read-only usage, node, module tree, pending reason, and
  efficiency triage.

Future skills should be prioritized when they reduce repeated support tickets,
have public references, can be validated without private cluster access, and
fit a clear reviewer area.

## Design Principles

- Skills should be understandable before they are executable.
- Destructive, expensive, or shared-system actions must be explicit and
  documented.
- Cluster-specific assumptions belong in placeholders or site adapters.
- Examples should teach safe defaults first.
- Generated artifacts should be deterministic and validated in CI.
- The registry should help users move from "it ran once" to reproducible,
  supportable HPC workflows.
