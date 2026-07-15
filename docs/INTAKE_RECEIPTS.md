# Community Intake Receipts

The v0.6 P2 receipt workflow turns a fresh quarantined intake observation into
a portable, deterministic evidence record. It never skips P1: every create or
verify operation stages and scans the contribution again without executing or
returning its instruction content.

## Workflow

Create a draft receipt outside the contribution:

```bash
hpc-skill receipt create ./community-skill.zip \
  --output ./review/community-skill.receipt.json \
  --json
```

A benign scanner pass produces `review-required`, not `accepted`. The draft
contains exact `bindings` for the source, bounded inventory, effective policy,
findings, accepted exceptions, intake evidence, and candidate context
manifest. The local source filename is normalized to `contribution`, so the
receipt contains no temporary path and remains stable when identical source
bytes are reviewed under a different local filename.

After inspecting the P1 report and every finding, create a decision JSON
outside the contribution. Copy the draft's `bindings` object exactly:

```json
{
  "$schema": "https://hpc-skill-hub.org/schemas/community-skill-intake-decision.schema.json",
  "schema_version": "0.1.0",
  "reviewer_id": "maintainer-a",
  "reviewer_role": "maintainer-intake",
  "reviewed_on": "2026-07-14",
  "disposition": "accept",
  "bindings": {
    "source_digest": "<sha256>",
    "inventory_digest": "<sha256>",
    "policy_digest": "<sha256-or-null>",
    "findings_digest": "<sha256>",
    "exceptions_digest": "<sha256>",
    "context_digest": "<sha256>",
    "intake_digest": "<sha256>",
    "review_basis_digest": "<sha256>"
  },
  "acknowledged_finding_digests": [],
  "acknowledged_exception_ids": [],
  "rationale": "Reviewed the exact bounded intake evidence."
}
```

An `accept` decision must list every active finding digest and every applied
policy exception id. Unknown, missing, duplicated, or unsorted acknowledgements
fail closed. `request-changes` keeps the receipt at `review-required`; `reject`
produces `blocked`. A P1 `blocked` report can never be accepted.

Create and verify the accepted receipt:

```bash
hpc-skill receipt create ./community-skill.zip \
  --decision ./review/community-skill.decision.json \
  --output ./review/community-skill.accepted.json \
  --json

hpc-skill receipt verify ./review/community-skill.accepted.json \
  --source ./community-skill.zip \
  --json
```

When an external policy was used, pass the same external path to both commands.
The contribution, decision, receipt, and policy are separate trust objects; a
directory contribution may not contain its own decision, receipt, or policy.

## Receipt Contract

Receipts follow
[`community-skill-intake-receipt.schema.json`](../schemas/community-skill-intake-receipt.schema.json),
and decisions follow
[`community-skill-intake-decision.schema.json`](../schemas/community-skill-intake-decision.schema.json).
The receipt records:

- the complete normalized P1 report, including intake and scanner versions;
- source, inventory, policy, finding, exception, and review-basis digests;
- redacted accepted-exception provenance already bound to finding digests;
- the exact maintainer intake disposition and acknowledgements;
- a candidate context-manifest digest and, only for `accepted`, the identical
  accepted digest with `context_loading_allowed: true`;
- a top-level digest over the full receipt excluding only that digest field.

The context digest binds canonical path, byte-count, and SHA-256 records for
every accepted UTF-8 file. P4 must reconstruct content under the same bounds and
verify every file before returning it to an agent; P2 does not retain a
quarantine directory or return file content.

## Verification And Exit Codes

Verification first validates the closed receipt contract and its self-digest,
then re-runs P1 with the recorded limits. It rejects stale inventory, source,
policy, exception, finding, scanner, or intake evidence. Recorded limits may be
equal to or stricter than the P1 defaults; a receipt cannot widen the accepted
boundary.

| Result | Meaning | CLI exit |
| --- | --- | ---: |
| `accepted` | Exact maintainer intake decision and fresh evidence bindings pass. | 0 |
| `review-required` | Evidence is valid, but exact maintainer acceptance is absent. | 0 |
| `blocked` | P1 blocked the source or the maintainer rejected it. | 1 |
| Error or stale receipt | Input, contract, digest, policy, or fresh-intake verification failed. | 2 |

## Evidence Boundary

Canonical digests detect drift; they are not digital signatures and do not
establish reviewer identity. `maintainer-intake` means only that the named
public-safe reviewer disposition covers the exact static evidence. Every P2
receipt keeps `domain_review_complete` and `independent_review_complete` false.
It does not prove domain correctness, operational usefulness, adoption,
maturity, execution safety, or agent performance. P3 binds those separate
review and adoption decisions without rewriting P2 evidence. See
[Community Review And Adoption Evidence](COMMUNITY_EVIDENCE.md).
