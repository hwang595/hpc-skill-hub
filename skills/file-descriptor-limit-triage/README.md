# File Descriptor Limit Triage

Use this skill when a job or workflow reports `Too many open files`, `EMFILE`,
`unable to open file`, unexplained data-loader crashes, worker failures, or
metadata-heavy failures after opening many files.

This is common in:

- Python data loaders and multiprocessing pools.
- Nextflow, Snakemake, CWL, WDL, Dask, Ray, and Parsl workers.
- MPI jobs where many ranks open logs, checkpoints, shards, or shared metadata.
- Many-small-file datasets, tar extraction, temporary-file fan-out, and archive
  preparation.

## Example

Inspect the current shell limits:

```bash
bash examples/fd-limit-triage.sh
```

Inspect a running process and a log:

```bash
bash examples/fd-limit-triage.sh 12345 slurm-12345.out
```

## What It Collects

- Current shell `ulimit -n`, `ulimit -Hn`, and `ulimit -a` output.
- `/proc/<pid>/limits` and `/proc/<pid>/fd` counts when available.
- Optional `lsof -p <pid>` counts when the site permits `lsof`.
- Recent log lines and matching symptoms such as `Too many open files`,
  `EMFILE`, `ulimit`, `RLIMIT_NOFILE`, and file open errors.
- Review prompts for worker fan-out, per-process leaks, and many-small-file
  patterns.

## Safety Notes

This skill is read-only. It does not change `ulimit`, scheduler limits, systemd
limits, PAM limits, process state, or workflow configuration. Do not post raw
`lsof`, `/proc`, or log output publicly without redacting paths, usernames,
project names, dataset names, and command lines.
