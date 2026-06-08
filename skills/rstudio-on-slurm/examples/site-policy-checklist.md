# Site Policy Checklist

Confirm these items before starting an RStudio or Posit IDE session on Slurm:

- Posit Workbench Launcher, Open OnDemand, or a site-approved user wrapper is
  the preferred launch path.
- User-started RStudio Server processes are allowed, or explicitly avoided.
- Any SSH tunnel or browser endpoint follows local access policy.
- The project directory does not contain restricted data that should not be
  exposed through an interactive web session.
- The allocation uses a short wall time and an appropriate interactive or debug
  partition.
- R package libraries are on storage suitable for many small files.
- The session is stopped and the Slurm job is cancelled when work is finished.
