# Release Process

Use releases to mark stable schema and registry snapshots.

## Versioning

Use semantic versioning for repository releases:

- Patch: documentation, examples, or validator fixes that do not change schema.
- Minor: new skills, new site adapter fields, or compatible CLI features.
- Major: breaking schema or CLI changes.

Individual skills keep their own `version` field in `skill.json`.

## Pre-Release Checklist

Run:

```bash
python3 tools/validate_skills.py
python3 tools/build_index.py --check
python3 tools/build_site.py --output /tmp/hpc-skill-hub-site/index.html
python3 tools/hpc_skill.py list
python3 tools/hpc_skill.py collections
python3 -m unittest discover -s tests
make check
```

Review:

- `registry/index.json` is current.
- `docs/SKILL_CATALOG.md` is current.
- New skills have README files, examples, tests, and references.
- Medium and high-risk entries explain impact and safety notes.
- Site adapters contain only public, non-sensitive information.
- GitHub Actions are green on `main`.

## Release Notes Template

```markdown
## Added

## Changed

## Fixed

## Skills

## Site Adapters

## Safety Notes
```
