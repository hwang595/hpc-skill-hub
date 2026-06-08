# v0.1.0 Release Notes

Status: planned seed release.

## Summary

`v0.1.0` is the first public snapshot of HPC Skill Hub: an open registry of
reusable, reviewable skills for running, debugging, optimizing, and maintaining
HPC workflows.

The release is intended for early adopters, HPC centers, research software
engineers, instructors, and domain reviewers who want to test the skill format,
request missing workflows, or contribute public site adapters.

## Registry Contents

- Skills: 57.
- Collections: 11.
- Site adapters: 1 example adapter.
- Skill maturity: all seed.
- Risk labels: low and medium only in the seed registry.

## Skill Coverage

- Core HPC: Slurm submission, arrays, dependency chains, pending reason triage,
  monitoring, resource estimation, efficiency review, checkpoint/restart,
  failure triage, interactive sessions, Jupyter, OpenMP placement, quota
  triage, and scratch management.
- Software stacks: module debugging, module tree health, compiler/MPI
  compatibility, reproducible run capture, Python virtualenv, Ray on Slurm,
  Dask Jobqueue, mpi4py on Slurm, Rscript on Slurm, Julia on Slurm, MATLAB
  batch jobs, Conda/Mamba, Apptainer builds and runtime, Spack, and EasyBuild.
- Containers: Apptainer-compatible image build planning, container runtime
  execution, GPU visibility checks, scratch staging, checksum manifests, and
  reproducible run capture.
- Workflow engines: lightweight Slurm dependency chains, CWL and WDL runs
  inside Slurm allocations, Dask worker clusters, Nextflow, Snakemake, and
  nf-core on Slurm.
- Training and onboarding: workshop preflight, reset checklists, intro Slurm
  workflows, notebooks, Python/Conda environments, Rscript, Julia, and MATLAB
  batch jobs, and common learner triage.
- Data movement: Globus, rsync, checksum manifests, scratch staging, archive
  preparation, scratch inventory, and filesystem quota triage.
- GPU/MPI performance: MPI sanity checks, mpi4py launch checks, GPU sanity
  checks, Ray cluster smoke tests, PyTorch DDP, NCCL diagnostics, GPU memory
  triage, DeepSpeed, OpenMP placement, Slurm efficiency review, and basic
  profiling.
- AI/HPC: GPU allocation checks, Ray clusters, Dask workers, PyTorch DDP,
  DeepSpeed, NCCL diagnostics, GPU memory triage, container runtime execution,
  data staging, checkpoint/restart planning, reproducible run capture, and
  Slurm efficiency review.
- Bioinformatics: nf-core, GATK, and local BLAST+ workflow patterns with data
  staging and checksum practices.
- Simulation: LAMMPS, GROMACS, Quantum ESPRESSO, OpenFOAM, WRF, MPI launch
  checks, OpenMP placement, restart planning, profiling, and reproducibility.
- Facility operations: read-only Slurm usage reporting, pending reason triage,
  node-health triage, and module tree health checks for support teams and
  facility maintainers.

## Tooling

- `python3 tools/hpc_skill.py validate`
- `python3 tools/hpc_skill.py list`
- `python3 tools/hpc_skill.py search <query>`
- `python3 tools/hpc_skill.py show <skill-id> --examples`
- `python3 tools/hpc_skill.py collections`
- `python3 tools/hpc_skill.py collection <collection-id>`
- `python3 tools/hpc_skill.py adapter <adapter-id>`
- `python3 tools/hpc_skill.py scaffold skill <skill-id>`
- `python3 tools/hpc_skill.py scaffold site-adapter <adapter-id>`
- `python3 tools/hpc_skill.py health`

## GitHub Launch Readiness

- Validation workflow for every pull request and push to `main`.
- Package workflow for source distribution, wheel, metadata, and installed CLI
  smoke checks.
- GitHub Pages publishing workflow for the generated static registry, including
  ecosystem entry points for adopters, contributors, site adapters,
  integrations, safety review, and RFCs.
- Dependabot configuration for GitHub Actions and Python packaging.
- Issue templates for bugs, docs, skill requests, site adapters, and safety
  review.
- Maturity review template and guidance for promoting skills beyond seed.
- Adoption report template and adopter playbook for public pilot feedback.
- Pull request template with validation, risk, privacy, and reviewer prompts.
- Review routing guidance and CODEOWNERS placeholder for maintainers and domain
  reviewers.
- Triage runbook and starter labels for issue intake and domain-review queues.
- Skill lifecycle guidance for moving requests through seed, review,
  field-testing, maintenance, and deprecation.
- Integration guide, integration request template, and starter label for
  downstream tools, portals, assistants, and workflow projects.
- Repository metadata, labels, and starter ruleset files.
- Seed community issues for launch coordination.
- Support and citation metadata for public project use.
- Local launch readiness audit for GitHub publishing.
- Command generators for repository setup, labels, starter issues, rulesets,
  and release publication.
- Deterministic release manifest with file checksums for the seed snapshot.
- Registry index, health, and release manifest schemas plus artifact contract
  validation for downstream consumers.

## Known Limitations

- Skills are seed maturity and should be reviewed by domain maintainers before
  being treated as field-tested.
- The example site adapter is intentionally non-production.
- GitHub remote creation, label application, ruleset application, and Pages
  activation must be performed in an authenticated GitHub environment.
- No private cluster policy, credentials, allocation names, hostnames, or
  unpublished security procedures should be added to the public registry.

## Release Checks

Before tagging `v0.1.0`, maintainers should confirm:

- `make check` passes locally, `Validate` passes in GitHub Actions, and
  `Package` passes source distribution, wheel, metadata, and installed CLI
  smoke checks.
- `registry/index.json`, `registry/health.json`, `docs/SKILL_CATALOG.md`, and
  `docs/REGISTRY_HEALTH.md` are current.
- `docs/COMPATIBILITY.md` and `registry/releases/v0.1.0.json` are current.
- GitHub repository metadata, labels, and rulesets match `.github/`.
- The generated Pages site is published.
- The first community issue is pinned.
