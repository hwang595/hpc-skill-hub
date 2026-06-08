# Changelog

All notable changes to HPC Skill Hub are tracked here.

This project uses semantic versioning for repository releases. Individual
skills keep their own `version` field in `skills/*/skill.json`.

## Unreleased

- Prepare the seed registry for public GitHub launch, including repository
  metadata, labels, rulesets, issue templates, pull request templates, Pages
  publishing, and governance docs.

## v0.1.0 - Planned

Initial public seed release.

### Added

- 40 seed HPC skills covering Slurm, job arrays, monitoring, resource
  estimation, failure triage, checkpoint/restart, interactive sessions,
  notebooks, OpenMP placement, storage triage, software environments,
  containers, Spack, EasyBuild, data movement, workflow engines, MPI/GPU
  diagnostics, AI/HPC launches, bioinformatics workflows, molecular dynamics,
  CFD, and weather workloads.
- 7 curated collections: `core-hpc`, `software-stacks`, `workflow-engines`,
  `data-movement`, `gpu-mpi-performance`, `bioinformatics-workflows`, and
  `simulation-workflows`.
- 1 example public site adapter: `example-campus-cluster`.
- Machine-readable registry index and health reports.
- Installable `hpc-skill` CLI for discovery, validation, scaffolding,
  collections, site adapters, and registry health.
- Static site generation for GitHub Pages.
- JSON schemas for skills, collections, and site adapters.
- GitHub Actions validation, Pages publishing, Dependabot, issue templates,
  pull request templates, starter labels, repository metadata, and starter
  `main` branch ruleset configuration.
- Governance, safety, release, maintainer handoff, authoring, publishing, and
  community launch documentation.

### Safety Notes

- User-facing examples default to dry-run, read-only, plan-only, or explicitly
  bounded behavior where practical.
- Medium-risk skills document resource impact, output volume, or side effects.
- Site adapters must contain only public, non-sensitive local policy.
- High-risk or facility-operations skills require explicit maintainer review
  before promotion beyond seed maturity.
