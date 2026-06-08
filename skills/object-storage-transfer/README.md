# Object Storage Transfer

Use this skill when a workflow needs to move data between an HPC filesystem and
S3-compatible or cloud object storage. It is written for rclone first, with a
small AWS CLI example for sites that standardize on `aws s3 sync`.

## Example

Plan a non-destructive rclone copy without moving data:

```bash
bash examples/rclone-object-transfer.sh <source-uri> <destination-uri>
```

Run only after reviewing the dry-run log and destination prefix:

```bash
RUN_OBJECT_TRANSFER=1 bash examples/rclone-object-transfer.sh <source-uri> <destination-uri>
```

Use `OBJECT_TRANSFER_MODE=sync` only when the destination should match the
source exactly. Actual sync requires an additional explicit opt-in:

```bash
OBJECT_TRANSFER_MODE=sync ALLOW_OBJECT_SYNC_DELETE=1 RUN_OBJECT_TRANSFER=1 \
  bash examples/rclone-object-transfer.sh <source-uri> <destination-uri>
```

## Pattern

- Keep credentials in site-approved rclone config, AWS profiles, or managed
  identity mechanisms rather than command lines.
- Start with `rclone copy --dry-run`; it does not delete destination objects.
- Use `sync` only after reviewing deletion behavior and destination scope.
- Add bandwidth, transfer count, and checker limits when running from shared
  login nodes or data transfer nodes.
- Save transfer logs and combined reports for support handoff.
- Run a small test prefix before moving a full dataset.
- Prefer Globus or site-managed transfer tools for very large, policy-sensitive,
  or cross-institution transfers.

## Safety Notes

This skill is `medium` risk because object-storage transfers can overwrite
objects, consume shared network bandwidth, and, in sync mode, delete destination
objects. The rclone example defaults to dry-run copy mode and requires
`RUN_OBJECT_TRANSFER=1` before copying data. Actual sync mode also requires
`ALLOW_OBJECT_SYNC_DELETE=1`.

The examples do not print credential environment variables. Do not pass access
keys, session tokens, or secret keys as command-line arguments.

## Success Criteria

- The dry-run log contains the expected source and destination prefixes.
- The selected mode is `copy` unless destination deletion has been approved.
- Transfer limits match site policy for the node where the command runs.
- The actual transfer log and combined report are saved.
- Optional post-transfer `rclone check` output is recorded for the test prefix
  or dataset.
