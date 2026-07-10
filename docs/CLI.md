# CLI

`tools/hpc_skill.py` is a zero-dependency command-line interface for exploring
the generated registry index and scaffolding new contributions.

Run it from the repository root:

```bash
python3 tools/hpc_skill.py list
python3 tools/hpc_skill.py search slurm
python3 tools/hpc_skill.py show slurm-submit-job --examples
python3 tools/hpc_skill.py collections
python3 tools/hpc_skill.py collection core-hpc
python3 tools/hpc_skill.py health
python3 tools/hpc_skill.py validate
python3 tools/hpc_skill.py security skills/slurm-submit-job
python3 tools/hpc_skill.py adapters
python3 tools/hpc_skill.py adapter example-campus-cluster
```

Install the package during development to use the `hpc-skill` command:

```bash
python3 -m pip install .
hpc-skill list
hpc-skill collection core-hpc
hpc-skill security ./community-skill --format json
```

The installed command can run read-only discovery commands from the packaged
registry snapshot. When a full checkout is available, it prefers the current
repository's `registry/index.json` and `registry/health.json`. For commands
that validate or write repository files, run from the repository root or set
`HPC_SKILL_HUB_ROOT` to the repository root.

For code changes without reinstalling:

```bash
PYTHONPATH=src python3 -m hpc_skill_hub collections
```

## Scaffolding Contributions

Create a draft skill:

```bash
python3 tools/hpc_skill.py scaffold skill my-new-skill --category education --tool bash
```

Create a draft site adapter:

```bash
python3 tools/hpc_skill.py scaffold site-adapter my-campus-cluster --name "My Campus Cluster"
```

Scaffolds are written into the current repository by default. Use `--root` for
experiments or CI smoke tests:

```bash
python3 tools/hpc_skill.py scaffold skill ci-test-skill --root /tmp/hpc-skill-hub-scaffold
```

After editing scaffolded files, run:

```bash
python3 tools/hpc_skill.py validate --skill my-new-skill
python3 tools/build_index.py
python3 tools/build_health.py
python3 tools/hpc_skill.py validate
make check
```

## Validating Contributions

Validate one skill while iterating:

```bash
python3 tools/hpc_skill.py validate --skill slurm-submit-job
```

Validate the full registry before opening a pull request:

```bash
python3 tools/hpc_skill.py validate
```

The full command checks manifest metadata, generated registry index freshness,
registry health freshness, compatibility table freshness, and the safety audit.
It also blocks high or critical community skill security findings. Single-skill
validation skips generated registry checks and audits/scans only that skill
directory.

## Scanning Community Skills

Scan an HPC Skill Hub package, agent `SKILL.md` directory, or parent directory
without executing its content:

```bash
hpc-skill security ./community-skill
hpc-skill security ./community-skill --format json
hpc-skill security ./community-skill --format sarif
```

The default threshold fails on `high` and `critical`; lower-severity findings
produce a `review` verdict. See [Community Skill Security](SKILL_SECURITY.md).

## Filtering Skills

```bash
python3 tools/hpc_skill.py list --category scheduler
python3 tools/hpc_skill.py list --scheduler slurm
python3 tools/hpc_skill.py list --risk medium
python3 tools/hpc_skill.py list --tag gpu
```

## JSON Output

Discovery commands support JSON output for automation:

```bash
python3 tools/hpc_skill.py show gpu-sanity-check --json
python3 tools/hpc_skill.py collection core-hpc --json
python3 tools/hpc_skill.py health --json
python3 tools/hpc_skill.py adapters --json
```

## Updating The Index

The CLI reads `registry/index.json`. Rebuild the index after changing skills or
site adapters:

```bash
python3 tools/build_index.py
python3 tools/build_index.py --check
python3 tools/build_health.py
python3 tools/build_health.py --check
python3 tools/build_compatibility.py
python3 tools/build_compatibility.py --check
python3 tools/build_package_data.py
python3 tools/build_package_data.py --check
python3 tools/validate_registry_artifacts.py
```

## Future Direction

The CLI is intentionally small and already installable as `hpc-skill`. Next
steps include richer security policy packs, template rendering, and site-aware
generation for common scheduler and workflow files.
