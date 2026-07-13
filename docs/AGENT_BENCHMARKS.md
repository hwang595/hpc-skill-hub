# Agent Benchmarks

Agent Benchmarks compare coding agents on public-safe HPC Skill Hub workloads.
The primary question is whether repository guidance and registry-backed skills
improve correctness and safety without unacceptable failure, time, token, or
cost regressions.

CI validates contracts, context isolation, the experiment matrix, aggregation,
and generated reports. It never launches Codex, Claude Code, or another paid
agent.

## Conditions

| Condition | Context available to the agent |
| --- | --- |
| `baseline` | Task prompt and condition-scoped synthetic fixtures only. |
| `docs-only` | Baseline context plus `AGENTS.md` and provider-specific repository guidance. |
| `skill-enabled` | Documentation context plus the router skill, registry index, CLI, and selected skill packages. |
| `skill-site-adapter` | Skill context plus an explicitly declared public site adapter. |

Fixtures declare their allowed conditions. The validator rejects skill files in
`baseline` or `docs-only` and rejects site-adapter files outside
`skill-site-adapter`.

## Contracts

Tasks follow
[`agent-benchmark-task.schema.json`](../schemas/agent-benchmark-task.schema.json).
Each task declares its version, conditions, skill ids, condition-scoped
fixtures, workspace mode, network policy, timeout, allowed write paths, rubric,
and expected outcomes.

Experiment plans follow
[`agent-benchmark-plan.schema.json`](../schemas/agent-benchmark-plan.schema.json).
The v0.2 calibration plan selects three tasks, two agent harnesses, three
conditions, and three trials per cell, producing 54 planned runs.
The v0.4 evidence plan adds an explicit per-run budget, total campaign ceiling,
and paid-run acknowledgement contract to the same balanced matrix.

Reviewed results follow
[`agent-benchmark-result.schema.json`](../schemas/agent-benchmark-result.schema.json).
They record exact agent, harness, model, task and repository provenance;
execution metrics; status; failure category; artifacts; rubric scores; and
evaluator provenance.

Blinded packet manifests, independent reviews, and reconciliations follow
[`agent-benchmark-review-packet.schema.json`](../schemas/agent-benchmark-review-packet.schema.json),
[`agent-benchmark-review.schema.json`](../schemas/agent-benchmark-review.schema.json),
and
[`agent-benchmark-reconciliation.schema.json`](../schemas/agent-benchmark-reconciliation.schema.json).

## Dry Run And Isolation

Inspect the deterministic matrix:

```bash
python3 tools/agent_benchmark_harness.py --json
```

Materialize one isolated context packet without launching an agent:

```bash
python3 tools/agent_benchmark_harness.py \
  --materialize <run-id> \
  --workspace-root /tmp/hpc-skill-hub-agent-bench-workspaces
```

The harness copies only condition-appropriate files. Baseline packets exclude
`AGENTS.md`, `CLAUDE.md`, `.agents/`, `.claude/`, registry indexes, and skill
packages. Skill-enabled packets include only the selected skills.

## Explicit Execution

A real run requires a single run id, an exact model id, and acknowledgement that
the command may consume paid quota:

```bash
python3 tools/agent_benchmark_harness.py \
  --execute <run-id> \
  --model <exact-model-id> \
  --allow-paid-run
```

The Codex adapter uses non-interactive, ephemeral execution with the task's
read-only or workspace-write sandbox. The Claude Code adapter uses print mode,
project-only settings, no session persistence, no MCP tools, and an allowlist of
read or edit tools based on the task contract. The harness refuses execution
when the matching CLI is unavailable.

Outputs go to `/tmp/hpc-skill-hub-agent-bench-runs` by default. Successful runs
are `pending-review`; the harness does not award scores. Review and redact all
outputs before copying selected artifacts or result records into the repository.

## Blinded Scoring

Use two reviewers for the calibration set:

1. Hide agent, model, harness, and condition labels from the review packet.
2. Score every criterion independently from 0 to 1. Suggested anchors are
   `0`, `0.25`, `0.5`, `0.75`, and `1`.
3. Reconcile any criterion difference of `0.25` or more and retain both public
   reviewer identifiers in `evaluation.evaluator_ids`.
4. Set `evaluation.blinded` accurately and match `rubric_version` to the task
   version.
5. Change status from `pending-review` to `scored` only after redaction and
   rubric completion.

LLM-assisted scoring may support reviewers, but it must be labeled
`llm-assisted`; it is not a substitute for calibration against human ratings.

Use `tools/agent_benchmark_review.py` to prepare digest-bound packets, validate
exactly two independent reviews, require reconciliation at the disagreement
threshold, and finalize a public staging bundle. The private mapping and salt
must stay outside the distributed packet. See the
[Blinded Review And Scoring runbook](BLINDED_REVIEW.md) for commands, trust
boundaries, and publication handling.

## Aggregation

The report uses rubric-weighted task scores from 0 to 100. Overall condition
scores are macro-averaged by task so additional trials cannot overweight one
workload. It reports:

- scored, failed, pending-review, and skipped run counts,
- terminal failure rate,
- score and 95% confidence interval when enough task values exist,
- mean wall time, tokens, and cost when provided,
- paired lift for matching task and trial numbers.

```text
Skill Lift = score(skill-enabled) - score(baseline)
Site Adapter Lift = score(skill-site-adapter) - score(skill-enabled)
```

Generate or check the public report with:

```bash
python3 tools/run_agent_benchmarks.py
python3 tools/run_agent_benchmarks.py --check
python3 tools/run_agent_benchmarks.py --json
```

See the generated [Calibration Plan](AGENT_BENCHMARK_PLAN.md),
[v0.3 Smoke Plan](AGENT_BENCHMARK_SMOKE_PLAN.md), and
[v0.4 Evidence Plan](AGENT_BENCHMARK_V0_4_PLAN.md). Public output is available
as both an [Agent Benchmark Report](AGENT_BENCHMARK_REPORT.md) and an
[Evidence Dashboard](AGENT_BENCHMARK_DASHBOARD.html).

## v0.3 Six-Run Smoke Campaign

Before spending quota on the 54-run repeated-trial matrix, validate one paired
task across both agents and all three core conditions:

```bash
python3 tools/agent_benchmark_harness.py \
  --plan agent-bench/plans/smoke-v0.3.json \
  --preflight \
  --model-override codex-smoke=<exact-codex-model> \
  --model-override claude-smoke=<exact-claude-model>
```

Preflight verifies that each CLI is installed, records its version, blocks
`configured-default` model aliases, rejects network-enabled task contracts, and
requires a clean repository commit. It does not call either agent.

Materialize every isolated context without paid execution:

```bash
python3 tools/agent_benchmark_harness.py \
  --plan agent-bench/plans/smoke-v0.3.json \
  --materialize-all \
  --workspace-root /tmp/hpc-skill-hub-smoke-contexts
```

Check resumable state and the next pending run:

```bash
python3 tools/agent_benchmark_harness.py \
  --plan agent-bench/plans/smoke-v0.3.json \
  --status --json
```

Real execution remains one explicit run at a time and requires both an exact
model id and `--allow-paid-run`. The smoke plan sets a USD 0.50 per-run ceiling
for Claude Code. Codex CLI does not expose the same hard budget switch, so its
quota must be approved and monitored outside the harness.

Do not score a dirty-worktree run as public evidence. Commit the benchmark
contract first, execute from that clean commit, redact artifacts, and then use
the blinded review and scoring tool. `--allow-dirty-run` exists only for
explicitly non-public harness debugging.

## v0.4 Repeated Evidence Campaign

The v0.4 plan expands the validated smoke path to three public-safe tasks,
three conditions, three trials, and two agents: 54 runs in total. Inspect its
matrix and preflight exact model ids without launching an agent:

```bash
python3 tools/agent_benchmark_harness.py \
  --plan agent-bench/plans/evidence-v0.4.json \
  --json

python3 tools/agent_benchmark_harness.py \
  --plan agent-bench/plans/evidence-v0.4.json \
  --preflight \
  --model-override codex-v0-4=<exact-codex-model> \
  --model-override claude-v0-4=<exact-claude-model>
```

The plan sets a USD 0.75 per-run ceiling and a USD 40.50 total campaign
ceiling. Before each run, the harness sums recorded result costs and refuses to
start when the next per-run allowance would exceed the total. The total is an
authorization ceiling, not a spending target. Codex quota and any provider
charges that are not exposed to the harness still require external monitoring.

Track resumable state and recorded budget without paid execution:

```bash
python3 tools/agent_benchmark_harness.py \
  --plan agent-bench/plans/evidence-v0.4.json \
  --status --json
```

Real execution remains one run at a time. Each invocation requires an exact
model id and `--allow-paid-run`; the plan cannot authorize a batch launch.
Review the [v0.4 Completion Matrix](V0_4_COMPLETION.md) before opening the real
campaign.

## Publication Gate

Do not publish a leaderboard row until:

- the model and agent versions are exact rather than `configured-default`,
- the run comes from a clean repository snapshot at the recorded commit,
- at least three trials exist for each compared condition,
- failures and pending runs remain visible,
- every scored run has exactly two independent blinded reviewers,
- every scored run has digest-verified public artifacts that pass the
  repository safety audit and human redaction review,
- paired conditions use the same task version and trial numbers,
- scoring provenance names the rubric version and reviewer method.

`tools/run_agent_benchmarks.py` enforces these requirements as a publication
readiness gate. The dashboard lists blockers and suppresses comparative
ranking until the gate opens.
