# Large File Archive Prepare

Use this skill when an HPC dataset is ready for archival, publication,
support handoff, or movement into long-term storage.

## Example

Create a reviewable archive plan:

```bash
bash examples/prepare-archive.sh /path/to/dataset project-run-001
```

After reviewing the manifest and plan, create the archive explicitly:

```bash
CREATE_ARCHIVE=1 bash examples/prepare-archive.sh /path/to/dataset project-run-001
```

## Pattern

- Identify the exact directory or file that should be archived.
- Generate a sorted manifest before creating any package.
- Record file count, approximate size, source path, and intended archive path.
- Review the manifest for temporary files, private data, and missing metadata.
- Create the archive only after the plan looks correct.
- Pair the archive with a checksum manifest before transfer or publication.

## Safety Notes

This skill is `medium` risk because archive creation can write large files and
increase filesystem load. The example defaults to planning mode and only
creates a tar.gz file when `CREATE_ARCHIVE=1` is set. Run on user-owned data,
avoid broad home or project roots, and archive from a filesystem appropriate
for large sequential reads.

## Success Criteria

- The archive manifest contains the intended files and excludes obvious
  scratch, temporary, cache, and private files.
- The archive summary records source path, file count, size estimate, and
  archive path.
- The tar.gz archive is created only after explicit opt-in.
- A checksum manifest is generated for the archive before transfer or handoff.
