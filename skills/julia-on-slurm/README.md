# Julia On Slurm

Use this skill when a Julia workload should run as a Slurm batch job with
explicit project, package depot, thread, log, and output locations.

## Example

Review the account, partition, and Julia module placeholders, then submit from
this skill directory:

```bash
sbatch examples/julia-slurm.sbatch
```

To run a different script, project, depot, or output directory:

```bash
JULIA_SCRIPT=path/to/analysis.jl \
JULIA_PROJECT_DIR=path/to/project \
JULIA_DEPOT_PATH=/path/to/user/julia-depot: \
OUTPUT_DIR=results/julia-run \
  sbatch examples/julia-slurm.sbatch
```

Use a project, scratch, or software path for `JULIA_DEPOT_PATH`. The trailing
colon keeps access to bundled Julia resources while moving user package writes
to the chosen depot.

## Pattern

- Load the site Julia module if your cluster requires one.
- Set `JULIA_DEPOT_PATH` before starting Julia so packages, registries,
  artifacts, and precompile caches land in a user-owned location.
- Use an explicit project directory containing `Project.toml`.
- Match `JULIA_NUM_THREADS` or `--threads` to `SLURM_CPUS_PER_TASK`.
- Keep logs and outputs under explicit directories.
- Record Julia version, project path, depot path, load path, and thread count
  in the job log.

## Safety Notes

This skill is `medium` risk because it submits scheduler jobs and Julia package
operations can write many files while resolving, downloading, or precompiling
packages. The included example uses only Julia standard libraries and small
synthetic data. Run package instantiation as a separate, reviewed preparation
step when possible, and follow local policy for depots, artifacts, and scratch
usage.

## Success Criteria

- `sbatch` accepts the script after site placeholders are replaced.
- The Slurm log records Julia version, `JULIA_DEPOT_PATH`, `DEPOT_PATH`,
  `LOAD_PATH`, project path, and thread count.
- Output files are written under the requested output directory.
- The selected depot is user-owned and appropriate for package caches and
  precompile output.
