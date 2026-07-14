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
python3 tools/build_skill_quality.py --check
python3 tools/build_compatibility.py --check
python3 tools/build_skill_reviews.py --check
python3 tools/build_package_data.py --check
python3 tools/build_release_manifest.py <version> --check
python3 tools/review_packet.py --check
python3 tools/agent_benchmark_harness.py --check
python3 tools/agent_benchmark_harness.py --plan agent-bench/plans/evidence-v0.4.json --report docs/AGENT_BENCHMARK_V0_4_PLAN.md --check
python3 tools/agent_benchmark_harness.py --plan agent-bench/plans/evidence-v0.5.json --report docs/AGENT_BENCHMARK_V0_5_PLAN.md --check
python3 tools/run_agent_benchmarks.py --check
python3 tools/build_release_status.py --check
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
- `registry/skill-quality.json` is current.
- `registry/review-status.json` is current and each v0.4 pilot bundle links a
  public review issue and immutable review commit.
- `registry/release-status.json` is current, matches the package version, and
  keeps comparative evidence, maturity promotion, and tag provenance closed or
  pending unless their real evidence exists.
- `docs/SKILL_CATALOG.md` is current.
- `docs/COMPATIBILITY.md` is current.
- `docs/AGENT_BENCHMARK_V0_5_PLAN.md`, `docs/V0_5_COMPLETION.md`,
  `docs/REVIEW_PACKET_v0.4.0.md`, and the generated dashboards are current.
- `src/hpc_skill_hub/data/registry/`, `data/integrations/`, and
  `data/security/` match their generated or canonical JSON sources.
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
- Tagged package builds attest the versioned release manifest, source
  distribution, and wheel with `actions/attest@v4`; downloaded artifacts pass
  `gh attestation verify <artifact> --repo <owner>/hpc-skill-hub`.
- New skills have README files, examples, tests, and references.
- Medium and high-risk entries explain impact and safety notes.
- Site adapters contain only public, non-sensitive information.
- Any maturity promotions link a maturity review issue or public review
  evidence.
- Any comparative benchmark claim is backed by a complete, blinded campaign;
  otherwise the comparative publication gate stays closed and the release
  notes state that no measured-lift claim is being made.
- `Validate` and `Package` GitHub Actions are green on `main`.

See [Release Provenance](RELEASE_PROVENANCE.md) for the tag-time signing and
verification boundary.

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
[v0.5.0 Release Notes](RELEASE_NOTES_v0.5.0.md), as the starting point for the
GitHub release body.

After `main` is pushed, GitHub Actions are green, the Pages site is published,
and the repository homepage points at the Pages URL, inspect the release
commands:

```bash
python3 tools/github_release.py <version> --repo <owner>/hpc-skill-hub
```

Run the printed commands when they look correct.
