# RStudio On Slurm

Use this skill when R users need an RStudio or Posit IDE session backed by a
scheduled Slurm allocation instead of a login node.

The examples default to plan-only mode. They do not install RStudio, start a
system service, or assume administrator privileges. Set `RUN_RSTUDIO_SESSION=1`
only after the site provides an approved launch path, such as Posit Workbench
Launcher, Open OnDemand, or a user-safe wrapper command.

## Examples

```bash
bash examples/rstudio-preflight.sh /path/to/project
sbatch examples/rstudio-session.sbatch
RSTUDIO_LAUNCH_CMD="<site-approved-wrapper>" RUN_RSTUDIO_SESSION=1 sbatch examples/rstudio-session.sbatch
bash examples/tunnel-template.sh <compute-host> 8787 8787
```

## Adaptation Points

- Replace `<account>`, `<debug-partition>`, and `<login-host>`.
- Prefer Posit Workbench with Slurm Launcher or a site-maintained Open OnDemand
  app when available.
- Use a short wall time and a debug or interactive partition.
- Keep the project directory on storage suitable for interactive editing.
- Use only the R module, package library, and RStudio wrapper approved by the
  local site.

## Safety Notes

This skill is `medium` risk because web IDE sessions consume compute resources,
can expose a browser-accessible service, and may run terminal commands under
the user's account. Some facilities prohibit user-started RStudio Server
processes or tunnels. Review the site policy checklist before enabling
`RUN_RSTUDIO_SESSION=1`.

## Success Criteria

- The Slurm log shows a compute hostname and selected project directory.
- R is available and reports the expected library paths.
- The RStudio session runs only inside the scheduled allocation.
- The user cancels the job or exits the Workbench session when finished.
