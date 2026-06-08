# Technical Roadmap

## Phase 0: Seed Repository

- Define the skill package format.
- Add the first curated batch of HPC skills.
- Add validation scripts and CI.
- Add contribution, security, and governance documents.
- Keep all examples runnable or directly adaptable on real clusters.

## Phase 1: Usable Registry

- Add richer metadata search over skill manifests.
- Publish static documentation from the registry.
- Add compatibility tables for schedulers, containers, workflow engines, and
  scientific domains.
- Add site adapters so HPC centers can publish public local policy without
  forking core skills.
- Introduce skill quality levels: `seed`, `reviewed`, `field-tested`, and
  `maintained`.

## Phase 2: CLI And Developer Experience

- Add `hpc-skill list`, `hpc-skill show`, `hpc-skill validate`, and
  `hpc-skill scaffold`.
- Add template rendering for common HPC scripts and config files.
- Add local dry-run checks for commands that may be dangerous on shared systems.
- Add optional adapters for agentic tools that can read skill metadata.

## Phase 3: Integrations

- Slurm: batch scripts, accounting, queue inspection, and REST integration.
- Open OnDemand: portal app templates and user-facing interactive workflows.
- Apptainer: image execution, bind mounts, GPU pass-through, and reproducibility.
- Spack and EasyBuild: scientific software stack creation and module generation.
- Globus: reliable transfer recipes and checksum validation.
- Workflow engines: Nextflow, Snakemake, CWL, and WDL.
- Observability: job failure triage, performance profiling, and utilization
  reporting.

## Phase 4: Open Ecosystem

- Publish a website for discovery and documentation.
- Add maintainership areas by domain: scheduler, containers, bioinformatics,
  AI/HPC, molecular dynamics, CFD, climate, and facility operations.
- Add signed releases and provenance for reviewed skills.
- Add a lightweight review board for high-risk or site-admin skills.
- Encourage HPC centers to contribute site adapters instead of private forks.
- Publish adapter contribution guidelines and examples for training clusters,
  campus clusters, national facilities, and cloud HPC environments.

## Design Principles

- Skills should be understandable before they are executable.
- Destructive or expensive actions must be explicit and documented.
- Cluster-specific assumptions must be marked clearly.
- Examples should teach safe defaults first.
- The registry should help users move from "it ran once" to reproducible,
  supportable HPC workflows.
