# Node Local Scratch Staging

Use this skill when a job should use node-local temporary storage for fast
intermediate work, but final outputs and restart files must return to durable
project or scratch storage.

Node-local directories are often purged automatically when a job exits. Treat
them as temporary acceleration space, not as a place to keep results.

## Example

Review the manifest and placeholders, then submit a tiny test first:

```bash
sbatch examples/node-local-scratch.sbatch
```

Run the example locally for script review:

```bash
NODE_LOCAL_BASE="$(pwd)/local-node-tmp" \
OUTPUT_DIR="$(pwd)/node-local-output" \
bash examples/node-local-scratch.sbatch
```

Enable cleanup only after confirming stage-out worked:

```bash
CLEANUP_NODE_LOCAL=1 sbatch examples/node-local-scratch.sbatch
```

## Pattern

- Choose a node-local base from `NODE_LOCAL_BASE`, `SLURM_TMPDIR`, `TMPDIR`, or
  a site-approved path.
- Record capacity and environment evidence before copying data.
- Create a private job-local directory with `mktemp -d`.
- Stage inputs into `work/inputs`.
- Run the workload from `work`.
- Stage selected outputs and the report back to durable storage.
- Clean only the marked directory created by this job.

## Safety Notes

This skill is `medium` risk because it copies data, writes outputs, and can
delete temporary directories. The cleanup path is guarded by a marker file, a
path-name check, and an explicit confirmation variable. Do not store the only
copy of a result on node-local scratch.

## Success Criteria

- Capacity and selected temporary directory are recorded.
- Stage-in logs list every expected input.
- Workload output is copied back to durable storage.
- Cleanup is skipped by default or deletes only the marked job-local directory.
- Restart files and final outputs are not left only on node-local storage.
