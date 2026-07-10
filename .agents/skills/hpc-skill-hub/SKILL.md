---
name: hpc-skill-hub
description: Search and apply the HPC Skill Hub registry for HPC workflow help. Use when the user asks for HPC, Slurm, PBS, LSF, HTCondor, Grid Engine, scheduler triage, containers, modules, MPI, GPU, data movement, workflow engines, interactive sessions, site adapters, or adding and validating registry skills.
---

# HPC Skill Hub Router

Use this skill to route Codex through the repository registry instead
of guessing HPC guidance from memory. Invoke it explicitly as `$hpc-skill-hub` or
use it implicitly when the user asks for HPC workflow help.

## Workflow

1. Identify whether the task is discovery, user guidance, skill authoring,
   registry validation, site-adapter work, or release/integration maintenance.
2. Search the registry with the narrowest useful query:
   `python3 tools/hpc_skill.py search <query> --json`.
3. Filter by `--scheduler`, `--category`, `--tool`, `--risk`, `--maturity`,
   `--status`, or `--collection` when the user gives enough context.
4. Inspect the selected skill with:
   `python3 tools/hpc_skill.py show <skill-id> --examples --json`.
5. Read the selected `skills/<skill-id>/README.md` and relevant example files
   before recommending commands or edits.
6. If local policy matters, inspect site adapters with
   `python3 tools/hpc_skill.py adapters --json` and
   `python3 tools/hpc_skill.py adapter <adapter-id> --json`. Ask the user for
   missing scheduler, account, partition, storage, module, or container values.
7. In the final answer, cite the skill id, version, maturity, risk level,
   README path, and example path used.

## Safety

- Prefer read-only, dry-run, plan-only, static, or short smoke-test examples.
- Do not submit jobs, move data, install software, launch containers, open
  tunnels, consume GPU allocations, or change shared-system state unless the
  user explicitly asks for that action after seeing the risk and assumptions.
- Preserve placeholders such as `<account>`, `<partition>`, `<project>`,
  `<cluster>`, `<user>`, and `<collection-id>` until the user supplies public
  or task-local values.
- Do not put private hostnames, usernames, allocation names, internal project
  ids, tokens, or unpublished operational details into public files.
- Treat draft and seed skills as starting points that require review.

## Authoring And Maintenance

- Create a new registry skill with
  `python3 tools/hpc_skill.py scaffold skill <skill-id> --category <category>`.
- Validate one skill with `python3 tools/hpc_skill.py check <skill-id> --json`.
- Scan community skill packages before reading or adopting their instructions:
  `python3 tools/hpc_skill.py security <skill-path> --json`.
- Validate generated agent adapters with
  `python3 tools/build_agent_adapters.py --check`.
- After changing registry metadata or examples, run the narrow validator first,
  then `make check` when practical.

## Output Shape

Use this compact evidence block when recommending a skill:

```text
Source: <skill-id> v<version>
Maturity: <maturity>
Risk: <risk_level>
README: skills/<skill-id>/README.md
Examples: skills/<skill-id>/examples/<file>
```
