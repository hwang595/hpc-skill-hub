.PHONY: agent-adapters agent-benchmarks artifact-contracts audit benchmarks check cli community-context community-evidence compatibility doctor health index intake mcp mcp-client-configs package-data receipt release-manifest release-status review-packet security site skill-context skill-quality skill-reviews test trust-policy validate clean

PYTHON ?= python3
SITE_OUTPUT ?= /tmp/hpc-skill-hub-site/index.html

validate:
	$(PYTHON) tools/validate_skills.py

index:
	$(PYTHON) tools/build_index.py --check

health:
	$(PYTHON) tools/build_health.py --check

skill-quality:
	$(PYTHON) tools/build_skill_quality.py --check

skill-reviews:
	$(PYTHON) tools/build_skill_reviews.py --check

skill-context:
	$(PYTHON) tools/build_skill_context.py --check

compatibility:
	$(PYTHON) tools/build_compatibility.py --check

mcp-client-configs:
	$(PYTHON) tools/build_mcp_client_configs.py --check

agent-adapters:
	$(PYTHON) tools/build_agent_adapters.py --check

agent-benchmarks:
	$(PYTHON) tools/agent_benchmark_harness.py --check
	$(PYTHON) tools/agent_benchmark_harness.py --plan agent-bench/plans/smoke-v0.3.json --report docs/AGENT_BENCHMARK_SMOKE_PLAN.md --check
	$(PYTHON) tools/agent_benchmark_harness.py --plan agent-bench/plans/evidence-v0.4.json --report docs/AGENT_BENCHMARK_V0_4_PLAN.md --check
	$(PYTHON) tools/agent_benchmark_harness.py --plan agent-bench/plans/evidence-v0.5.json --report docs/AGENT_BENCHMARK_V0_5_PLAN.md --check
	$(PYTHON) tools/agent_benchmark_campaign.py --help
	$(PYTHON) tools/agent_benchmark_review.py --help
	$(PYTHON) tools/run_agent_benchmarks.py --check

release-status:
	$(PYTHON) tools/build_release_status.py --check

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

intake:
	$(PYTHON) tools/quarantine_skill_intake.py tests/fixtures/intake/benign-skill --json

receipt:
	$(PYTHON) tools/community_intake_receipt.py create tests/fixtures/intake/benign-skill --json

community-evidence:
	$(PYTHON) tools/community_review_evidence.py --help

community-context:
	$(PYTHON) tools/community_context_bundle.py --help

trust-policy:
	$(PYTHON) -m unittest tests.test_skill_security

site:
	$(PYTHON) tools/build_site.py --output $(SITE_OUTPUT)

cli:
	$(PYTHON) tools/hpc_skill.py list
	PYTHONPATH=src $(PYTHON) -m hpc_skill_hub collections
	$(PYTHON) tools/hpc_skill.py health
	PYTHONPATH=src $(PYTHON) -m hpc_skill_hub doctor --json
	$(PYTHON) tools/hpc_skill.py review candidates
	$(PYTHON) tools/hpc_skill.py review status job-failure-triage
	$(PYTHON) tools/hpc_skill.py review check reviews/v0.4.0/job-failure-triage.json
	$(PYTHON) tools/hpc_skill.py validate --skill slurm-submit-job
	$(PYTHON) tools/hpc_skill.py validate --skill slurm-submit-job --json
	$(PYTHON) tools/hpc_skill.py check slurm-submit-job
	$(PYTHON) tools/hpc_skill.py search slurm
	$(PYTHON) tools/hpc_skill.py show slurm-submit-job --examples
	$(PYTHON) tools/hpc_skill.py collections
	$(PYTHON) tools/hpc_skill.py collection core-hpc
	$(PYTHON) tools/hpc_skill.py adapters
	$(PYTHON) tools/hpc_skill.py resolve slurm-submit-job --adapter example-campus-cluster --json
	$(PYTHON) tools/hpc_skill.py intake tests/fixtures/intake/benign-skill --json
	$(PYTHON) tools/hpc_skill.py receipt create tests/fixtures/intake/benign-skill --json
	$(PYTHON) tools/hpc_skill.py evidence --help
	$(PYTHON) tools/hpc_skill.py community-context --help
	$(PYTHON) tools/hpc_skill.py security skills/slurm-submit-job --fail-on high

mcp:
	PYTHONPATH=src $(PYTHON) -m hpc_skill_hub.mcp_server --help

doctor:
	PYTHONPATH=src $(PYTHON) -m hpc_skill_hub doctor --json

test:
	$(PYTHON) -m unittest discover -s tests

check: validate index health skill-quality skill-reviews skill-context compatibility mcp-client-configs agent-adapters benchmarks agent-benchmarks release-status package-data release-manifest review-packet artifact-contracts audit security intake receipt community-evidence community-context trust-policy test site cli mcp doctor

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
