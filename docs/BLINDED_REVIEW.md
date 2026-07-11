# Blinded Review And Scoring

The blinded review workflow turns private `pending-review` agent runs into a
staged, public-safe scored bundle. It keeps agent identity and experiment
condition away from reviewers while preserving a private, digest-bound mapping
for finalization.

The workflow never launches an agent and never imports files into the
repository automatically. Private mapping, salt, and finalized staging paths
are rejected when they resolve inside the repository.

## Trust Boundaries

Keep these locations separate:

- **Private run root:** raw result records and harness artifacts.
- **Private control data:** the blind salt and blind-id-to-run mapping.
- **Review packet:** redacted responses, task rubrics, score templates, and a
  manifest that omits run id, agent, harness, model, and condition.
- **Public staging bundle:** finalized result JSON and the redacted response
  selected for publication.

Distribute only the review packet to reviewers. Do not distribute the salt,
private mapping, raw run root, or existing result metadata.

## 1. Prepare

Create a private random salt with restrictive permissions, then prepare the
packet. The mapping must be outside the packet root.

```bash
umask 077
mkdir -p /tmp/hpc-skill-hub-review-private
openssl rand -out /tmp/hpc-skill-hub-review-private/blind-salt.bin 32

python3 tools/agent_benchmark_review.py prepare \
  --plan agent-bench/plans/smoke-v0.3.json \
  --run-root /tmp/hpc-skill-hub-agent-bench-runs \
  --packet-root /tmp/hpc-skill-hub-review-packet \
  --mapping /tmp/hpc-skill-hub-review-private/mapping.json \
  --salt-file /tmp/hpc-skill-hub-review-private/blind-salt.bin \
  --redaction-reviewer <reviewer-id> \
  --json
```

Preparation accepts only results that are `pending-review`, record an exact
model id, come from a clean repository snapshot, and have network access
disabled. It verifies the final-output digest and runs the repository safety
audit plus the high-severity skill security gate. The named redaction reviewer
remains responsible for confirming that the response is safe to distribute.

Blind ids are HMAC-SHA256 identifiers derived from the private salt and run id.
The private mapping binds the packet manifest, and the manifest binds each
response, rubric, and score template by SHA-256. Reusing the same salt makes
packet regeneration deterministic; use a new salt for a new review campaign.

## 2. Review Independently

Each case contains `response.txt`, `rubric.json`, and `score-template.json`.
Each reviewer copies the template into a separate reviewer directory and fills
every criterion with a score from 0 to 1 and a non-empty rationale:

```text
/tmp/hpc-skill-hub-reviews/
  reviewer-a/case-012345abcdef.json
  reviewer-b/case-012345abcdef.json
```

Reviewers must not share scores before submitting their independent reviews and
must not try to identify the agent or condition. `reviewer_type` is `human` or
`llm-assisted`; LLM assistance must be disclosed.

Check packet state:

```bash
python3 tools/agent_benchmark_review.py status \
  --packet-root /tmp/hpc-skill-hub-review-packet \
  --mapping /tmp/hpc-skill-hub-review-private/mapping.json \
  --reviews-dir /tmp/hpc-skill-hub-reviews \
  --reconciliations-dir /tmp/hpc-skill-hub-reconciliations \
  --json
```

Every case requires exactly two reviews with different reviewer ids. Unknown
blind ids, extra reviews, incomplete rubrics, duplicate criteria, invalid
timestamps, and unrecognized reconciliation files make the packet invalid.

## 3. Reconcile

If any criterion differs by `0.25` or more, status becomes
`needs-reconciliation`. Create one reconciliation JSON for that blind id using
[`agent-benchmark-reconciliation.schema.json`](../schemas/agent-benchmark-reconciliation.schema.json).
It must name the two original reviewers and include a final score and rationale
for every criterion.

When no criterion reaches the threshold, finalization uses the arithmetic mean
of the two independent scores for each criterion.

## 4. Finalize To Staging

Finalize only after every case reports `ready`:

```bash
python3 tools/agent_benchmark_review.py finalize \
  --packet-root /tmp/hpc-skill-hub-review-packet \
  --mapping /tmp/hpc-skill-hub-review-private/mapping.json \
  --reviews-dir /tmp/hpc-skill-hub-reviews \
  --reconciliations-dir /tmp/hpc-skill-hub-reconciliations \
  --output-root /tmp/hpc-skill-hub-reviewed-staging \
  --json
```

Finalization rechecks the source-result and redacted-response digests, records
the two reviewer ids and blinded evaluation provenance, retains only the
redacted final response, reruns safety and security checks, and validates the
staged result with the existing benchmark aggregator.

Inspect the staging bundle before adding selected files to
`agent-bench/results/` and `agent-bench/artifacts/`. Raw transcripts, private
mapping data, salts, and reviewer working directories must never be committed.

## Public Contracts

- Review packet manifest:
  [`agent-benchmark-review-packet.schema.json`](../schemas/agent-benchmark-review-packet.schema.json)
- Independent review:
  [`agent-benchmark-review.schema.json`](../schemas/agent-benchmark-review.schema.json)
- Reconciliation:
  [`agent-benchmark-reconciliation.schema.json`](../schemas/agent-benchmark-reconciliation.schema.json)
- Final result:
  [`agent-benchmark-result.schema.json`](../schemas/agent-benchmark-result.schema.json)
