# Quota And Filesystem Triage

Use this skill when a job or workflow fails with storage-like symptoms and the
user needs to distinguish quota, inode, capacity, and permission issues.

## Example

```bash
bash examples/filesystem-triage.sh <path> [log-file]
```

If no path is provided, the script inspects the current directory. If a log file
is provided, it searches for common storage-related error messages.

## Common Signals

- `No space left on device`: filesystem capacity, quota, or inode exhaustion.
- `Disk quota exceeded`: user or group quota limit.
- `Permission denied`: directory ownership, group access, or ACL mismatch.
- Very high inode use: many small files can fail jobs even when byte usage looks
  acceptable.
- Write failures in scratch: check site retention policy and whether the job
  writes to the intended filesystem.

## What To Capture For Support

- Filesystem capacity and inode usage for the affected path.
- Output from `quota` if the site provides it.
- The path that failed and the command or application writing to it.
- The last relevant log lines around the failure.
- Whether the path is home, scratch, project, or temporary job storage.

## Safety Notes

This skill is read-only. Logs and filesystem paths can contain private dataset,
project, or user information, so redact sensitive values before sharing.
