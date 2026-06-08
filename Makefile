.PHONY: audit check compatibility health release-manifest test validate index site cli clean

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

release-manifest:
	$(PYTHON) tools/build_release_manifest.py v0.1.0 --check

audit:
	$(PYTHON) tools/audit_safety.py

site:
	$(PYTHON) tools/build_site.py --output $(SITE_OUTPUT)

cli:
	$(PYTHON) tools/hpc_skill.py list
	PYTHONPATH=src $(PYTHON) -m hpc_skill_hub collections
	$(PYTHON) tools/hpc_skill.py health
	$(PYTHON) tools/hpc_skill.py validate --skill slurm-submit-job
	$(PYTHON) tools/hpc_skill.py search slurm
	$(PYTHON) tools/hpc_skill.py show slurm-submit-job --examples
	$(PYTHON) tools/hpc_skill.py collections
	$(PYTHON) tools/hpc_skill.py collection core-hpc
	$(PYTHON) tools/hpc_skill.py adapters

test:
	$(PYTHON) -m unittest discover -s tests

check: validate index health compatibility release-manifest audit test site cli

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
