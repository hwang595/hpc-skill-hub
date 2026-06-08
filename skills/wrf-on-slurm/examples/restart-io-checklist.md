# WRF Restart And I/O Checklist

- Confirm WPS produced `met_em*` files for every time required by
  `interval_seconds`, start time, and end time.
- Confirm `namelist.input` dates, `dx`, `dy`, `e_we`, `e_sn`, and `max_dom`
  match the WPS domain.
- Run `real.exe` first and check `rsl.out.0000` or `real.log` for the success
  message before starting `wrf.exe`.
- Review `history_interval` and `frames_per_outfile` before long runs because
  they control `wrfout_d0*` cadence and file grouping.
- Set `restart_interval` to create `wrfrst_d0*` files before the wall-time
  limit, and preserve those files on durable storage.
- For restart runs, set the start time to the restart timestamp and set
  `restart = .true.` in `namelist.input`.
- If using split restart I/O, keep the restart processor count consistent with
  the original run unless a site WRF maintainer has reviewed the workflow.
- Keep `rsl.out.*`, `rsl.error.*`, `namelist.input`, module/container details,
  and Slurm job metadata with the run record.
