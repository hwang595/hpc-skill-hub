# Community Skill Security

Community-contributed skills are untrusted input until they pass automated
checks and human review. A skill can contain executable examples, agent-facing
instructions, dependency installation steps, network actions, or references to
ambient credentials. Repository validation alone does not establish trust.

## Security Scanner

The installable scanner accepts an HPC Skill Hub package, a Codex or Claude
Code `SKILL.md` directory, a parent directory containing multiple skills, or a
single file:

```bash
hpc-skill security ./path/to/skill
python3 tools/scan_skill_security.py skills/<skill-id>
```

JSON and SARIF output are available for portals, CI, and review tooling:

```bash
hpc-skill security ./path/to/skill --format json
hpc-skill security ./path/to/skill --format sarif
```

The default policy fails on `high` and `critical` findings. Use
`--fail-on medium` for a stricter review gate or `--fail-on none` to collect a
report without changing the exit status.

## Verdicts

| Verdict | Meaning | Expected action |
| --- | --- | --- |
| `pass` | No rule matched. | Continue normal validation and human review. |
| `review` | Findings exist below the failure threshold. | Review the exact file, behavior, risk declaration, guard, and remediation. |
| `block` | At least one finding meets the failure threshold. | Do not install, load into an agent context, or execute the skill until resolved. |

Reports follow
[`skill-security-report.schema.json`](../schemas/skill-security-report.schema.json)
and include stable rule ids, severity, category, file/line location, remediation,
skill id when available, and a deterministic finding fingerprint. Reports do
not copy matched secret text into output.

## Initial Rule Coverage

The v0.3 scanner checks for:

- Prompt-injection language that overrides higher-priority instructions or
  conceals behavior from users and reviewers.
- Download-to-shell and encoded-payload execution chains.
- Reverse-shell patterns and SSH persistence.
- Writes to shell startup profiles.
- Reads of common ambient credential files.
- Embedded private keys and common token-shaped secrets.
- Privileged execution and world-writable permissions.
- Recursive deletion, dynamic shell evaluation, and package installation that
  require explicit review.
- Symlinks, executable binary payloads, oversized files, invalid manifests, and
  manifest paths that escape the skill package.
- Manifest `risk_level` values that understate detected behavior.

Rule matches are evidence for review, not proof of malicious intent. For
example, marker-guarded cleanup can be a legitimate `medium` finding.

## Agent Adoption Protocol

Coding agents should apply this order to community skills:

1. Scan the package before loading untrusted `SKILL.md`, README, or examples
   into the working context.
2. Stop on `block` and show the user the rule ids, locations, and remediation.
3. Treat `review` as an explicit decision point; inspect guards, declared risk,
   network/resource impact, and provenance.
4. Run registry/schema validation after security scanning.
5. Present commands for review and require explicit user intent before any
   execution, installation, job submission, transfer, or shared-state change.

## Trust Boundary And Limitations

The scanner is static, local, deterministic, and standard-library-only. It does
not execute skill content or use the network. It cannot prove that a script is
safe, detect every obfuscated payload, verify a remote artifact after download,
or replace domain review and sandboxing. Future v0.3 work should add provenance,
signed release metadata, archive extraction limits, and stronger policy packs
without turning static findings into automatic maturity promotion.
