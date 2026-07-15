# Changelog

All notable changes to HPC Skill Hub are tracked here.

This project uses semantic versioning for repository releases. Individual
skills keep their own `version` field in `skills/*/skill.json`.

## Unreleased

### Added

- Add a schema-validated, packaged `v0.5.0` provenance receipt that records the
  release commit, successful Package workflow, artifact digests, and completed
  GitHub attestation verification without treating the receipt as a signature.
- Add the v0.6 verified community intake plan, completion matrix, and milestone.
- Add v0.6 P1 quarantined community intake for directories, ZIP files, and TAR
  files with no-execution staging, bounded resources, portable path checks,
  binary and encoding rejection, cleanup, scanner integration, and a strict
  machine-readable report contract.
- Add v0.6 P2 deterministic community intake receipts with portable source,
  inventory, scanner, policy, finding, exception, maintainer-decision, and
  context-manifest bindings plus fresh stale-evidence verification.
- Add v0.6 P3 deterministic community review packets, issue-ready summaries,
  exact-bound independent domain and safety decisions, public-safe adoption
  reports, declared-domain coverage, role separation, and aggregate status that
  never authorizes automatic maturity promotion, plus bounded external evidence
  loading and a canonical non-signature digest helper.

### Changed

- Mark v0.5 as released and verified across the generated status, website,
  roadmap, notes, and completion contracts while keeping comparative evidence
  and maturity-promotion gates closed.
- Validate published release manifests as immutable snapshots after release and
  update GitHub workflow actions to their current Node 24-compatible majors.

## v0.5.0 - 2026-07-14

### Added

- Add a generated, packaged v0.5 release-status contract that summarizes
  compatibility, verified context, MCP, benchmark, review, and security
  evidence while keeping comparative, promotion, and pre-release tag-provenance
  gates explicitly closed or pending.
- Add a 72-run MCP evidence plan across Codex and Claude Code, three public-safe
  tasks, four isolated conditions, and three trials, with exact installed MCP
  package and contract locks, preflight protocol diagnostics, and separate
  MCP-versus-baseline and MCP-versus-skill publication gates.
- Add v0.5 P3 Trust Policy Packs with a separately versioned packaged baseline,
  explicit rule enablement, monotonic severity overrides, digest-bound and
  expiring reviewed exceptions, scanner/context provenance receipts, and
  fail-closed policy loading outside contributed packages.
- Enforce exact MCP tool and argument allowlists in server startup, doctor, and
  protocol tests; exclude private site-policy inputs, MCP logging, and raw
  argument reflection from the public server contract.
- Add a canonical packaged MCP client contract, deterministic Codex and Claude
  Code configuration examples, and generated onboarding documentation.
- Add `hpc-skill doctor` for Python, package metadata, registry schema, package
  data, context-digest, client-contract, optional SDK, and in-memory protocol
  diagnostics, with strict MCP mode and JSON output.
- Smoke-test core-only and full-MCP wheel installs outside the source checkout,
  including verified context retrieval through the official SDK protocol.
- Add deterministic verified context bundles for all registry-declared skill
  artifacts, with bounded UTF-8 content, file/skill/bundle SHA-256 integrity,
  registry-index binding, security-scan provenance, fail-closed generation,
  packaged-wheel access, and read-only MCP resources.
- Start the v0.5 read-only MCP surface with six closed-domain registry tools,
  optional official SDK v1 support, explicit safety annotations, packaging,
  protocol tests, and CI smoke coverage.
- Add the v0.5 trusted agent distribution plan and MCP safety contract.

### Changed

- Upgrade the generated Pages registry into an operational explorer with
  release-readiness gates, collection shortcuts, responsive table/card views,
  sorting, shareable URL filters, and bounded mobile result expansion.
- Prepare package, citation, release notes, completion matrix, wheel smoke tests,
  and immutable manifest metadata for the `v0.5.0` release.

## v0.4.0 - 2026-07-13

- Start the v0.4 P0 evidence foundation with a versioned 54-run Codex and
  Claude Code campaign, explicit per-run and total budget contracts, resumable
  cost accounting, and exact-model paid-run gates.
- Add a generated public evidence dashboard that withholds comparative ranking
  until results have two independent blinded reviewers, digest-verified public
  artifacts, no pending reviews, and at least three paired trials.
- Add a v0.4 completion matrix, roadmap, milestone, CI checks, and tests that
  distinguish campaign readiness from real measured agent evidence.
- Add the P1 real-evidence campaign control plane with clean-commit and exact-model
  locks, seeded balanced execution waves, resumable next-wave commands, budget
  stop conditions, and strict finalized-staging import audits.
- Add the P2A evidence-backed maturity review workflow with release-scoped
  source bundles, machine-checkable promotion blockers, installed CLI review
  commands, generated registry status, a reviewer packet, and a static dashboard.

## v0.3.0 - 2026-07-13

- Add a deterministic skill-quality audit with ten reviewable workflow
  dimensions, bounded evidence bonuses, benchmark-aware release priorities,
  a versioned JSON Schema contract, generated maintainer reports, and non-threshold CI
  freshness checks.
- Deepen `gpu-sanity-check`, `job-failure-triage`, and `slurm-submit-job` with
  explicit prerequisites, evidence interpretation, resource impact, failure
  handling, cleanup, site boundaries, read-only review helpers, and expanded
  static/fixture benchmark coverage.
- Deepen `slurm-pending-reason-triage`, `mpi-hello-and-benchmark`, and
  `quota-and-filesystem-triage` with offline snapshot and log reviewers,
  temporary MPI build cleanup, bounded storage evidence, and executable
  synthetic benchmark fixtures.
- Close the remaining tier-1 agent-evidence quality gaps across Slurm OOM,
  output-log, QOS/account, shared-permission, and IOR/MDTest workflows with
  offline evidence reviewers, fail-closed report handling, true no-write
  plan-only behavior, bounded storage smoke parameters, and positive/negative
  process-level regression coverage.
- Add a read-only site-adapter resolver, ship complete public policy in registry
  index contract `0.2.0`, and expose mapped, compatible-unmapped, and
  incompatible outcomes to installed CLI and agent consumers.
- Add tag-only GitHub/Sigstore build provenance for release manifests, source
  distributions, and wheels through `actions/attest@v4`.
- Add a blinded agent benchmark review and scoring MVP with digest-bound review
  packets, two-reviewer validation, disagreement reconciliation, redaction and
  tamper gates, and public-safe staged result finalization.
- Start the v0.3 security foundation with an installable community skill
  scanner, structured JSON/SARIF reports, prompt-injection and dangerous-action
  rules, manifest risk cross-checks, agent adoption guidance, and CI gating.
- Treat published release manifests as immutable historical snapshots while
  reserving worktree checksum comparison for explicit release preparation.
- Fix GitHub post-launch milestone verification to use a GET request instead of
  accidentally invoking the create-milestone endpoint.
- Add a six-run v0.3 Codex/Claude smoke calibration with executable/model
  preflight, condition-isolated bulk materialization, resumable campaign status,
  and a bounded path to the full repeated-trial benchmark.

## v0.2.0 - 2026-07-10

- Add the v0.2 Evidence Pilot for Codex and Claude Code with six public-safe
  tasks, condition-scoped context isolation, task/plan/result schemas, a
  54-run calibration matrix, and an explicit paid-execution gate.
- Add repeated-trial agent benchmark aggregation with macro task scores,
  terminal failure rates, confidence intervals, cost/time/token metrics,
  paired skill lift, and blinded evaluator provenance.
- Add static and public-safe fixture benchmarks for 15 representative skill
  workflows and include benchmark freshness checks in local and GitHub CI.
- Add productization sprint improvements: structured `hpc-skill validate --json`
  output, `hpc-skill check` and `hpc-skill new` contributor shortcuts,
  richer skill scaffolds, CLI discovery filters, and multi-filter static
  catalog search.
- Add a scientific simulation workflows seed skill for issue #12, covering
  plan-only run packets, input checks, reproducibility notes, scheduler context,
  log triage, and post-processing review for common HPC simulation software.
- 97 seed HPC skills are now included in the current registry baseline.
- Start `v0.2.0` reviewed-skill pilot development.
- Add `tools/review_packet.py` for generating and checking the reviewed-skill
  pilot packet from the current registry.
- Add `docs/REVIEW_PACKET_v0.2.0.md` with reviewer routing, suggested labels,
  candidate evidence, and maturity promotion gates.
- Add `docs/RELEASE_NOTES_v0.2.0.md` and `registry/releases/v0.2.0.json` as
  the current development release artifacts while preserving the published
  `v0.1.0` snapshot.
- Update local and GitHub validation to check the current `v0.2.0` release
  manifest and review packet.
- Add a Slurm output-log triage seed skill for read-only `sacct`, optional
  `scontrol`/`squeue`, stdout/stderr filename patterns, working-directory,
  path, file-size, tail, and log-signal evidence around missing, empty, or
  misplaced Slurm logs.
- Add a Slurm node-failure triage seed skill for read-only `sacct`, optional
  `scontrol`/`squeue`/`sinfo`, unavailable-node reason, node state, and log
  evidence around `NODE_FAIL`, `BOOT_FAIL`, launch failures, lost tasks, and
  support handoff.
- Add a Slurm time-limit triage seed skill for read-only `sacct`, optional
  `scontrol`/`seff`, and log evidence around `TIMEOUT`, walltime exhaustion,
  scheduler signals, checkpoint cadence, slow array tasks, and workflow retry
  choices.
- Add a file descriptor limit triage seed skill for read-only `ulimit`,
  `/proc` limits, optional `lsof`, fd count, and log evidence around `EMFILE`,
  `Too many open files`, workflow fan-out, data loaders, and many-small-file
  workloads.
- Add a BLAS/OpenMP thread-control seed skill for read-only environment
  reports, optional Python threadpool metadata, and reviewed export blocks for
  OpenMP, oneMKL, OpenBLAS, BLIS, vecLib, NumExpr, R, and Julia thread pools.
- Add a Slurm maintenance reservation triage seed skill for read-only `squeue`,
  `sinfo`, optional `scontrol`, and review guidance around maintenance windows,
  advanced reservations, drained nodes, down partitions, and unavailable
  resources.
- Add a shared project permissions triage seed skill for read-only user/group,
  path traversal, `stat`, optional `namei`, optional `getfacl`, and log evidence
  around shared directory access and ACL failures.
- Add a node-local scratch staging seed skill for capacity evidence, secure
  `mktemp -d` work directories, stage-in/stage-out logs, and marker-guarded
  cleanup around `TMPDIR`/`SLURM_TMPDIR` style temporary storage.
- Add a Slurm array retry planning seed skill for converting failed array-task
  accounting into a compact retry range, optional manifest row review, and
  guarded `sbatch --array` retry command.
- Add a Slurm OOM memory triage seed skill for read-only `sacct`, optional
  `scontrol`/`seff`, and log evidence around `OUT_OF_MEMORY`, killed workers,
  cgroup memory limits, and follow-up memory request review.
- Add a CMake HPC build preflight seed skill for capturing compiler, MPI,
  module, build-directory, test, and install-prefix assumptions before guarded
  CMake configure/build/test/install phases.
- Add a Lustre striping layout planning seed skill for read-only `lfs`
  evidence, review-only `setstripe` planning, and site policy checks before
  changing data-intensive workflow layouts.
- Add a Darshan I/O profile analysis seed skill for turning existing Darshan
  logs into parser output, optional summary commands, and review notes for
  POSIX, MPI-IO, HDF5, and PnetCDF access patterns.
- Add a parallel HDF5 and NetCDF preflight seed skill for MPI-IO wrapper,
  build-configuration, and tiny smoke-test planning.
- Add a Slurm QOS and account limit triage seed skill for read-only
  association, QOS, fairshare, and pending reason evidence.
- Add a Slurm preemption and requeue seed skill for signal-aware jobs,
  restart-safe checkpoint state, and operator-reviewed manual requeue decisions.
- Add an MPI fabric diagnostics seed skill for collecting MPI, UCX,
  libfabric, Open MPI MCA, PMIx, and tiny communication probe evidence.
- Add a Slurm GPU binding diagnostics seed skill for collecting per-task
  `CUDA_VISIBLE_DEVICES`, Slurm GPU variables, and optional vendor telemetry.
- Add a hybrid MPI/OpenMP on Slurm seed skill for aligning MPI task shape,
  `cpus-per-task`, OpenMP thread settings, and CPU binding evidence.
- Add a license-aware Slurm job seed skill for planning `--licenses` requests,
  visible license evidence, and guarded licensed application dry-runs.
- Add an MPI rank binding diagnostics seed skill for collecting Slurm task
  placement, CPU affinity, and topology evidence from small MPI probe jobs.
- Add a Parsl on Slurm seed skill with bounded SlurmProvider and
  HighThroughputExecutor launch planning plus a tiny Python app smoke workflow.
- Extend registry artifact validation to catch stale public collection and site
  adapter counts in launch and proposal materials.
- Add a GitHub Pages homepage command generator and post-launch homepage URL
  check for confirming the published repository links to its generated site.
- Add a post-launch GitHub verification tool for checking published repository
  metadata, labels, milestones, starter issues, workflows, Pages, rulesets, and
  releases.
- Add a proposal evidence report generator for owner handoffs, open-source
  review packets, and ecosystem sponsor discussions.
- Add a reviewed-skill pilot starter issue for routing the first seed skill
  maturity reviews from the local review candidate report.
- Add a review candidate report generator for ranking seed skills that are
  ready for first domain review routing and `reviewed` maturity pilot planning.
- Add a launch evidence report generator for maintainer handoff, launch issues,
  and open-source proposal evidence without taking networked action.
- Add an object storage transfer seed skill with rclone dry-run copy planning,
  guarded sync mode, optional AWS CLI S3 sync planning, bounded transfer
  settings, and validation logs.
- Add a TensorFlow multi-worker on Slurm seed skill with TF_CONFIG launch
  planning, worker index mapping, strategy initialization, and a tiny
  distributed tensor reduction smoke test.
- Add a Hugging Face Accelerate on Slurm seed skill with dry-run launch
  planning, explicit multi-node launch arguments, and a tiny Accelerate tensor
  collective smoke test.
- Add a JAX distributed on Slurm seed skill with dry-run launch planning,
  accelerator visibility checks, distributed initialization, and tiny compiled
  computation smoke-test examples.
- Add a GitHub owner checklist for confirming repository ownership,
  permissions, maintainer queues, public-safety review, and launch decision
  records before networked publication.
- Add a public launch packet that summarizes local readiness, GitHub owner
  prerequisites, launch sequence, outreach targets, and success criteria for
  the first open-source publication.
- Add a public-doc-backed draft NERSC Perlmutter site adapter, covering Slurm
  constraints, QOS notes, Lmod, scratch storage, Globus/DTN transfer guidance,
  and container adaptation notes from public NERSC documentation.
- Add an Open OnDemand Batch Connect skill for reviewable Slurm-backed portal
  app skeletons, and extend safety auditing to cover `.erb` templates.
- Prepare the seed registry for public GitHub launch, including repository
  metadata, labels, rulesets, issue templates, pull request templates, Pages
  publishing, seed community issues, and governance docs.
- Add the first `facility-ops` collection and a read-only Slurm usage reporting
  skill for support teams.
- Add a read-only Slurm node-health triage skill for facility operations.
- Add a read-only module-tree health check skill for software-stack and
  facility operations support.
- Add a training and onboarding collection with a workshop preflight and reset
  checklist skill.
- Add maturity review guidance and issue template for promoting seed skills.
- Add adopter playbook and adoption report issue template for public pilot
  feedback.
- Add local launch readiness audit for GitHub publishing preparation.
- Add support and citation metadata for public project use.
- Add review routing guidance and CODEOWNERS launch checklist for maintainer
  assignment.
- Add triage runbook and starter labels for public issue and pull request
  intake.
- Add skill lifecycle guidance for moving community requests through seed,
  review, field testing, maintenance, and deprecation.
- Add ecosystem entry points to the generated static site for adopters,
  contributors, site adapters, integrations, safety review, and RFCs.
- Add GitHub Discussion category forms and setup guidance for adoption, skill
  coverage, site adapters, review process, and integrations.
- Add GitHub milestone metadata and command generator for launch, reviewed-skill
  pilot, integration, adapter, and ecosystem backlog planning.
- Add launch readiness checks for GitHub Discussion forms and milestone
  metadata.
- Add integration guide, integration request template, and starter label for
  downstream registry consumers.
- Add a read-only Slurm efficiency report skill for completed job resource
  review.
- Add a Slurm job dependency chain skill for small multi-stage workflows.
- Add a read-only Slurm pending reason triage skill for queue wait diagnosis.
- Add a PBS submit job skill and scheduler basics collection for OpenPBS/PBS Pro
  starter workloads.
- Add an LSF submit job skill for IBM Spectrum LSF CPU, MPI, and GPU starter
  workloads.
- Add an HTCondor submit job skill for high-throughput single-job, many-task,
  and GPU starter workloads.
- Add a Grid Engine submit job skill for SGE/UGE CPU, parallel environment, and
  array starter workloads.
- Add an Apptainer MPI on Slurm skill for hybrid and bind-model containerized
  MPI launch patterns.
- Add a VS Code Tunnel on Slurm skill for policy-aware IDE sessions on compute
  allocations.
- Add an RStudio on Slurm skill for policy-aware Posit or RStudio sessions on
  scheduled compute allocations.
- Add a Streamlit on Slurm skill for policy-aware Python data apps and AI demos
  on scheduled compute allocations.
- Add a TensorBoard on Slurm skill for policy-aware training monitors on short
  compute allocations.
- Add an IOR and MDTest storage smoke skill for small, policy-aware filesystem
  benchmark evidence on Slurm.
- Expand the technical roadmap with current registry baseline, GitHub launch
  gates, integration tracks, maturity evidence, and open ecosystem milestones.
- Add a NAMD on Slurm skill for molecular dynamics jobs with CPU/GPU layout and
  restart planning.
- Add a CP2K on Slurm skill for MPI/OpenMP electronic-structure and molecular
  simulation jobs.
- Add an Rscript on Slurm skill for batch R workloads with explicit package
  library and output controls.
- Add a Julia on Slurm skill for batch Julia workloads with explicit depot,
  project, and thread settings.
- Add a MATLAB batch on Slurm skill for non-interactive MATLAB workloads with
  explicit logging and license notes.
- Add a mpi4py on Slurm skill for Python MPI workloads with matching MPI module
  and Python environment checks.
- Add a Dask Jobqueue on Slurm skill with dry-run worker job script review and
  bounded worker scaling.
- Add a Ray on Slurm skill with explicit head node selection, resource bounds,
  launch records, and smoke test controls.
- Add a `containers` collection for Apptainer builds, runtime execution, GPU
  checks, data staging, checksums, and reproducible run capture.
- Add an `ai-hpc` collection for distributed AI launch, validation,
  troubleshooting, data staging, and reproducibility workflows.
- Add a BLAST on Slurm skill with local database creation, bounded output
  controls, and a tiny FASTA smoke test.
- Add a Quantum ESPRESSO on Slurm skill with MPI sizing, pseudopotential checks,
  scratch paths, restart planning, and a PWscf input template.
- Add a CWL on Slurm skill with cwltool cache, output, temporary directory, and
  smoke-test controls.
- Add a WDL on Slurm skill with miniwdl input, run directory, output JSON, and
  smoke-test controls.

## v0.1.0 - Released

Initial public seed release.

### Added

- 96 seed HPC skills covering Slurm, PBS/OpenPBS, LSF, HTCondor, Grid Engine,
  job arrays, array retry planning, dependency chains, pending reason and maintenance reservation triage, monitoring, resource
  estimation, QOS/account limit evidence, output-log triage, OOM memory triage, time-limit triage, node-failure triage, efficiency review, license-aware jobs, failure triage, checkpoint/restart,
  preemption and requeue-safe restart behavior,
  interactive sessions, Open OnDemand Batch Connect templates, notebooks, RStudio, IDE tunnels, OpenMP
  placement, BLAS/OpenMP thread pool control, file descriptor triage, storage triage, shared project permissions and ACL triage, node-local scratch staging, Python/R/Julia/MATLAB software environments,
  CMake build preflight, parallel HDF5/NetCDF preflight, Darshan I/O profile
  analysis, Lustre striping layout planning,
  TensorBoard, Streamlit, Ray, Dask Jobqueue, Parsl, JAX, Hugging Face Accelerate, TensorFlow, mpi4py, containers, containerized MPI, Spack, EasyBuild, object storage, data movement, node-local scratch staging,
  storage smoke benchmarks, CWL/WDL, workflow engines, GPU binding diagnostics, MPI fabric diagnostics, MPI/GPU diagnostics,
  MPI rank binding diagnostics, hybrid MPI/OpenMP layouts,
  AI/HPC launches, bioinformatics workflows including local BLAST+, molecular dynamics including NAMD,
  electronic-structure and quantum chemistry including CP2K, CFD, weather
  workloads, read-only facility operations, and training onboarding.
- 12 curated collections: `core-hpc`, `scheduler-basics`, `software-stacks`,
  `containers`, `workflow-engines`, `data-movement`, `ai-hpc`,
  `gpu-mpi-performance`, `bioinformatics-workflows`, `simulation-workflows`,
  `facility-ops`, and `training-onboarding`.
- 2 site adapters: `example-campus-cluster` and the public-doc-backed draft
  `nersc-perlmutter-public`.
- Machine-readable registry index and health reports.
- Installable `hpc-skill` CLI for discovery, validation, scaffolding,
  collections, site adapters, and registry health.
- Static site generation for GitHub Pages.
- JSON schemas for skills, collections, and site adapters.
- GitHub Actions validation, Pages publishing, Dependabot, issue templates,
  pull request templates, starter labels, repository metadata, and starter
  `main` branch ruleset configuration.
- Seed community issues and command generators for launching the public
  contribution queue.
- Governance, safety, release, maintainer handoff, authoring, publishing, and
  community launch documentation, plus a technical roadmap for public launch,
  registry growth, integrations, and ecosystem stewardship.

### Safety Notes

- User-facing examples default to dry-run, read-only, plan-only, or explicitly
  bounded behavior where practical.
- Medium-risk skills document resource impact, output volume, or side effects.
- Site adapters must contain only public, non-sensitive local policy.
- High-risk or facility-operations skills require explicit maintainer review
  before promotion beyond seed maturity.
