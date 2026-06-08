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
python3 tools/build_health.py --check
python3 tools/build_compatibility.py --check
python3 tools/build_package_data.py --check
python3 tools/build_release_manifest.py v0.1.0 --check
python3 tools/audit_safety.py
python3 tools/launch_readiness.py
python3 tools/build_site.py --output /tmp/hpc-skill-hub-site/index.html
python3 tools/hpc_skill.py list
python3 tools/hpc_skill.py collections
python3 tools/hpc_skill.py health
PYTHONPATH=src python3 -m hpc_skill_hub collection core-hpc
python3 -m pip install .
hpc-skill collection core-hpc
python3 -m unittest discover -s tests
make check
```

Review:

- `CHANGELOG.md` includes the release.
- `docs/RELEASE_NOTES_v<version>.md` is ready for GitHub release notes.
- `registry/index.json` is current.
- `docs/SKILL_CATALOG.md` is current.
- `docs/COMPATIBILITY.md` is current.
- `src/hpc_skill_hub/data/registry/` matches the generated registry JSON.
- `registry/releases/v<version>.json` is current and attached to the GitHub
  release.
- New skills have README files, examples, tests, and references.
- Medium and high-risk entries explain impact and safety notes.
- Site adapters contain only public, non-sensitive information.
- Any maturity promotions link a maturity review issue or public review
  evidence.
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

## First Seed Release

Use [v0.1.0 Release Notes](RELEASE_NOTES_v0.1.0.md) as the starting point for
the first public GitHub release body.

After `main` is pushed, GitHub Actions are green, and the Pages site is
published, inspect the release commands:

```bash
python3 tools/github_release.py v0.1.0 --repo <owner>/hpc-skill-hub
```

Run the printed commands when they look correct.
