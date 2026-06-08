# CLI

`tools/hpc_skill.py` is a zero-dependency command-line interface for exploring
the generated registry index.

Run it from the repository root:

```bash
python3 tools/hpc_skill.py list
python3 tools/hpc_skill.py search slurm
python3 tools/hpc_skill.py show slurm-submit-job --examples
python3 tools/hpc_skill.py collections
python3 tools/hpc_skill.py collection core-hpc
python3 tools/hpc_skill.py adapters
python3 tools/hpc_skill.py adapter example-campus-cluster
```

Install the package during development to use the `hpc-skill` command:

```bash
python3 -m pip install .
hpc-skill list
hpc-skill collection core-hpc
```

The installed command finds the registry from the current repository checkout.
If you run it from another directory, set `HPC_SKILL_HUB_ROOT` to the repository
root.

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
python3 tools/validate_skills.py
python3 tools/build_index.py
make check
```

## Filtering Skills

```bash
python3 tools/hpc_skill.py list --category scheduler
python3 tools/hpc_skill.py list --scheduler slurm
python3 tools/hpc_skill.py list --risk medium
python3 tools/hpc_skill.py list --tag gpu
```

## JSON Output

Every command supports JSON output for automation:

```bash
python3 tools/hpc_skill.py show gpu-sanity-check --json
python3 tools/hpc_skill.py collection core-hpc --json
python3 tools/hpc_skill.py adapters --json
```

## Updating The Index

The CLI reads `registry/index.json`. Rebuild the index after changing skills or
site adapters:

```bash
python3 tools/build_index.py
python3 tools/build_index.py --check
```

## Future Direction

This script is intentionally small. It can become the base for a packaged
`hpc-skill` command with scaffold, render, and site-aware template workflows.
