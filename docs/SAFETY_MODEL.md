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
- Jupyter token-shaped URLs.
- Private network addresses.
- SSH commands or HPC service URLs with real-looking hostnames.
- Slurm account, WCKEY, or reservation values that are not placeholders.
- Private-looking HPC storage paths such as non-placeholder scratch, project,
  GPFS, Lustre, NFS, or home paths.
- Recursive remove against filesystem root.
- `chmod 777`.
- `sudo` in user-facing examples.
- Local build artifacts that should stay out of the repository.

Run:

```bash
python3 tools/audit_safety.py
```

The audit allows public-safe placeholders such as `<account>`, `<partition>`,
`<login-node>`, `/project/<project>`, and `/scratch/<user>`, plus localhost and
example domains for runnable templates. The audit is deliberately conservative.
It is not a full static analyzer and it does not replace maintainer review.

## Community Skill Security Scan

`hpc-skill security` treats a contributed skill package as untrusted input and
adds agent-oriented checks for prompt injection, concealed behavior,
download-to-shell execution, persistence, ambient credential access, binary or
symlink payloads, and understated manifest risk.

Run the repository gate with:

```bash
python3 tools/scan_skill_security.py skills --fail-on high
```

The safety audit protects the public repository as a whole. The security
scanner evaluates the trust boundary of each skill package and emits text,
JSON, or SARIF findings. See [Community Skill Security](SKILL_SECURITY.md) for
the threat model, verdicts, agent adoption protocol, and limitations.

## Review Expectations

Reviewers should still check:

- Whether resource requests are modest for smoke tests.
- Whether data-transfer examples can overwrite or publish data.
- Whether site adapters contain only public, non-sensitive policy.
- Whether medium and high-risk entries explain cost and side effects.
- Whether commands are safe for login nodes and shared filesystems.
