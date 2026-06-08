# Scratch Storage Management

Use this skill when a user needs to understand storage usage before launching a
job, staging a dataset, or cleaning a workflow directory.

## Example

```bash
bash examples/storage-inventory.sh <scratch-or-project-path>
```

If no path is provided, the script inspects the current directory.

## What To Look For

- A filesystem that is close to full.
- A user directory with a few unexpectedly large top-level entries.
- Large temporary files left by previous jobs.
- Workflow work directories that can be regenerated.
- Output that should be archived or moved to project storage.

## Cleanup Planning

The example is read-only. Use its output to write a human-reviewed cleanup plan:

- Keep original input data and provenance files.
- Archive or transfer valuable results before removing local copies.
- Regenerate disposable cache and work directories when possible.
- Check site retention policy for scratch files.
- Avoid changing shared project directories without group agreement.

## Safety Notes

This skill does not remove files. The report may reveal private paths, dataset
names, or project names, so review output before sharing it in public issues or
support tickets.
