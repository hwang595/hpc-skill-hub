.PHONY: check test validate index site cli clean

PYTHON ?= python3

validate:
	$(PYTHON) tools/validate_skills.py

index:
	$(PYTHON) tools/build_index.py --check

site:
	$(PYTHON) tools/build_site.py --output /tmp/hpc-skill-hub-site/index.html

cli:
	$(PYTHON) tools/hpc_skill.py list
	PYTHONPATH=src $(PYTHON) -m hpc_skill_hub collections
	$(PYTHON) tools/hpc_skill.py search slurm
	$(PYTHON) tools/hpc_skill.py show slurm-submit-job --examples
	$(PYTHON) tools/hpc_skill.py collections
	$(PYTHON) tools/hpc_skill.py collection core-hpc
	$(PYTHON) tools/hpc_skill.py adapters

test:
	$(PYTHON) -m unittest discover -s tests

check: validate index test site cli

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
