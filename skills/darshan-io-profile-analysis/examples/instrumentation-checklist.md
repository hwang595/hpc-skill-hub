# Darshan Instrumentation Checklist

Use this checklist before collecting a new Darshan log. The default analysis
script in this skill assumes the log already exists.

## Site Policy

- Confirm whether Darshan is already enabled by the site for batch jobs.
- Confirm whether users may manually enable Darshan through compiler wrappers
  or runtime preloading.
- Confirm where logs are written and whether the path is private, shared, or
  centrally managed.
- Confirm whether logs can be shared outside the site after redaction.

## Application Fit

- Identify whether the workload uses POSIX, MPI-IO, HDF5, NetCDF, PnetCDF, or
  another I/O layer.
- Capture the expected scale, number of ranks, target filesystem, and output
  layout before collecting evidence.
- Prefer a representative short run before instrumenting a long production
  run.

## Runtime Choices

- Use site-provided modules, wrappers, or instructions when available.
- If using `LD_PRELOAD`, confirm the library path, MPI stack, and executable
  launch method match the site documentation.
- Use `darshan-config --log-path` when available to discover the configured
  default log location.
- Keep DXT trace collection disabled unless a reviewer asks for it; detailed
  traces can be large and more sensitive.

## Handoff Notes

- Record the application name, scheduler job id, task count, node count,
  filesystem, and relevant modules in a public-safe way.
- Redact private paths, usernames, project names, hostnames, and file names
  before sharing parser output.
- Preserve the original raw log privately so follow-up reviewers can regenerate
  summaries if needed.
