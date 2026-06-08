# Module Environment Debug

Use this skill when software fails after loading modules, changing compilers, or
moving between login and compute nodes.

## Example

```bash
bash examples/env-report.sh /path/to/executable
```

## What To Look For

- Multiple compiler or MPI families loaded at the same time.
- `which mpirun` and `which mpicc` pointing to different stacks.
- Empty or surprising `LD_LIBRARY_PATH`.
- Executables linked to libraries that are not available on compute nodes.

## Safety Notes

This skill is read-only and does not load, unload, or purge modules.
