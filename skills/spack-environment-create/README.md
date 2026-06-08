# Spack Environment Create

Use this skill to create a reproducible user-owned software environment with
Spack.

## Example

```bash
cp examples/spack.yaml ./spack.yaml
spack env create my-hpc-env ./spack.yaml
spack env activate my-hpc-env
spack concretize
```

Or use:

```bash
bash examples/create-env.sh my-hpc-env
```

## Safety Notes

This skill is `medium` risk because builds can consume significant CPU time,
storage, and quota. Prefer using a project software area or scratch build cache
when your site recommends one.
