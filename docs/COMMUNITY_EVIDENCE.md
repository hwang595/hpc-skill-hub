# Community Review And Adoption Evidence

The v0.6 P3 workflow turns an accepted P2 intake receipt into a deterministic
maintainer review packet, validates independent domain and safety decisions,
records public-safe adoption reports, and produces an issue-ready aggregate
status. It never loads contribution instructions or promotes registry maturity.

## Workflow

Start with the original contribution and a fresh P2 receipt whose status is
`accepted`. Keep every receipt, packet, review, report, and generated status
outside a directory contribution.

Create a packet and Markdown issue summary:

```bash
hpc-skill evidence packet ./review/community-skill.accepted.json \
  --source ./community-skill.zip \
  --id community-skill \
  --version 0.1.0 \
  --risk medium \
  --domain scheduler \
  --submitter contributor-a \
  --artifact-url https://example.org/releases/community-skill-0.1.0.zip \
  --output ./review/community-skill.packet.json \
  --summary-output ./review/community-skill.issue.md \
  --json
```

The command re-runs P1 and P2 verification before creating the packet. It
binds the exact receipt, source, inventory, accepted context, contribution
metadata, and review basis digests. It copies no README, `SKILL.md`, example,
or other instruction content into the packet or issue summary.

Independent reviewers author records that follow
[`community-skill-independent-review.schema.json`](../schemas/community-skill-independent-review.schema.json).
Copy the packet's contribution id and version plus the complete output of
`evidence_bindings(packet)` into the record. Each record must include:

- one public-safe review id and reviewer id;
- `scope: domain` with one declared contribution domain, or `scope: safety`
  with `domain: safety`;
- the exact review date, decision, conflict disclosure, public evidence URL,
  notes, and independence attestation;
- all six checklist booleans, all `true` for an `approved` decision;
- a canonical SHA-256 over the record excluding `review_digest`.

Attach the canonical self-digest without editing the draft in place:

```bash
hpc-skill evidence digest ./review/community-skill.domain-review.draft.json \
  --output ./review/community-skill.domain-review.json \
  --json
```

The command accepts only the independent-review and adoption-report schemas,
reads a bounded regular JSON file without following symlinks, and writes to a
different path. The digest detects later edits; it is not a reviewer signature
or identity proof.

Every declared contribution domain needs approved coverage before the domain
gate passes. Medium- and high-risk contributions also require an approved
safety review. Domain and safety owners must differ. Neither reviewer may be
the submitter or P2 intake decision maker.

Independent adopters author records that follow
[`community-skill-adoption-report.schema.json`](../schemas/community-skill-adoption-report.schema.json).
Reports bind the same immutable evidence and use structured, public-safe fields
for test scope, outcome, environment type, scheduler, optional public site
adapter, public documentation, observations, and follow-up URLs. Private site
details must be omitted. The adopter must differ from the submitter, intake
maintainer, and supplied independent reviewers.

Fresh-verify and aggregate the evidence:

```bash
hpc-skill evidence check ./review/community-skill.packet.json \
  --receipt ./review/community-skill.accepted.json \
  --source ./community-skill.zip \
  --review ./review/community-skill.domain-review.json \
  --review ./review/community-skill.safety-review.json \
  --adoption ./review/community-skill.adoption.json \
  --output ./review/community-skill.status.json \
  --summary-output ./review/community-skill.issue.md \
  --json
```

Pass the same external `--policy` used for P1 and P2 when applicable. The
standalone repository wrapper exposes the same interface:

```bash
python3 tools/community_review_evidence.py check ...
```

## Artifact Contracts

P3 publishes four strict JSON contracts:

| Artifact | Purpose |
| --- | --- |
| [`community-skill-review-packet.schema.json`](../schemas/community-skill-review-packet.schema.json) | Immutable maintainer routing packet generated only from fresh accepted P2 evidence. |
| [`community-skill-independent-review.schema.json`](../schemas/community-skill-independent-review.schema.json) | Exact-bound domain or safety decision with checklist, independence, and public evidence. |
| [`community-skill-adoption-report.schema.json`](../schemas/community-skill-adoption-report.schema.json) | Public-safe operational observation from an independent adopter. |
| [`community-skill-evidence-status.schema.json`](../schemas/community-skill-evidence-status.schema.json) | Deterministic aggregate with separate gates, owners, counts, domain coverage, and self-digest. |

Python validation adds constraints that JSON Schema alone cannot establish:
canonical digest recomputation, fresh source and receipt verification,
cross-object equality, chronological ordering, role separation, full declared
domain coverage, and status-summary consistency.

## Gates And Owners

| Gate | Owner | Passing evidence |
| --- | --- | --- |
| Intake acceptance | `maintainer-intake` | Fresh P2 `accepted` receipt. |
| Domain review | Independent domain reviewer or reviewers | At least one approved exact-bound review for every declared domain, with no changes-requested or rejected domain decision. |
| Safety review | Independent safety reviewer | Approved exact-bound safety review for medium or high risk; absent low-risk safety review is `not-required`. |
| Adoption evidence | Independent adopter | One or more valid public-safe reports; `recorded` describes presence, not success. |
| Maturity promotion | Registry maintainer in a separate lifecycle change | Never authorized by a P3 packet, review, report, or aggregate status. |

`review-complete` means only that the applicable P3 review gates pass. Adoption
reports keep `successful`, `partial`, and `blocked` outcomes visible; any valid
report makes the evidence gate `recorded`. Field-tested or maintained maturity
still requires the existing registry lifecycle evidence and a separately
reviewed maintainer change.

## Exit Codes

| Result | CLI exit |
| --- | ---: |
| Valid packet or valid status that is pending/review-complete | 0 |
| Valid aggregate with `changes-requested` or `rejected` review status | 1 |
| Invalid, stale, substituted, private, conflicting, or unreadable evidence | 2 |

## Evidence Boundary

Canonical digests detect drift; they are not signatures and do not prove the
human identity behind a public id. Public URLs are evidence pointers, not
network-fetched attestations. P3 performs no contribution execution, job
submission, data movement, package installation, agent context loading, or
registry mutation. Synthetic fixtures prove parser and policy behavior only;
they do not establish that a real skill is correct, adopted, mature, or useful.
