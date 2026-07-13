# Agent Bench

Agent Bench measures whether repository guidance and HPC Skill Hub skills improve
coding-agent behavior on realistic, public-safe workloads. It separates task
contracts, execution plans, private run artifacts, reviewed result records, and
generated reports.

The evidence-pilot workflow is dry-run by default:

```bash
python3 tools/agent_benchmark_harness.py --check
python3 tools/agent_benchmark_harness.py --json
python3 tools/agent_benchmark_review.py --help
python3 tools/agent_benchmark_campaign.py --help
python3 tools/run_agent_benchmarks.py --check
python3 tools/run_agent_benchmarks.py --json
```

The calibration plan expands to 54 runs across two agent harnesses, three tasks,
three conditions, and three repeated trials. CI validates that matrix but never
launches an external agent.

The v0.3 smoke campaign in `plans/smoke-v0.3.json` uses one OOM routing task,
three conditions, two agents, and one trial per cell for six runs. It validates
the execution and review pipeline before the 54-run repeated-trial calibration.

The v0.4 evidence campaign in `plans/evidence-v0.4.json` locks the repeated
matrix to one clean commit, exact models, CLI versions, and a reviewed budget.
`tools/agent_benchmark_campaign.py` schedules nine balanced waves and audits
finalized public staging without launching an agent. See the
[campaign operations runbook](../docs/AGENT_BENCHMARK_CAMPAIGN.md).

Check local agent/model readiness without executing a run:

```bash
python3 tools/agent_benchmark_harness.py \
  --plan agent-bench/plans/smoke-v0.3.json \
  --preflight \
  --model-override codex-smoke=<exact-codex-model> \
  --model-override claude-smoke=<exact-claude-model>
```

Materialize all six isolated contexts or inspect resumable state:

```bash
python3 tools/agent_benchmark_harness.py \
  --plan agent-bench/plans/smoke-v0.3.json \
  --materialize-all \
  --workspace-root /tmp/hpc-skill-hub-smoke-contexts

python3 tools/agent_benchmark_harness.py \
  --plan agent-bench/plans/smoke-v0.3.json \
  --status
```

Directory roles:

- `tasks/`: versioned task prompts, fixtures, execution limits, and rubrics.
- `plans/`: reproducible experiment matrices.
- `results/`: reviewed, public-safe result records.
- `artifacts/`: redacted artifacts referenced by imported results.
- `fixtures/`: synthetic inputs used to test the benchmark implementation.

See [`docs/AGENT_BENCHMARKS.md`](../docs/AGENT_BENCHMARKS.md) for execution,
review, scoring, and publication rules. The operational workflow is documented
in [`docs/BLINDED_REVIEW.md`](../docs/BLINDED_REVIEW.md).
