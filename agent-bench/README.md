# Agent Bench

Agent Bench measures whether repository guidance and HPC Skill Hub skills improve
coding-agent behavior on realistic, public-safe workloads. It separates task
contracts, execution plans, private run artifacts, reviewed result records, and
generated reports.

The evidence-pilot workflow is dry-run by default:

```bash
python3 tools/agent_benchmark_harness.py --check
python3 tools/agent_benchmark_harness.py --json
python3 tools/run_agent_benchmarks.py --check
python3 tools/run_agent_benchmarks.py --json
```

The calibration plan expands to 54 runs across two agent harnesses, three tasks,
three conditions, and three repeated trials. CI validates that matrix but never
launches an external agent.

Directory roles:

- `tasks/`: versioned task prompts, fixtures, execution limits, and rubrics.
- `plans/`: reproducible experiment matrices.
- `results/`: reviewed, public-safe result records.
- `artifacts/`: redacted artifacts referenced by imported results.
- `fixtures/`: synthetic inputs used to test the benchmark implementation.

See [`docs/AGENT_BENCHMARKS.md`](../docs/AGENT_BENCHMARKS.md) for execution,
review, scoring, and publication rules.
