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
