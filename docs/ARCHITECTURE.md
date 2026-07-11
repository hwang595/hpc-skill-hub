# Architecture

HPC Skill Hub is organized as a registry-first repository. The core artifact is
a skill package under `skills/<skill-id>/`.

## Skill Package

A skill package contains:

- `skill.json`: machine-readable metadata.
- `README.md`: human-readable operating notes.
- `examples/`: scripts, configs, command files, or templates.
- Optional tests, assets, and fixtures as the skill matures.

The manifest is intentionally simple JSON so it can be validated without
language-specific dependencies. A future CLI can render templates, index skills,
or expose the registry as an API.

## Site Adapter Package

A site adapter under `site-adapters/<adapter-id>/` contains:

- `site.json`: public local policy and infrastructure metadata.
- `README.md`: human-facing notes for adapting skills to the site.

Site adapters are optional. They let HPC centers document partitions, modules,
storage conventions, and policy notes without editing or forking generic skills.

## Registry Index

`tools/build_index.py` generates:

- `registry/index.json`: machine-readable registry metadata for websites, CLIs,
  search services, and agent integrations.
- `docs/SKILL_CATALOG.md`: human-readable catalog grouped by category.

Both generated artifacts are checked in CI so documentation and machine-readable
metadata stay aligned with the skill manifests.

Registry index contract `0.2.0` embeds each adapter's complete public policy so
the installed CLI can resolve a portable skill and site adapter without a
checkout. `hpc-skill resolve` emits the separate, read-only
`site-adapter-resolution` contract and never renders or executes commands.

`tools/build_health.py` generates `registry/health.json` and
`docs/REGISTRY_HEALTH.md` for maintainer-facing coverage, risk, maturity, and
collection health.

`tools/build_compatibility.py` generates `docs/COMPATIBILITY.md` for scheduler,
collection, workflow engine, container, domain, and tool compatibility views
derived from `registry/index.json`.

`tools/build_release_manifest.py` generates `registry/releases/<version>.json`
with deterministic file sizes and SHA-256 checksums for release provenance.

`tools/build_package_data.py` copies `registry/index.json` and
`registry/health.json` into `src/hpc_skill_hub/data/registry/` so installed CLI
users can run read-only discovery commands without a repository checkout.

`tools/validate_registry_artifacts.py` checks the generated registry index,
health report, packaged registry snapshot, immutable historical release
manifests, and public JSON Schema pointers used by downstream integrations.
Preparing a new release separately runs `tools/build_release_manifest.py` to
compare that version's snapshot with the release candidate worktree.

The tag-triggered package workflow uses GitHub artifact attestations to bind
the versioned release manifest and tested Python distributions to their build
workflow without granting signing permissions to pull request build jobs.

`hpc_skill_hub.security` and `tools/scan_skill_security.py` scan untrusted skill
packages without executing them. The scanner emits text, JSON, or SARIF and is
available through the installed `hpc-skill security` command.

`tools/agent_benchmark_harness.py` expands versioned experiment plans into
condition-isolated run packets. The v0.3 smoke plan uses six runs to verify
Codex/Claude executable and exact-model preflight, context isolation, resumable
status, and the paid-execution boundary before the 54-run calibration.

## Collections

Collections under `collections/*.json` group skills into adoption paths such as
core HPC, software stacks, workflow engines, data movement, and GPU/MPI
performance. Collections reference skill ids instead of duplicating skill
metadata.

## CLI

`tools/hpc_skill.py` reads `registry/index.json` and provides lightweight
discovery commands for users and maintainers. It deliberately uses only the
Python standard library so it can run on login nodes, laptops, CI systems, and
minimal container images. The package entry point prefers a full repository
checkout when one is available, then falls back to the packaged registry
snapshot for read-only discovery commands.

## Static Site

`tools/build_site.py` reads `registry/index.json` and emits a single-file HTML
registry explorer with search, collection and site-adapter tables, adoption
paths, and contribution lanes for new community requests. The `Publish Pages`
workflow builds and deploys that output through GitHub Pages when the
repository is hosted on GitHub.

## Validation Flow

```text
pull request
  -> tools/scan_skill_security.py
  -> tools/validate_skills.py
  -> manifest structure checks
  -> referenced artifact checks
  -> README and example presence checks
```

The seed validator is not a full JSON Schema implementation. It performs the
checks that matter most for repository health and contributor feedback. The
schema in `schemas/skill.schema.json` documents the public contract and can be
used by editors or downstream tools.

## Maturity Model

- `seed`: useful starting point, not yet reviewed on multiple systems.
- `reviewed`: reviewed by maintainers for safety and portability.
- `field-tested`: used successfully on at least one real HPC site.
- `maintained`: actively owned, tested, and updated.

## Runtime Boundary

The registry does not directly execute high-impact commands. Skills provide
templates, checklists, diagnostics, and dry-run paths. A future CLI may execute
selected workflows, but only with explicit user intent and risk labeling.
