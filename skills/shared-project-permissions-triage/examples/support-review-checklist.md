# Shared Permission Review Checklist

Use this checklist after collecting `permission-triage.sh` output. Keep private
usernames, groups, project IDs, and paths out of public issues.

## Identity And Group Membership

- Confirm the user is in the intended project group in both numeric and named
  `id` output.
- If group membership was recently changed, ask whether the user started a new
  login session after the change.
- Check whether the job ran under the same account, supplementary groups, and
  project context as the interactive test.

## Path Traversal

- Review every parent directory from `namei -l`; users need execute/search
  permission on each parent to reach the target.
- If the target path is a symlink, inspect the resolved path and not only the
  link's directory.
- Check for restrictive permissions on a higher-level project, lab, campaign, or
  scratch parent directory.

## Ownership And Inheritance

- Confirm the owning group on the directory matches the collaboration group.
- For shared writable directories, check whether setgid inheritance is expected
  so new files keep the project group.
- Check whether default ACLs are expected on new files and subdirectories.
- Review whether the user's `umask` is too restrictive for collaborative write
  or read access.

## ACL Review

- If `getfacl` output exists, compare the requested user or group entry with the
  effective rights after the ACL mask.
- Check whether default ACL entries exist on directories where future files must
  inherit access.
- Treat ACL changes as a site or project-owner action; do not recommend public
  one-size-fits-all `setfacl` commands.

## Workflow And Transfer Clues

- Determine whether `rsync`, archive extraction, Globus, or another transfer
  tool preserved source modes or ownership unexpectedly.
- Check whether the failure is actually capacity, quota, inode, or read-only
  filesystem state instead of permissions.
- Compare interactive access with access from batch jobs, containers, and
  workflow engines, because each may use different paths or bind mounts.

## Escalation Packet

- Redacted target path and parent path.
- Redacted `id`, `ls -ld`, `stat`, `namei -l`, and `getfacl` output.
- One failing command and the exact redacted error line.
- Whether the desired access is read-only, group write, execute/search, or
  inherited access for newly created files.
