# WRF On Slurm

Use this skill when a real-data WRF case needs a conservative Slurm launch
pattern, especially when choosing MPI ranks, staging a clean run directory,
reviewing restart settings, and controlling output volume.

## Example

Create a launch plan:

```bash
bash examples/wrf-realdata.sbatch
```

After loading a site-approved WRF module or container, run with a small
WPS-generated `met_em` set and a clean WRF run template:

```bash
RUN_WRF=1 \
WRF_RUN_TEMPLATE=/path/to/WRF/run-template \
WRF_MET_EM_GLOB='/path/to/WPS/met_em.d01.*.nc' \
WRF_WRF_NTASKS=16 \
bash examples/wrf-realdata.sbatch
```

## Pattern

- Start from a clean WRF run directory template that contains `real.exe`,
  `wrf.exe`, physics tables, and site-approved runtime files.
- Keep `namelist.input` under review with the WPS domain, dates, grid
  dimensions, output cadence, restart cadence, and I/O format.
- Use fewer ranks for `real.exe` than for `wrf.exe` unless local scaling
  evidence says otherwise.
- Treat `rsl.out.*` and `rsl.error.*` as primary evidence for MPI runs.
- Preserve `wrfinput_d0*`, `wrfbdy_d01`, `wrfout_d0*`, and `wrfrst_d0*` on
  durable storage according to the site's data-retention policy.

## Safety Notes

This skill is `medium` risk because WRF jobs can consume many node-hours and
produce large NetCDF output and restart files. The example defaults to
plan-only mode and only stages files, links `met_em` inputs, runs `real.exe`,
and runs `wrf.exe` when `RUN_WRF=1` is set.

## Success Criteria

- The plan records WRF template path, namelist path, met_em pattern, staged
  work directory, Slurm layout, `real.exe` command, and `wrf.exe` command.
- `real.exe` produces `wrfinput_d0*` and `wrfbdy_d01` before `wrf.exe` starts.
- MPI logs include the expected number of `rsl.out.*` and `rsl.error.*` files.
- Restart interval and history output cadence are reviewed before long runs.
