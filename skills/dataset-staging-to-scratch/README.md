# Dataset Staging To Scratch

Use this skill when a job should read inputs from scratch or node-local storage
instead of repeatedly accessing slower shared project storage.

## Example

Replace `<account>` and `<partition>`, review paths, then submit:

```bash
sbatch examples/stage-to-scratch.sbatch
```

Use a tiny manifest first. Scale only after checking scratch quotas and site
retention policy.

## Pattern

- Declare input files or directories in a manifest.
- Create a job-specific scratch directory.
- Copy inputs into scratch with `rsync`.
- Run the workload inside the scratch directory.
- Copy selected outputs back to durable storage.
- Keep logs with source, scratch, and destination paths.

## Safety Notes

This skill is `medium` risk because it submits jobs, copies data, and writes to
scratch and output locations. Avoid staging irreplaceable originals without
checksums, and do not assume scratch is backed up.

## Success Criteria

- Stage-in logs show every expected input path.
- The workload runs from the scratch directory.
- Selected outputs are copied back to durable storage.
- Scratch cleanup follows site policy and does not remove shared source data.
