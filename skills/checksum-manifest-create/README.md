# Checksum Manifest Create

Use this skill when data should be validated before transfer, after transfer, or
before archival.

## Example

Create a checksum manifest from a file list:

```bash
bash examples/create-checksums.sh examples/files.txt checksums/sha256-manifest.txt
```

The file list should contain one path per line. Blank lines and comments are
ignored.

## Pattern

- Create a manifest of intended files before transfer.
- Generate checksums without modifying the source files.
- Keep missing-file entries visible instead of silently skipping them.
- Store the checksum manifest with transfer logs or archive metadata.
- Re-run the same manifest on the destination to compare results.

## Safety Notes

This skill is `low` risk and read-only for source files. Checksumming large
datasets can still create I/O load, so run on an appropriate filesystem and
avoid scanning shared metadata-heavy directories during peak usage.

## Success Criteria

- Every expected file has a checksum entry or an explicit missing-file entry.
- The checksum algorithm is recorded in the output header.
- The manifest can be rerun after transfer to verify data integrity.
