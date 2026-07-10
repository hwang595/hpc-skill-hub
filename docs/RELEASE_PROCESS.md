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
python3 tools/build_release_manifest.py <version> --check
python3 tools/review_packet.py --check
python3 tools/validate_registry_artifacts.py
python3 tools/audit_safety.py
python3 tools/scan_skill_security.py skills --fail-on high
python3 tools/launch_readiness.py
python3 tools/build_site.py --output /tmp/hpc-skill-hub-site/index.html
python3 tools/hpc_skill.py list
python3 tools/hpc_skill.py collections
python3 tools/hpc_skill.py health
PYTHONPATH=src python3 -m hpc_skill_hub collection core-hpc
python3 -m pip install .
hpc-skill collection core-hpc
python3 -m pip install --upgrade build twine
python3 -m build --sdist --wheel
python3 -m twine check dist/*
python3 -m unittest discover -s tests
make check
```

Review:

- `CHANGELOG.md` includes the release.
- `docs/RELEASE_NOTES_v<version>.md` is ready for GitHub release notes.
- `pyproject.toml`, `setup.py`, `src/hpc_skill_hub/__init__.py`,
  `CITATION.cff`, and the README badge agree on the repository version.
- `registry/index.json` is current.
- `docs/SKILL_CATALOG.md` is current.
- `docs/COMPATIBILITY.md` is current.
- `src/hpc_skill_hub/data/registry/` matches the generated registry JSON.
- Registry index, health, release manifest, package data, and schema pointers
  pass `tools/validate_registry_artifacts.py`.
- `registry/releases/v<version>.json` is current and attached to the GitHub
  release.
- Previously published release manifests remain byte-for-byte unchanged;
  development validation uses `validate_registry_artifacts.py --release-only`.
- For `v0.2.0` and later reviewed-skill pilot releases,
  `docs/REVIEW_PACKET_v0.2.0.md` or its successor is current.
- Built source and wheel distributions pass `twine check`, and the `Package`
  workflow smoke tests the installed `hpc-skill` CLI outside the checkout.
- New skills have README files, examples, tests, and references.
- Medium and high-risk entries explain impact and safety notes.
- Site adapters contain only public, non-sensitive information.
- Any maturity promotions link a maturity review issue or public review
  evidence.
- `Validate` and `Package` GitHub Actions are green on `main`.

## Release Notes Template

```markdown
## Added

## Changed

## Fixed

## Skills

## Site Adapters

## Safety Notes
```

## Release Command Generator

Use the matching release notes, such as
[v0.2.0 Release Notes](RELEASE_NOTES_v0.2.0.md), as the starting point for the
GitHub release body.

After `main` is pushed, GitHub Actions are green, the Pages site is published,
and the repository homepage points at the Pages URL, inspect the release
commands:

```bash
python3 tools/github_release.py <version> --repo <owner>/hpc-skill-hub
```

Run the printed commands when they look correct.
