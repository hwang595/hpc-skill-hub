# Globus Transfer Dataset

Use this skill for reliable movement of large datasets between storage systems,
HPC centers, instruments, or cloud endpoints.

## Example

```bash
bash examples/transfer-and-watch.sh <source-collection> /source/path <dest-collection> /dest/path
```

## Safety Notes

This skill is `medium` risk because it moves data and may overwrite destination
files depending on flags. Start with a small test path and confirm collection
permissions before transferring production data.

## Success Criteria

- The Globus task reaches `SUCCEEDED`.
- The destination path contains the expected files.
- Transfer logs and task id are saved with the analysis record.
