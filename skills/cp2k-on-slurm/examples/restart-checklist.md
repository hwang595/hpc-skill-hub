# CP2K Restart Checklist

- Confirm the project prefix used by the previous run and preserve all
  project-prefixed restart, wavefunction, trajectory, and log files.
- Confirm restart files are on durable project or scratch storage, not only
  node-local temporary storage.
- Record the exact CP2K executable, module or container, input file, data-file
  paths, Slurm job id, MPI layout, and `OMP_NUM_THREADS`.
- Review whether the follow-on input needs `EXT_RESTART`, `WFN_RESTART_FILE_NAME`,
  or run-type-specific restart keywords.
- Before a production continuation, run a short continuation test and compare
  energy, forces, and expected trajectory or restart outputs.
- Review trajectory, cube, restart, and wavefunction output volume before
  increasing run length or system size.
