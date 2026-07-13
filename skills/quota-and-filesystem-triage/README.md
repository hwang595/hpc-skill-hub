# Quota And Filesystem Triage

Use this skill to distinguish byte-capacity, inode, user/group quota,
permissions, read-only mount, and filesystem I/O signals before deleting data,
moving a workload, or requesting policy changes. It collects bounded read-only
evidence for one user-selected path and an optional application log.

## Prerequisites

- Ask the user for the affected path and optional log file. Start with the
  narrowest directory that reproduces the failure and do not scan unrelated
  project trees.
- Confirm the user is allowed to inspect the path and log. Preserve private
  dataset names, project identifiers, usernames, and mount details.
- Treat `quota` output as optional because commands, units, user/group/project
  quota models, and reporting delays vary by site and filesystem.
- Do not assume `No space left on device` proves global byte capacity; quota or
  inode exhaustion can produce similar application behavior.

## Inputs And Outputs

Inputs are an existing file or directory and an optional existing log. Output is
terminal-only evidence from `df`, optional `quota`, a write-permission check, and
bounded log excerpts. The script does not create files, test writes, traverse
the directory tree, change permissions, or delete data.

## Workflow

1. Review the path and log for privacy before running anything. Then collect the
   report:

   ```bash
   bash examples/filesystem-triage.sh <path> [log-file]
   ```

   With no path, the script inspects the current directory. A missing target or
   requested log is an error rather than silently incomplete evidence.
2. Record filesystem byte use and inode use separately. Compare them with any
   visible user, group, or project quota output.
3. Check whether the selected directory is writable by the current identity,
   then correlate the earliest relevant application log line.
4. Fill in `examples/storage-evidence-checklist.md`, distinguishing facts from
   hypotheses and identifying the filesystem owner or site team when local
   policy evidence is required.
5. Plan remediation only after the limiting dimension is known. Deletion,
   permission changes, quota requests, data movement, and retries are separate
   user-approved actions.

## Failure Modes

| Signal | Possible explanation | Next read-only evidence |
| --- | --- | --- |
| `No space left on device` | Filesystem bytes, quota, or inodes exhausted | Compare `df -h`, `df -ih`, quota, and the failing path's mount |
| `Disk quota exceeded` | User, group, or project limit reached | Identify quota scope and whether accounting has caught up |
| High `IUse%` with free bytes | Too many files/directories or metadata limit | Confirm inode pressure; do not infer which files should be removed |
| `Permission denied` | Ownership, group, ACL, traversal, or read-only mount | Route to permission triage and inspect each path component read-only |
| `Read-only file system` | Mount state, snapshot, policy, or wrong target | Confirm mount/path identity and prepare a support handoff |
| `Input/output error` or stale handle | Storage or client/server issue may dominate | Preserve timestamps, path, node/job context, and contact site support |

Several limits can be high simultaneously. A writable-directory check reflects
the current identity and mode/ACL evaluation, but it does not perform a real
write or prove that quota and runtime mount state will allow a job to write.

## Validation

A complete report identifies the selected path, distinguishes byte and inode
pressure, states whether quota evidence was available, records permission and
log signals, and leaves uncertain causes unresolved. Success means one bounded
next diagnostic or support handoff is justified by evidence; it does not mean a
write was attempted or the filesystem was modified.

## Resource And Cost

The example is read-only and bounded: `df`, `quota`, permission tests, `tail`,
and streaming `grep` use negligible CPU and do not recursively walk the target.
Large logs still consume read bandwidth during `grep`, so select the relevant
log and avoid repeatedly scanning shared filesystems.

## Cleanup

No cleanup is required because the script writes no files and changes no
filesystem state. Any later deletion, archive, migration, permission repair, or
quota request needs its own scope, ownership check, cost estimate, validation,
and rollback or recovery plan.

## Site Adaptation

Home, project, scratch, object, and temporary filesystems have different quota,
inode, retention, backup, purge, and support policies. Resolve mount names and
policy through a public site adapter or user-provided documentation. Redact
private paths, usernames, group/project names, hostnames, and dataset fragments
before sharing output.

## Safety Notes

This skill is `low` risk and read-only. Never turn a storage triage request into
`rm`, recursive traversal, `chmod`, `chown`, quota changes, transfer, or job
resubmission without a separate explicit request and review of data ownership
and recovery implications.
