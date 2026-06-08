# OpenFOAM On Slurm

Use this skill when a CFD case needs a conservative OpenFOAM launch pattern on
a Slurm cluster, especially when choosing MPI ranks, domain decomposition, and
output reconstruction.

## Example

Create a launch plan:

```bash
bash examples/openfoam-smoke.sbatch
```

After loading a site-approved OpenFOAM module or container, run the tiny cavity
case explicitly:

```bash
RUN_OPENFOAM=1 OPENFOAM_NTASKS=2 bash examples/openfoam-smoke.sbatch
```

## Pattern

- Start with a small case template and stage it into a job-owned output
  directory.
- Record Slurm layout, solver, case path, decomposition count, decomposition
  shape, and reconstruction command before scaling.
- Use `decomposePar` before the solver and run the solver with `-parallel`.
- Use `reconstructPar` only after confirming processor outputs and storage
  volume are acceptable.
- Keep run records separate from large result directories.

## Safety Notes

This skill is `medium` risk because OpenFOAM jobs can consume many CPU hours
and write large processor directories and reconstructed fields. The example
defaults to plan-only mode and only stages the case, writes `decomposeParDict`,
runs `blockMesh`, `decomposePar`, the solver, and `reconstructPar` when
`RUN_OPENFOAM=1` is set.

## Success Criteria

- The plan records case template, staged case path, solver, Slurm tasks,
  decomposition settings, solver command, and reconstruction command.
- A small smoke case runs before production input is submitted.
- Processor directory count matches the intended MPI task count.
- Reconstruction and output retention are reviewed before long runs.
