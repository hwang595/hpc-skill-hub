# Contributing

Thanks for helping build HPC Skill Hub.

## What Makes A Good Skill

A skill should be:

- Practical: it solves a real HPC task.
- Portable: site-specific assumptions are declared instead of hidden.
- Reviewable: commands and risks are visible.
- Testable: examples can be statically validated and, where possible, dry-run.
- Teachable: the README explains when and why to use the skill.

## Add A Skill

1. Create a directory under `skills/` using a lowercase kebab-case id.
2. Add `skill.json`.
3. Add `README.md`.
4. Add at least one file under `examples/`.
5. Run:

   ```bash
   python3 tools/validate_skills.py --skill your-skill-id
   python3 tools/audit_safety.py
   make check
   ```

6. Open a pull request with a short explanation of the target users, expected
   cluster environment, and known risks.

You can generate the starter files with:

```bash
python3 tools/hpc_skill.py scaffold skill your-skill-id --category education --tool bash
```

## Add A Site Adapter

Site adapters live under `site-adapters/<adapter-id>/` and describe public,
non-sensitive local policy for one HPC site or training environment.

1. Copy `site-adapters/example-campus-cluster/`.
2. Replace example values with public site information or placeholders.
3. Keep private hostnames, allocation names, users, and internal security
   details out of the repository.
4. Run:

   ```bash
   python3 tools/validate_skills.py
   python3 tools/audit_safety.py
   make check
   ```

Adapters should clarify local usage without changing the portable meaning of a
core skill.

You can generate the starter files with:

```bash
python3 tools/hpc_skill.py scaffold site-adapter your-site-id --name "Your Site"
```

## Skill Risk Levels

- `low`: Read-only guidance, templates, or diagnostics.
- `medium`: Runs jobs, allocates compute time, or writes user-owned files.
- `high`: Changes shared environments, admin state, accounting, quotas, or node
  availability.

High-risk skills require explicit maintainer review before they can be marked
as reviewed or field-tested.

## Style

- Prefer POSIX shell examples unless a scheduler or tool requires otherwise.
- Use placeholders such as `<account>`, `<partition>`, and `<project>` for
  site-specific values.
- Avoid embedding private hostnames, usernames, emails, tokens, or project IDs.
- Keep scripts conservative: short wall times, modest memory, and clear output.
