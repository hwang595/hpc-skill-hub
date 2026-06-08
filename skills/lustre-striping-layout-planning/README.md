# Lustre Striping Layout Planning

Use this skill when a workload writes to a Lustre filesystem and you need
evidence before changing stripe count, stripe size, OST pool, or progressive
file layout settings.

The example script is read-only. It writes current layout evidence and a
reviewable plan, but it does not run `lfs setstripe`, `lfs migrate`, or any
other command that changes file layout.

## Example

Collect evidence for a target path:

```bash
bash examples/lustre-layout-report.sh /path/on/lustre lustre-layout-report
```

Then review `lustre-layout-report/stripe-plan.md` with site documentation,
storage support, or a domain reviewer before applying any layout changes.

## What It Collects

- `lfs getstripe` output for the target path.
- Directory default layout through `lfs getstripe -d` when applicable.
- `lfs df -h` evidence for Lustre OST and MDT capacity when available.
- Portable `df -h`, `df -i`, and `stat` output.
- A bounded sample of large files in the target directory when `find` is
  available.
- A review-only plan with placeholder `lfs setstripe` examples.

## Safety Notes

This skill is `medium` risk because applying a stripe layout can change how
new files use shared OSTs, and migrating existing files can create significant
I/O load. The provided script only inspects state and creates a plan.

Do not change striping on broad project directories, shared workflow roots, or
existing production files without site approval. Stripe settings usually affect
new files created after the setting is applied; existing files need a copy or
migration workflow if their layout must change.

## Success Criteria

- The current file or directory layout is captured before any change.
- The expected I/O pattern is written down: many small files, per-rank files,
  large shared checkpoints, staged analysis reads, or mixed output.
- The plan avoids hard-coding OST indices unless the site recommends it.
- Wide striping is justified by file size, concurrency, Darshan evidence,
  application documentation, or a small approved benchmark.
- Any `setstripe` or `migrate` action has a rollback and cleanup plan.

## Review Prompts

- Is the workload bottlenecked on I/O layout, metadata, small files, or
  application-level buffering?
- Should the application write fewer larger files before changing Lustre
  striping?
- Does the site provide progressive file layout defaults that should be left
  in place?
- Should changes apply to a new empty output directory instead of an existing
  shared directory?
