# Rsync Data Transfer

Use this skill for small to medium data transfers where `rsync` is appropriate
and Globus or another managed transfer service is not needed.

## Example

Plan a transfer without copying data:

```bash
bash examples/rsync-plan.sh <source-path> <destination-path>
```

Run only after reviewing the dry-run log:

```bash
RUN_TRANSFER=1 bash examples/rsync-plan.sh <source-path> <destination-path>
```

## Pattern

- Start with a dry run and save the log.
- Use archive mode and partial transfer support for resumability.
- Add `--delete` only when the destination should mirror the source exactly.
- Capture post-transfer validation with checksums or file counts.
- Prefer Globus or site-managed tools for very large, cross-site, or
  policy-sensitive transfers.

## Safety Notes

This skill is `medium` risk because `rsync` can overwrite destination files and
consume I/O bandwidth. The example defaults to dry-run mode and requires
`RUN_TRANSFER=1` before it copies data.

## Success Criteria

- The dry-run log contains the expected source and destination paths.
- The actual transfer log is saved.
- Destination files match expected counts or checksums.
- Any destructive flags are reviewed before use.
