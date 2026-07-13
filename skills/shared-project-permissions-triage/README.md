# Shared Project Permissions Triage

Use this skill when a user or collaborator can list, read, write, stage, or
transfer files in one shared HPC path but fails with `Permission denied`,
unexpected group ownership, missing ACL access, or inherited permission issues
in another path.

The skill is designed for project, scratch, campaign, lab, and course
directories where several users or jobs need predictable access.

## Prerequisites

- Obtain the narrowest affected path and optional log from an authorized user.
  The path may reveal project, course, campaign, or dataset identifiers.
- Run as the identity experiencing the failure when possible; shell access tests
  describe only the current identity and do not impersonate collaborators.
- Treat group databases, ACL support, mount options, and support-owned parent
  directories as site policy. Do not infer a repair from one mode string.
- The script performs no test write. A writable result does not prove quota,
  mount state, or application identity will allow a later job write.

## Workflow

```bash
bash examples/permission-triage.sh <path> [log-file]
```

If no path is provided, the script inspects the current directory. If a log file
is provided, it searches for permission, ownership, ACL, and read-only
filesystem clues.

Review saved public-safe path, ACL, and log evidence offline:

```bash
python3 examples/review-permission-evidence.py \
  --namei <namei.txt> --acl <getfacl.txt> --log <application.log>
```

## Common Signals

- `Permission denied` while a user appears to be in the expected project group.
- A job can create files, but collaborators cannot read or update them later.
- New files inherit the user's primary group instead of the project group.
- A parent directory lacks execute/search permission, so the target path cannot
  be traversed even if the final directory looks correct.
- A POSIX ACL entry exists, but the ACL mask removes the effective permission.
- Files staged by transfer tools preserve restrictive source modes.

## What The Script Collects

- Current user, numeric IDs, group names, and shell `umask`.
- Target path and parent directory metadata from `ls -ld` and `stat`.
- Read, write, and execute tests using shell `test`.
- Path traversal evidence from `namei -l` when available.
- ACL evidence from `getfacl -p` when available.
- Filesystem mount/capacity context from `df -h` when available.
- Recent permission-related log lines when a log file is provided.

## What To Review

Use `examples/support-review-checklist.md` to decide whether the likely cause is
group membership, parent traversal, setgid/default ACL inheritance, ACL mask,
sticky-bit behavior, restrictive umask, transfer mode preservation, or a site
policy that requires support action.

## Resource And Cost

The live and offline examples are read-only and bounded to one selected path,
its parent metadata, optional traversal/ACL output, and an optional log. They do
not recursively walk a project tree. Broad metadata scans on shared filesystems
can create load and expose unrelated data, so keep follow-up inspection narrow.

## Cleanup

No cleanup is required because the examples create no files and change no
permissions, ownership, ACLs, groups, or data. Any repair requires separate
owner/support approval plus validation and rollback planning.

## Site Adaptation

Group refresh behavior, setgid/default ACL conventions, ACL support, transfer
mode policy, and support-owned directory boundaries vary by site. Redact raw
paths, users, groups, ACLs, project ids, and log excerpts before sharing.

## Safety Notes

This skill is read-only. It does not run `chmod`, `chgrp`, `chown`, `setfacl`,
group-management commands, file creation probes, or cleanup commands. Do not
post raw paths, group names, usernames, ACLs, project IDs, or log excerpts in
public issues without redaction.
