# Module Tree Health Check

Use this skill when support teams or software-stack maintainers need a
read-only snapshot of the visible module tree before diagnosing broken module
paths, missing modulefiles, stale compiler/MPI stacks, or confusing user
reports.

This skill is different from `module-environment-debug`: it focuses on the
health and visibility of the module tree itself, while `module-environment-debug`
focuses on one user's currently loaded environment and optional executable.

## Assumptions

- The site uses Lmod or Environment Modules.
- `module` is available in the current shell, usually as a shell function.
- Optional commands such as `module spider` may be Lmod-specific and may not
  work with every module implementation.
- Module names, paths, and metadata may expose site policy or internal software
  layout. Review before sharing outside the support team.

## Example

Collect a general module tree report:

```bash
bash examples/module-tree-health.sh
```

Inspect metadata for a specific module or pattern:

```bash
bash examples/module-tree-health.sh gcc
```

Write to a named output directory:

```bash
bash examples/module-tree-health.sh openmpi module-tree-report
```

## Review The Output

The script creates files such as:

- `summary.md`: report scope and review reminders.
- `modulepath.txt`: current `MODULEPATH` entries.
- `module-avail.txt`: visible module names from `module avail`.
- `module-list.txt`: currently loaded modules.
- `module-spider.txt`: optional Lmod spider output for a module pattern.
- `module-whatis.txt`: optional module metadata for a module pattern.
- `tool-paths.txt`: common compiler, MPI, Python, and package-manager command
  paths visible in the current shell.

Look for:

- Empty or surprising `MODULEPATH` entries.
- Missing compiler, MPI, CUDA/ROCm, Python, or domain application modules.
- Module names that appear in documentation but not in `module avail`.
- Multiple module trees that expose incompatible compiler or MPI families.
- Tool paths that point outside the expected module tree.

## Success Criteria

- The report directory exists.
- Missing optional module subcommands are recorded instead of hiding failures.
- No `module load`, `module unload`, `module purge`, or modulefile edits occur.
- The report gives a maintainer enough evidence to reproduce or route a module
  visibility issue.

## Safety Notes

This skill is low risk because it reads environment and module metadata only.
It can still reveal private install paths, module naming conventions, licensed
software names, or internal software-stack policy. Redact raw reports before
posting them publicly.
