# Community Skill Security

Community-contributed skills are untrusted input until they pass automated
checks and human review. A skill can contain executable examples, agent-facing
instructions, dependency installation steps, network actions, or references to
ambient credentials. Repository validation alone does not establish trust.

Use `hpc-skill intake` as the first boundary for an untrusted directory or
archive. It inventories and stages bounded UTF-8 source before invoking this
scanner and returns no instruction content. See
[Quarantined Community Intake](COMMUNITY_INTAKE.md). Use `hpc-skill security`
directly only when the source is already expanded inside a reviewed boundary.

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

The packaged `community-default@0.1.0` policy fails on active `high` and
`critical` findings. Use `--fail-on medium` for a stricter review gate or
`--fail-on none` for report-only process behavior. Report-only mode does not
erase a policy `block` verdict. See [Trust Policy Packs](TRUST_POLICY_PACKS.md)
for external policy and reviewed-exception rules.

## Verdicts

| Verdict | Meaning | Expected action |
| --- | --- | --- |
| `pass` | No rule matched. | Continue normal validation and human review. |
| `pass-with-exceptions` | Every finding is covered by an exact, unexpired reviewed exception. | Preserve the receipt and re-review before expiration or any source change. |
| `review` | Findings exist below the failure threshold. | Review the exact file, behavior, risk declaration, guard, and remediation. |
| `block` | At least one finding meets the failure threshold. | Do not install, load into an agent context, or execute the skill until resolved. |

Reports follow
[`skill-security-report.schema.json`](../schemas/skill-security-report.schema.json)
and include stable rule ids, base and effective severity, category, file/line
location, remediation, skill id when available, a deterministic fingerprint,
and a source-bound finding digest. Policy, target, and rule-catalog digests form
a provenance receipt. Reports do not copy matched secret, reviewer, or exception
justification text into output.

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

1. Run `hpc-skill intake` before loading untrusted `SKILL.md`, README, or
   examples into the working context.
2. Stop on `blocked` and show boundary or scanner rule ids and remediation.
3. Hand `review-required` and `ready-for-review` to a human without loading the
   package into agent context; P1 never records acceptance.
4. After a later acceptance workflow, run registry/schema validation.
5. Present commands for review and require explicit user intent before any
   execution, installation, job submission, transfer, or shared-state change.

## Trust Boundary And Limitations

The scanner is static, local, deterministic, and standard-library-only. It does
not execute skill content or use the network. It cannot prove that a script is
safe, detect every obfuscated payload, verify a remote artifact after download,
or replace domain review and sandboxing. Tagged package builds now add signed
GitHub artifact provenance for release manifests and distributions. Versioned
policy packs and reports detect policy/content drift but are not signatures.
The quarantined intake layer adds archive and resource limits, but neither a
clean intake nor a reviewed exception establishes correctness, adoption,
maturity, or execution authorization.
