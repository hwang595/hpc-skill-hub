# File Descriptor Review Checklist

Use this checklist after collecting `fd-limit-triage.sh` output. Keep private
paths, usernames, project names, dataset names, and command lines out of public
issues.

## Limit Evidence

- Record current shell soft and hard `nofile` limits.
- On Linux, compare `/proc/<pid>/limits` with the shell limit to see whether
  batch launch changed the limit.
- Confirm whether the failing process is the scheduler batch shell, a worker, a
  data-loader process, a workflow-engine child, or an MPI rank.

## Open Descriptor Pressure

- Compare the open descriptor count with the soft limit.
- If one process is near the limit, look for a descriptor leak or one worker
  opening too many shards, logs, sockets, pipes, or temporary files.
- If many processes each open a moderate number, reduce worker count, rank fan
  out, open-at-once shard count, or per-task concurrency.

## Workload Shape

- For Python data loaders, check worker count, persistent workers, prefetch
  factor, and dataset shard fan-out.
- For workflow engines, check how many tasks run concurrently and whether each
  task opens many files.
- For MPI jobs, check whether every rank opens the same files, logs, or
  checkpoints independently.
- For many-small-file datasets, consider packing, batching, sharding, or
  staging to a filesystem suited to metadata-heavy access.

## Support Packet

- Redacted `ulimit -n`, `ulimit -Hn`, and `/proc/<pid>/limits` output.
- Redacted fd count or `lsof` summary.
- Exact redacted error lines from logs.
- Worker/rank/task counts and any data-loader or workflow concurrency settings.
- Whether the user requests a limit change or needs workflow restructuring.
