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

`tools/build_health.py` generates `registry/health.json` and
`docs/REGISTRY_HEALTH.md` for maintainer-facing coverage, risk, maturity, and
collection health.

## Collections

Collections under `collections/*.json` group skills into adoption paths such as
core HPC, software stacks, workflow engines, data movement, and GPU/MPI
performance. Collections reference skill ids instead of duplicating skill
metadata.

## CLI

`tools/hpc_skill.py` reads `registry/index.json` and provides lightweight
discovery commands for users and maintainers. It deliberately uses only the
Python standard library so it can run on login nodes, laptops, CI systems, and
minimal container images.

## Static Site

`tools/build_site.py` reads `registry/index.json` and emits a single-file HTML
registry explorer. The `Publish Pages` workflow builds and deploys that output
through GitHub Pages when the repository is hosted on GitHub.

## Validation Flow

```text
pull request
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
