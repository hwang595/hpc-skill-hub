# Example Campus Cluster Adapter

This is a non-production site adapter. It shows how an HPC center can map
generic registry skills to local partitions, modules, storage paths, and policy
notes without forking the core skill definitions.

## What To Replace

- Partition names and wall-time limits.
- Module names for MPI, CUDA/ROCm, Python, and workflow engines.
- Storage path conventions.
- Help desk URLs and local support contacts.
- Skill override notes that clarify local policy.

## What Not To Include

- Private hostnames.
- Usernames, project ids, tokens, or allocation names.
- Internal security procedures.
- Non-public storage paths or dataset names.

## Validation

Run from the repository root:

```bash
python3 tools/validate_skills.py
```
