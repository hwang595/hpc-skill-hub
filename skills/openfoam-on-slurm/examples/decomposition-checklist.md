# OpenFOAM Decomposition Checklist

- Confirm the case has `0`, `constant`, and `system` directories before staging.
- Match `numberOfSubdomains` to the intended Slurm task count.
- Choose a simple decomposition shape that fits the mesh dimensions before
  using graph-based methods on production cases.
- Run `blockMesh` or the site-approved meshing workflow before `decomposePar`.
- Run the solver with `-parallel` under the site-approved Slurm launcher.
- Reconstruct only the fields and time ranges that are needed for analysis.
- Preserve the launch record with solver, decomposition, module stack, and case
  paths before scaling.
