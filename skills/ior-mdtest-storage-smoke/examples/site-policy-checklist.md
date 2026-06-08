# Site Policy Checklist

Confirm these items before running IOR or MDTest on a shared HPC filesystem:

- Storage benchmarks are allowed for regular users on the target filesystem.
- The selected partition, wall time, and task count are appropriate for a tiny
  smoke run.
- The target directory is scratch or another benchmark-approved location, not a
  login-node filesystem or home directory.
- The run will not overlap with production acceptance testing, maintenance
  windows, or incident response.
- The benchmark size, file count, and metadata count are small enough for a
  support request or teaching demo.
- Results will be reported as local evidence, not as a site-wide performance
  claim.
- The marked run directory will be removed after outputs are captured.
