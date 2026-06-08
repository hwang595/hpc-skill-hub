# Conda Mamba On HPC

Use this skill when a workload needs a Conda, Mamba, or Micromamba environment
and the site allows user-managed package environments.

## Example

Choose a user-owned prefix and cache path that match site policy:

```bash
CONDA_PKGS_DIRS=<scratch-or-project-cache> \
  bash examples/create-conda-env.sh <env-prefix> examples/environment.yml
```

Prefer project or software storage for reusable environments. Avoid large
package trees in home directories or metadata-sensitive shared filesystems.

## Pattern

- Use an explicit prefix instead of relying on a hidden default environment.
- Keep package caches in a site-approved user-owned location.
- Put channels and dependencies in `environment.yml`.
- Export both YAML and package list after creation.
- Activate the prefix inside batch jobs before running the workload.

## Safety Notes

This skill is `medium` risk because Conda-style installs can write many files,
consume quota, and stress shared metadata services. Start with small
environments, avoid unnecessary package churn, and follow local policy for
caches and environment storage.

## Success Criteria

- The environment is created under the requested prefix.
- The chosen cache path is user-owned and policy-compliant.
- `conda list` or equivalent is exported.
- A fresh shell or Slurm job can activate the environment by prefix.
