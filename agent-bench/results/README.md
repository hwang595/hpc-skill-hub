# Agent Benchmark Results

Place reviewed, public-safe result JSON files here. Each file must follow
`schemas/agent-benchmark-result.schema.json`, use its `run_id` as the filename,
and record the exact task version, trial number, model, agent and harness
versions, repository commit, task hash, workspace policy, metrics, and evaluator
provenance.

Successful harness runs begin as `pending-review`. A result becomes `scored`
only after its artifacts are redacted and reviewers complete every rubric
criterion. Failed runs remain visible and contribute to the reported failure
rate instead of disappearing from the leaderboard.

Do not commit raw transcripts, private hostnames, usernames, accounts,
allocation names, tokens, private paths, internal project ids, or unpublished
site policy.
