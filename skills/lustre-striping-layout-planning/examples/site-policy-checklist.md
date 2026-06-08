# Lustre Striping Site Policy Checklist

Review these items before applying any `lfs setstripe`, progressive file
layout, OST pool, or migration command.

## Site Defaults

- Confirm the site default stripe count, stripe size, and any progressive file
  layout policy.
- Confirm whether users may set layouts on files, directories, or both.
- Confirm allowed stripe-count ranges, stripe-size values, and OST pools.
- Confirm whether explicit OST indices are allowed or discouraged.

## Target Scope

- Prefer a new empty output directory over an existing project or workflow root.
- Confirm the target path is on Lustre and not on home, NFS, object storage, or
  another backend.
- Confirm whether the setting should apply only to a new run, a single file, or
  a narrow output subtree.
- Record how the layout will be reset or retired after the workflow changes.

## Existing Data

- Do not assume `setstripe` changes existing files.
- Treat `lfs migrate`, recopying data, or rewriting checkpoints as separate
  operations that can create substantial I/O load.
- Confirm no active jobs are writing to files being migrated or recopied.

## Evidence

- Capture current `lfs getstripe` and `lfs df` output before changes.
- Use Darshan logs, application documentation, or an approved tiny benchmark to
  justify non-default layouts.
- Record expected file size, writer count, reader count, and restart behavior.

## Sharing

- Redact project names, private paths, hostnames, usernames, and sensitive file
  names before sharing reports publicly.
