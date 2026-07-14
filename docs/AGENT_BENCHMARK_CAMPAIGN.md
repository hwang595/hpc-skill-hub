# Agent Benchmark Campaign Operations

This runbook operates the v0.4 and v0.5 real-evidence campaigns after the benchmark
contracts are merged. The campaign tool locks provenance, randomizes balanced
execution waves, reports resumable state, and audits public staging. It never
launches an agent.

## Safety Boundary

- Keep the campaign lock, raw runs, blind salt, private mapping, reviews, and
  reconciliations outside the repository.
- Use one clean repository commit for the complete campaign.
- Pin exact Codex and Claude Code model ids and CLI versions.
- Approve provider quota before creating the campaign lock. The v0.4 plan
  authorizes at most USD 0.75 per run and USD 40.50 for the campaign; the v0.5
  MCP plan keeps the per-run cap and raises the 72-run ceiling to USD 54.00.
- Treat Claude Code's provider CLI budget as a hard limit. Codex usage requires
  external quota monitoring when its CLI does not expose an equivalent limit.
- Run one generated command at a time. Do not turn the command list into an
  unattended batch script.
- Stop when status reports an invalid result, changed provenance, insufficient
  budget, or any other blocker.

CI may exercise the campaign logic with synthetic fixtures, but it must never
run `prepare` against authenticated agents or execute a generated command.

## 1. Lock The Campaign

Start from the clean commit that will own every result. Confirm both CLIs are
installed and authenticated, choose exact model ids, and create a private
campaign directory:

```bash
umask 077
mkdir -p /tmp/hpc-skill-hub-v0.4-campaign

python3 tools/agent_benchmark_campaign.py prepare \
  --plan agent-bench/plans/evidence-v0.4.json \
  --model-override codex-v0-4=<exact-codex-model> \
  --model-override claude-v0-4=<exact-claude-model> \
  --seed <public-randomization-seed> \
  --output /tmp/hpc-skill-hub-v0.4-campaign/campaign.json \
  --acknowledge-paid-quota \
  --json
```

`prepare` runs the clean-commit and exact-model preflight, records the plan and
task digests, locks CLI versions, records budget enforcement mode, and creates
a deterministic schedule. It performs no agent call.

The 54-run v0.4 matrix becomes nine randomized waves. Each wave contains all
six agent and condition combinations for one task/trial pair, reducing order
bias without separating paired observations.

For the v0.5 MCP campaign, use the new plan and variant ids:

```bash
python3 tools/agent_benchmark_campaign.py prepare \
  --plan agent-bench/plans/evidence-v0.5.json \
  --model-override codex-v0-5=<exact-codex-model> \
  --model-override claude-v0-5=<exact-claude-model> \
  --seed <public-randomization-seed> \
  --output /tmp/hpc-skill-hub-v0.5-campaign/campaign.json \
  --acknowledge-paid-quota \
  --json
```

This command remains blocked until `hpc-skill doctor --require-mcp` passes. The
lock records the canonical MCP client-contract digest and installed package
version. The 72-run matrix has nine waves of eight agent/condition
combinations; campaign preparation still performs no paid agent call.

## 2. Inspect The Next Wave

Create a separate private run root and inspect status:

```bash
python3 tools/agent_benchmark_campaign.py status \
  --campaign /tmp/hpc-skill-hub-v0.4-campaign/campaign.json \
  --run-root /tmp/hpc-skill-hub-v0.4-runs \
  --json
```

Status rechecks the current clean commit and installed CLI versions, then
validates every existing result against the locked model, repository commit,
plan identity, and budget. It emits commands only for the
unfinished runs in the earliest incomplete wave. The commands include the
existing `--allow-paid-run` acknowledgement, but status does not execute them.

Before each command:

1. Review the run id, agent, model, task, condition, and remaining budget.
2. Confirm that no other campaign process is running the same id.
3. Execute exactly one command.
4. Re-run status and inspect the new result before continuing.

Do not use `--force` for public evidence. Preserve failed and timed-out results
instead of replacing them with a more favorable retry.

## 3. Blind And Review

After the intended runs are complete, use the existing digest-bound workflow:

```bash
python3 tools/agent_benchmark_review.py prepare \
  --plan agent-bench/plans/evidence-v0.4.json \
  --run-root /tmp/hpc-skill-hub-v0.4-runs \
  --packet-root /tmp/hpc-skill-hub-v0.4-review-packet \
  --mapping /tmp/hpc-skill-hub-v0.4-private/mapping.json \
  --salt-file /tmp/hpc-skill-hub-v0.4-private/blind-salt.bin \
  --redaction-reviewer <reviewer-id> \
  --json
```

Collect exactly two independent blinded reviews per case, reconcile criterion
differences of `0.25` or more, and finalize to a staging directory outside the
repository. Follow [Blinded Review And Scoring](BLINDED_REVIEW.md) for the full
trust boundary and commands.

## 4. Audit Public Staging

Audit the finalized bundle before copying any file into the repository:

```bash
python3 tools/agent_benchmark_campaign.py audit \
  --campaign /tmp/hpc-skill-hub-v0.4-campaign/campaign.json \
  --staging-root /tmp/hpc-skill-hub-v0.4-reviewed-staging \
  --json
```

The default audit requires the complete campaign: 54 runs for v0.4 or 72 for
v0.5. `--allow-partial` may be used to inspect a reviewed wave, but incomplete
evidence remains visible and cannot open the comparative publication gate.

The audit verifies:

- run identity, exact model, CLI version, and locked repository commit,
- scored status and exactly two independent blinded reviewers,
- task and result contracts,
- public artifact location and SHA-256 digest,
- absence of raw output, stderr, salts, mappings, and reviewer work products,
- repository safety audit and community-skill security findings.

Any security verdict of `review` blocks import by default. Only after a human
has reviewed every finding may the audit be repeated with
`--security-reviewer <reviewer-id>`. The audit output records that reviewer id.
Blocking findings cannot be acknowledged away.

## 5. Import And Publish

Manually inspect a ready staging bundle, then add only its `results/` records
and `artifacts/` files to the matching `agent-bench/` directories. Never add
the campaign lock, raw run root, packet mapping, salt, reviewer directories, or
reconciliation work products.

Regenerate the report and dashboard:

```bash
python3 tools/run_agent_benchmarks.py
make check
```

The dashboard independently enforces the publication gate. A successful
staging audit does not guarantee a ranking: the imported repository evidence
must still have complete paired comparisons, no pending reviews, exact
provenance, two blinded reviewers per scored run, and digest-verified public
artifacts.
