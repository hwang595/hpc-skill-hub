# Trust Policy Packs

HPC Skill Hub security policy is versioned separately from scanner code. The
scanner owns detection logic; a policy pack selects the complete known rule
catalog, sets an enforcement threshold, can raise rule severity, and can carry
reviewed exceptions for exact findings.

The repository and wheel ship
[`community-default@0.1.0`](../security/policies/community-default.json). Its
contract is defined by
[`skill-security-policy.schema.json`](../schemas/skill-security-policy.schema.json).

## Default Policy

The default pack:

- explicitly enables all 26 scanner rules;
- blocks active `high` and `critical` findings;
- permits exception machinery only for `low` and `medium` findings;
- contains no accepted exceptions; and
- is copied byte-for-byte into the installed wheel.

The policy pack does not contain regular expressions or executable hooks.
Detection remains in the scanner so a package cannot replace a rule's meaning.

Run the packaged baseline:

```bash
hpc-skill security ./community-skill --json
```

Use a stricter invocation threshold:

```bash
hpc-skill security ./community-skill --fail-on medium --json
```

`--fail-on none` is report-only mode. It returns a successful process status,
but the report still uses the policy threshold and keeps a `block` verdict.

## External Policies

An external policy is an operator or CI input, not package content:

```bash
hpc-skill security ./community-skill \
  --policy /trusted/review/site-reviewed.json \
  --json
```

A custom pack must be a complete policy with
`extends: community-default@0.1.0`. The loader fails closed unless it:

- names every scanner rule exactly once and keeps every rule enabled;
- uses the same or a stricter `fail_on` threshold;
- keeps the same or a lower `exception_max_severity` ceiling;
- keeps every rule's default severity or raises it; and
- contains only valid, unexpired reviewed exceptions.

The policy path must be outside the scan target. This prevents a contributed
skill from shipping a policy that grants itself exceptions. Policy files are
trusted review inputs and should be code-reviewed and access-controlled like CI
configuration.

## Severity Overrides

Overrides are monotonic. For example, a site can promote dynamic shell
evaluation from `medium` to `high`:

```json
{
  "rule_id": "execution.dynamic-eval",
  "severity": "high"
}
```

Lowering severity is rejected before package content is scanned.

## Reviewed Exceptions

An accepted exception binds all of these values:

- exception id and accepted status;
- rule id;
- skill id, including `null` for a standalone package;
- normalized package-relative path;
- `finding_digest`, which binds rule, path, line, and source-file SHA-256;
- reviewer, review date, expiration date, and justification.

Obtain the `finding_digest` from an initial JSON report, review the exact source,
then add the exception to a trusted external pack. Any source or line change
breaks the match. Expired exceptions make policy loading fail closed. The
default ceiling prevents exceptions for `high` or `critical` findings.

Reports retain accepted findings with `disposition: accepted` and the verdict
`pass-with-exceptions`. JSON, SARIF, and context receipts expose only the
exception id, expiration, and a digest of the review record. Reviewer and
justification text are not copied into scan reports or MCP context.

## Provenance Receipt

Security report schema `0.2.0` records:

- scanner name and version;
- policy id, version, source and effective SHA-256;
- enabled-rule, override, and exception counts;
- the effective enforcement and process-exit thresholds;
- target-content and rule-catalog SHA-256 values;
- applied exception ids; and
- source-bound finding digests and dispositions.

`registry/skill-context.json` schema `0.2.0` carries the same policy and scan
receipt for every packaged skill. The runtime verifier rejects the old minimal
policy record, blocked contexts, stale digests, or a policy receipt that does
not match its scan provenance.

These digests detect drift and bind review inputs. They are not signatures,
identity proofs, or substitutes for release attestations and human review.

## MCP Boundary

The MCP server exposes a fixed tool-name and argument allowlist. Server startup,
the doctor, and official SDK protocol tests compare callable signatures and
generated input schemas with that allowlist. Read-only annotations remain
client hints; the registered server surface is the enforcement boundary.

The server accepts only public registry site adapters. It has no private-policy
argument and does not use MCP logging. Responses do not echo raw search or
unknown-id arguments, and the canonical client contract records that sensitive
arguments are not logged.
