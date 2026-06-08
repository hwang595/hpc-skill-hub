# Launch Readiness

Use launch readiness checks before publishing the local seed repository to
GitHub or before cutting the first public release.

The readiness audit is intentionally local. It does not create repositories,
push branches, edit GitHub settings, create labels, open issues, or publish a
release. It reports what can be verified from the working tree and highlights
which GitHub actions still need an authenticated environment.

## Run The Audit

```bash
python3 tools/launch_readiness.py
```

For machine-readable output:

```bash
python3 tools/launch_readiness.py --json
```

To include the full local gate:

```bash
python3 tools/launch_readiness.py --run-check
```

## Interpreting Results

- `OK`: the local evidence is present and current.
- `WARN`: the item needs human follow-up or an external GitHub environment, but
  does not mean the local repository is broken.
- `FAIL`: a required launch artifact is missing, stale, or inconsistent.

Expected warnings before the first push include:

- `git-remote`: no `origin` remote has been configured yet.
- `gh-cli`: GitHub CLI is not available in the current environment.
- `make-check`: omitted unless `--run-check` is passed.
- `git-remote`: remains a warning until the public GitHub remote is configured.

## Related Commands

The readiness audit complements the command generators:

```bash
python3 tools/github_publish_plan.py --owner <owner> --run-check
python3 tools/build_package_data.py --check
python3 tools/build_release_manifest.py v0.1.0 --check
python3 tools/validate_registry_artifacts.py
python3 -m pip install --upgrade build twine
python3 -m build --sdist --wheel
python3 -m twine check dist/*
python3 tools/github_repo.py --owner <owner>
python3 tools/github_labels.py --repo <owner>/hpc-skill-hub
python3 tools/github_issues.py --repo <owner>/hpc-skill-hub --include-pin-notes
python3 tools/github_rulesets.py --repo <owner>/hpc-skill-hub
python3 tools/github_release.py v0.1.0 --repo <owner>/hpc-skill-hub
```

Review generated commands before running them. They are meant to be executed in
an authenticated GitHub environment after the local checks are clean.

`tools/github_publish_plan.py` is the safest first command because it prints the
ordered launch path and embeds the current readiness summary without taking any
networked action.
