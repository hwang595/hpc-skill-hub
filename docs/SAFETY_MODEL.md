# Safety Model

HPC Skill Hub contains examples that users may adapt for shared compute
systems. The project uses both human review and lightweight automation to reduce
operational risk.

## Risk Labels

- `low`: Read-only diagnostics, templates, or local reports.
- `medium`: Jobs, data movement, user-owned writes, or resource-consuming
  builds.
- `high`: Shared software stacks, admin state, accounting, quotas, node state,
  or security-sensitive behavior.

## Automated Safety Audit

`tools/audit_safety.py` scans repository text files for obvious hazards:

- Private key blocks.
- Token-shaped secrets.
- AWS key-shaped secrets.
- Recursive remove against filesystem root.
- `chmod 777`.
- `sudo` in user-facing examples.
- Local build artifacts that should stay out of the repository.

Run:

```bash
python3 tools/audit_safety.py
```

The audit is deliberately conservative. It is not a full static analyzer and it
does not replace maintainer review.

## Review Expectations

Reviewers should still check:

- Whether resource requests are modest for smoke tests.
- Whether data-transfer examples can overwrite or publish data.
- Whether site adapters contain only public, non-sensitive policy.
- Whether medium and high-risk entries explain cost and side effects.
- Whether commands are safe for login nodes and shared filesystems.
