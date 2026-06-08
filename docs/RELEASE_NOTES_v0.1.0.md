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

- Skills: 71.
- Collections: 12.
- Site adapters: 2, including 1 example adapter and 1 public-doc-backed draft
  adapter.
- Skill maturity: all seed.
- Risk labels: low and medium only in the seed registry.

## Skill Coverage

- Core HPC and schedulers: Slurm, PBS/OpenPBS, LSF, HTCondor, and Grid Engine
  submission, Slurm and Grid Engine arrays, dependency chains, pending reason
  triage, monitoring, resource estimation, efficiency review,
  checkpoint/restart, failure triage, interactive sessions, Open OnDemand Batch
  Connect templates, Jupyter, RStudio, VS Code tunnels, OpenMP placement, quota
  triage, and scratch management.
- Software stacks: module debugging, module tree health, compiler/MPI
  compatibility, reproducible run capture, Python virtualenv, Open OnDemand
  Batch Connect templates, Ray on Slurm, Dask Jobqueue, JAX distributed smoke
  tests, mpi4py on Slurm, TensorBoard monitors, Streamlit apps, Rscript and
  RStudio on Slurm, Julia on Slurm, MATLAB batch jobs, VS Code tunnels,
  Conda/Mamba, Apptainer builds and runtime, containerized MPI, Spack, and
  EasyBuild.
- Containers: Apptainer-compatible image build planning, container runtime
  execution, containerized MPI launch checks, GPU visibility checks, scratch
  staging, checksum manifests, and reproducible run capture.
- Workflow engines: lightweight Slurm dependency chains, CWL and WDL runs
  inside Slurm allocations, Dask worker clusters, Nextflow, Snakemake, and
  nf-core on Slurm.
- Training and onboarding: workshop preflight, reset checklists, intro Slurm
  workflows, Open OnDemand templates, notebooks, TensorBoard monitors,
  Streamlit apps, RStudio, VS Code tunnels, Python/Conda environments, Rscript,
  Julia, and MATLAB batch jobs, and common learner triage.
- Data movement: Globus, rsync, checksum manifests, scratch staging, archive
  preparation, IOR/MDTest storage smoke benchmarks, scratch inventory, and
  filesystem quota triage.
- GPU/MPI performance: MPI sanity checks, containerized MPI, mpi4py launch
  checks, GPU sanity checks, Ray cluster smoke tests, JAX distributed smoke
  tests, PyTorch DDP, NCCL diagnostics, GPU memory triage, TensorBoard
  monitors, DeepSpeed, OpenMP placement, Slurm efficiency review, storage smoke
  benchmarks, and basic profiling.
- AI/HPC: GPU allocation checks, Ray clusters, Dask workers, JAX distributed
  smoke tests, PyTorch DDP, DeepSpeed, NCCL diagnostics, GPU memory triage,
  TensorBoard monitors,
  Streamlit demos, container runtime execution, data staging, checkpoint/restart
  planning, reproducible run capture, and Slurm efficiency review.
- Bioinformatics: nf-core, GATK, and local BLAST+ workflow patterns with data
  staging and checksum practices.
- Simulation: LAMMPS, GROMACS, NAMD, Quantum ESPRESSO, CP2K, OpenFOAM, WRF, MPI
  launch checks, OpenMP placement, restart planning, profiling, storage smoke
  evidence, and reproducibility.
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
- Discussion category forms and setup guidance for adoption, skill coverage,
  site adapters, review process, and integrations.
- Maturity review template and guidance for promoting skills beyond seed.
- Adoption report template and adopter playbook for public pilot feedback.
- Pull request template with validation, risk, privacy, and reviewer prompts.
- Review routing guidance and CODEOWNERS placeholder for maintainers and domain
  reviewers.
- Triage runbook and starter labels for issue intake and domain-review queues.
- Skill lifecycle guidance for moving requests through seed, review,
  field-testing, maintenance, and deprecation.
- GitHub milestone metadata and command generator for launch, reviewed-skill
  pilot, integration, adapter, and ecosystem backlog planning.
- Launch readiness checks for Discussion forms and milestone metadata.
- Integration guide, integration request template, and starter label for
  downstream tools, portals, assistants, and workflow projects.
- Repository metadata, labels, and starter ruleset files.
- Seed community issues for launch coordination.
- Support and citation metadata for public project use.
- Technical roadmap covering the seed baseline, GitHub launch gates, registry
  growth, integrations, and open ecosystem milestones.
- Public launch packet summarizing local readiness, external GitHub
  prerequisites, launch sequence, outreach targets, and success criteria.
- GitHub owner checklist covering owner identity, permissions, maintainer map,
  public-safety review, and launch decision record before networked
  publication.
- Local launch readiness audit for GitHub publishing.
- Command generators for repository setup, labels, starter issues, rulesets,
  and release publication.
- Deterministic release manifest with file checksums for the seed snapshot.
- Registry index, health, and release manifest schemas plus artifact contract
  validation for downstream consumers.

## Known Limitations

- Skills are seed maturity and should be reviewed by domain maintainers before
  being treated as field-tested.
- The example site adapter is intentionally non-production, and the NERSC
  Perlmutter adapter is a draft derived from public documentation pending site
  review.
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
