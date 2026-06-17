# Benchmarks

HPC Skill Hub benchmarks test whether skills expose useful, public-safe
evidence for realistic HPC workflows. They are not site-wide performance
claims.

Use this document with [Maturity Review](MATURITY_REVIEW.md),
[Safety Model](SAFETY_MODEL.md), and [Agent Integration](AGENT_INTEGRATION.md).

## Benchmark Modes

| Mode | Runs in CI | Purpose |
| --- | --- | --- |
| `fixture` | yes | Validate that realistic, public-safe logs and scheduler snippets map to expected skill outcomes. |
| `static` | yes | Validate example scripts, batch files, and review artifacts without submitting work. |
| `dry-run` | yes, only when command is explicitly safe | Run plan-only or syntax-only commands that do not consume shared HPC resources. |
| `site` | no by default | Optional real-cluster smoke tests for adopters and site maintainers. |

CI should run fixture, static, and safe dry-run benchmarks only. Site-mode
benchmarks must require explicit opt-in because they may submit jobs, consume
allocations, touch shared filesystems, or depend on public local policy.

## Running Benchmarks

Update the generated report:

```bash
python3 tools/run_benchmarks.py
```

Check benchmark freshness:

```bash
python3 tools/run_benchmarks.py --check
```

Emit machine-readable results:

```bash
python3 tools/run_benchmarks.py --json
```

Run optional site-mode cases only after local review:

```bash
python3 tools/run_benchmarks.py --include-site
```

Some site-mode cases are gated by environment variables so public benchmark
metadata can stay generic while local adopters supply account, partition,
module, or policy values outside the repository. For example:

```bash
HPC_SKILL_HUB_SITE_ACCOUNT=<account> \
HPC_SKILL_HUB_SITE_PARTITION=<partition> \
HPC_SKILL_HUB_MPI_MODULE=<mpi-module> \
python3 tools/run_benchmarks.py --include-site
```

If a required environment variable is missing, the site command is reported as
skipped instead of falling back to placeholders.

## Case Format

Benchmark cases live under [`benchmarks/cases`](../benchmarks/cases) and follow
[`schemas/benchmark.schema.json`](../schemas/benchmark.schema.json). Each case
declares:

- skill ids covered by the benchmark,
- benchmark mode and risk level,
- fixtures and checks,
- safe commands to run,
- optional environment variables required for site-mode commands, and
- expected public-safe outcomes.

Fixtures belong under [`benchmarks/fixtures`](../benchmarks/fixtures). They
must not contain private hostnames, usernames, allocation names, internal
project ids, tokens, private paths, or unpublished operating procedures.

## Promotion Use

Benchmark results are supporting evidence, not automatic maturity decisions.
They can support:

- `reviewed` promotion when examples and assumptions survive repeatable static
  or fixture checks,
- `field-tested` promotion when site-mode results are paired with public-safe
  adoption notes, and
- regression checks when examples or triage wording changes.

See the generated [Benchmark Report](BENCHMARK_REPORT.md) for the current
CI-safe case results.
