# Python Virtualenv On HPC

Use this skill when a Python workload needs a lightweight user-owned
environment that is tied to explicit module and Python version assumptions.

## Example

Review the target path, load any site Python module, then run:

```bash
bash examples/create-venv.sh <venv-path> examples/requirements.txt
```

Use project or software storage for reusable environments. Avoid creating large
package trees in home directories with small quotas.

## Pattern

- Load a site Python module if your cluster requires one.
- Create the virtual environment in a user-owned prefix.
- Upgrade packaging tools only when local policy and network access allow it.
- Install from a pinned requirements file.
- Record Python version, pip version, module state, and installed packages.
- Activate the same environment inside Slurm jobs before running Python code.

## Safety Notes

This skill is `low` risk when used with small pinned requirements and
user-owned paths. Package installation may use network access and write many
small files, so follow local policy for package caches and shared filesystems.

## Success Criteria

- `python -V` and `pip --version` are recorded.
- `pip freeze` is saved with the environment.
- The environment activates from a fresh shell or batch job.
- The environment path and package cache location are acceptable for the site.
