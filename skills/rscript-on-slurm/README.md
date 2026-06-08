# Rscript On Slurm

Use this skill when an R analysis script should run as a Slurm batch job with
explicit package library, log, and output locations.

## Example

Review the account, partition, and R module placeholders, then submit:

```bash
sbatch examples/rscript-slurm.sbatch
```

To run a different script or output directory:

```bash
R_SCRIPT=path/to/analysis.R OUTPUT_DIR=results/r-run \
  sbatch examples/rscript-slurm.sbatch
```

Use a project, scratch, or software path for `R_LIBS_USER` when packages are
installed by the user. Avoid filling home directories with large package trees.

## Pattern

- Load the site R module if your cluster requires one.
- Set `R_LIBS_USER` to a user-owned path before running Rscript.
- Keep logs and analysis outputs under explicit directories.
- Run `Rscript --vanilla` so startup files do not silently change results.
- Print R version, library paths, and `sessionInfo()` in the job log.
- Keep package installation separate from production batch jobs when possible.

## Safety Notes

This skill is `medium` risk because it submits scheduler jobs and can write
many files if package installation is added. The included example uses only
base R and small synthetic data. Follow local policy for package caches,
compiled R packages, temporary directories, and shared filesystem usage.

## Success Criteria

- `sbatch` accepts the script after site placeholders are replaced.
- The Slurm log records the R version, `R_LIBS_USER`, `.libPaths()`, and
  `sessionInfo()`.
- Output files are written under the requested output directory.
- User package libraries are stored in an approved user-owned path.
