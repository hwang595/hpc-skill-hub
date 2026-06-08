# Security Policy

HPC Skill Hub contains examples that may run on shared computing systems.
Security review is part of project quality, not an afterthought.

## Report A Concern

Please open a private security advisory if available on the hosted repository,
or contact the maintainers listed in the repository metadata.

Do not open a public issue for secrets, privilege escalation concerns, unsafe
admin actions, or vulnerabilities in generated scripts.

## Security Expectations For Skills

- No embedded credentials, tokens, SSH keys, host-specific secrets, or private
  dataset paths.
- Commands that allocate compute time must state the expected resource impact.
- Commands that delete, overwrite, publish, transfer, or chmod data must be
  marked at least `medium` risk and explained in the README.
- Admin or facility operations must be marked `high` risk unless they are
  strictly read-only.
- Skills should prefer dry-run, read-only, or template generation paths by
  default.

## Automated Safety Audit

Run the lightweight audit before opening a pull request:

```bash
python3 tools/audit_safety.py
```

The audit checks for obvious secret material and dangerous shell patterns. It is
not a substitute for maintainer review. See [docs/SAFETY_MODEL.md](docs/SAFETY_MODEL.md).

## Supported Versions

During the seed stage, only the `main` branch is supported. Versioned releases
will be added once the manifest format stabilizes.
