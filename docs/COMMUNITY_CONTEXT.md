# Trusted Community Context

P4 converts one accepted and independently reviewed community contribution into
a portable, read-only context bundle. It never reads instruction content from
the original source after review. Instead, it reruns the P1 quarantine path,
reads the bounded temporary snapshot, and verifies every file against the P2
`accepted_context.accepted_digest` before cleanup.

## Exposure Gate

Content is buildable only when all of these conditions hold:

1. The P2 receipt is `accepted` and fresh for the source, inventory, scanner,
   policy, findings, exceptions, and candidate context digest.
2. The P3 packet is exact-bound to that receipt, source, context, contribution,
   and review basis.
3. Independent reviews cover every declared domain.
4. Medium- and high-risk contributions have an approved safety review owned by
   someone other than the domain reviewer.
5. The aggregate status is `review-complete` and maturity promotion remains
   `not-authorized`.

Adoption evidence may be embedded when available, but it is not required to
read reviewed context and does not authorize maturity promotion.

## Build And Inspect

Keep receipts, reviews, policies, and outputs outside the submitted package:

```bash
hpc-skill community-context build \
  --source <contribution> \
  --receipt <accepted-receipt.json> \
  --packet <review-packet.json> \
  --review <domain-review.json> \
  --review <safety-review.json> \
  --adoption <optional-adoption-report.json> \
  --output <community-context.json>

hpc-skill community-context check <community-context.json> --json
hpc-skill community-context show <community-context.json>
```

`check` verifies the complete offline evidence graph and returns provenance,
evidence digests, and the file manifest without returning instruction content.
`show` is the explicit content-reading operation and renders source, policy,
receipt, review, risk, and maturity state before files.

The bundle embeds the accepted receipt, review packet, independent reviews,
optional adoption reports, aggregate status, exact UTF-8 files, and all binding
digests. Loading recomputes the receipt, packet, review aggregation, file
digests, accepted context digest, and enclosing bundle digest. SHA-256 detects
substitution and drift; it is not an identity signature and does not replace
release attestations or human review of reviewer identities and evidence URLs.

## MCP Consumption

Community content is disabled by default. An operator explicitly configures
one or more previously checked bundles:

```bash
hpc-skill-mcp --community-bundle <community-context.json>
```

The `list_community_contexts` tool returns provenance and manifests only. Full
content is available at
`hpc-skill://community/{contribution_id}/{version}`. MCP startup fails if any
configured bundle is stale, malformed, review-incomplete, duplicated, or
digest-inconsistent.

The MCP surface has no source path, receipt, policy, review, execution, job,
transfer, install, network, credential, or private site-policy argument. Skill
content remains instruction, not authorization: examples are never executed
automatically and operational actions still require explicit user intent.
