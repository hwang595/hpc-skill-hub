.PHONY: agent-adapters agent-benchmarks artifact-contracts audit benchmarks check compatibility health package-data release-manifest review-packet security test validate index site cli clean

PYTHON ?= python3
SITE_OUTPUT ?= /tmp/hpc-skill-hub-site/index.html

validate:
	$(PYTHON) tools/validate_skills.py

index:
	$(PYTHON) tools/build_index.py --check

health:
	$(PYTHON) tools/build_health.py --check

compatibility:
	$(PYTHON) tools/build_compatibility.py --check

agent-adapters:
	$(PYTHON) tools/build_agent_adapters.py --check

agent-benchmarks:
	$(PYTHON) tools/agent_benchmark_harness.py --check
	$(PYTHON) tools/agent_benchmark_harness.py --plan agent-bench/plans/smoke-v0.3.json --report docs/AGENT_BENCHMARK_SMOKE_PLAN.md --check
	$(PYTHON) tools/agent_benchmark_review.py --help
	$(PYTHON) tools/run_agent_benchmarks.py --check

benchmarks:
	$(PYTHON) tools/run_benchmarks.py --check

package-data:
	$(PYTHON) tools/build_package_data.py --check

release-manifest:
	$(PYTHON) tools/validate_registry_artifacts.py --release-only

review-packet:
	$(PYTHON) tools/review_packet.py --check

artifact-contracts:
	$(PYTHON) tools/validate_registry_artifacts.py

audit:
	$(PYTHON) tools/audit_safety.py

security:
	$(PYTHON) tools/scan_skill_security.py skills --fail-on high

site:
	$(PYTHON) tools/build_site.py --output $(SITE_OUTPUT)

cli:
	$(PYTHON) tools/hpc_skill.py list
	PYTHONPATH=src $(PYTHON) -m hpc_skill_hub collections
	$(PYTHON) tools/hpc_skill.py health
	$(PYTHON) tools/hpc_skill.py validate --skill slurm-submit-job
	$(PYTHON) tools/hpc_skill.py validate --skill slurm-submit-job --json
	$(PYTHON) tools/hpc_skill.py check slurm-submit-job
	$(PYTHON) tools/hpc_skill.py search slurm
	$(PYTHON) tools/hpc_skill.py show slurm-submit-job --examples
	$(PYTHON) tools/hpc_skill.py collections
	$(PYTHON) tools/hpc_skill.py collection core-hpc
	$(PYTHON) tools/hpc_skill.py adapters
	$(PYTHON) tools/hpc_skill.py resolve slurm-submit-job --adapter example-campus-cluster --json
	$(PYTHON) tools/hpc_skill.py security skills/slurm-submit-job --fail-on high

test:
	$(PYTHON) -m unittest discover -s tests

check: validate index health compatibility agent-adapters benchmarks agent-benchmarks package-data release-manifest review-packet artifact-contracts audit security test site cli

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
