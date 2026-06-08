# MATLAB Batch On Slurm

Use this skill when a MATLAB script or function should run as a
non-interactive Slurm batch job with explicit license, log, and output
locations.

## Example

Review the account, partition, MATLAB module, and optional license placeholder,
then submit from this skill directory:

```bash
sbatch examples/matlab-slurm.sbatch
```

To run a different function or output directory:

```bash
MATLAB_ENTRYPOINT=my_function \
MATLAB_WORKDIR=path/to/mfiles \
OUTPUT_DIR=results/matlab-run \
  sbatch examples/matlab-slurm.sbatch
```

If the site tracks MATLAB licenses through Slurm, uncomment and replace the
`--licenses` placeholder in the example. Do not publish private license server
hostnames, feature names, or allocation policy in public skill examples.

## Pattern

- Load the site MATLAB module if your cluster requires one.
- Use `matlab -batch` for non-interactive batch execution.
- Use `-logfile` or Slurm output files so MATLAB output is captured.
- Add only the needed code directory to the MATLAB path.
- Keep outputs under an explicit user-owned directory.
- Record MATLAB version, entrypoint, output directory, thread settings, and
  license evidence in the job log.
- Avoid launching `parpool` or toolbox-heavy workflows until the site license
  and worker policy are clear.

## Safety Notes

This skill is `medium` risk because it submits scheduler jobs and may consume
limited MATLAB or toolbox license seats. The included example uses a small
single-process workload and does not request a specific license resource by
default. Confirm local license policy, Slurm license tracking, and toolbox
limits before adapting this pattern for production.

## Success Criteria

- `sbatch` accepts the script after site placeholders are replaced.
- The Slurm log and MATLAB logfile record the MATLAB version and entrypoint.
- Output files are written under the requested output directory.
- Any required license feature or Slurm license resource is documented through
  public-safe placeholders or a site adapter, not hard-coded private details.
