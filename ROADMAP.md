# Technical Roadmap

This roadmap turns HPC Skill Hub from a seed repository into a public,
reviewable ecosystem for reusable HPC operational knowledge.

## Current Baseline

The seed repository currently includes:

- 97 seed skills.
- 12 curated collections.
- 2 site adapters: 1 example adapter and 1 public-doc-backed draft adapter.
- JSON schemas for skills, collections, site adapters, registry health, and
  release manifests.
- An installable `hpc-skill` CLI for discovery, validation, scaffolding,
  collection browsing, site adapter browsing, and registry health.
- Generated Codex and Claude Code adapter surfaces, plus static and fixture
  benchmark coverage for selected skills.
- An evidence-pilot agent benchmark contract with six public-safe tasks and a
  dry-run 54-run Codex/Claude calibration matrix.
- A blinded review and scoring pipeline with redaction gates, independent
  double scoring, reconciliation, tamper detection, and staged finalization.
- Generated catalog, compatibility, registry health, package data, static site,
  and deterministic release manifest artifacts.
- GitHub metadata for labels, issue templates, discussion templates,
  milestones, workflows, starter rulesets, and seed community issues.
- Published `v0.1.0` through `v0.4.0` registry releases. The `v0.4.0` release
  adds evidence-campaign controls and review infrastructure without promoting
  skills automatically or claiming measured agent lift.

The public GitHub launch is complete. Current development focuses on turning
seed skills into reviewed skills through public-safe evidence and domain
review.

The v0.3 infrastructure is released. Real cross-agent runs, independent
scoring, external adoption evidence, and maturity promotion remain public
follow-up work rather than synthetic CI claims.

## v0.5 Current Development

Status: P0 through P3 are merged through PR #44 on 2026-07-14. P4's
repository-side MCP evidence capability and P5's release-candidate preparation
are complete locally. Merge, authenticated paid runs, independent review, the
release tag, and tag-triggered attestations remain external gates. The v0.5
delivery queue is tracked in issue #40.

v0.5 focuses on trusted agent distribution:

1. Ship a local stdio MCP server with a closed, read-only registry tool set.
2. Package digest-verified skill context so installed agents can inspect full
   workflows without scraping or a source checkout.
3. Generate Codex and Claude Code onboarding plus compatibility diagnostics.
4. Version community-skill trust policy and provenance receipts.
5. Measure an MCP-enabled benchmark condition only after explicit paid-run and
   independent-review authorization.
6. Publish v0.5.0 with immutable manifests and verified attestations.

The MCP surface contains no operational HPC actions. P1 packages only
registry-declared, security-scanned content and rejects stale, missing,
oversized, path-escaping, or blocked inputs. P2 generates reviewable examples
without silently enabling project MCP configuration and validates the exact
capability surface through an in-memory protocol probe. P3 adds a separately
versioned, fail-closed security policy with source-bound review exceptions and
MCP argument allowlists. P4 adds a 72-run MCP evidence contract without
launching paid agents in CI. P5 publishes one generated release-status artifact
that preserves closed external gates and an operational Pages explorer that
makes those gates visible beside the registry. See the
[v0.5 Development Plan](docs/V0_5_PLAN.md).

## v0.4 Released

Status: P0 evidence foundation and P1 campaign control plane merged through
PRs #27 and #28, and the P2A evidence-backed maturity review workflow merged
through PR #29. PR #38 completed release preparation, and `v0.4.0` was
published from commit `cee22c6` on 2026-07-13 with Validate, Package, Pages,
and tag-triggered attestations verified.

v0.4 focuses on evidence and a reviewed registry. Work proceeds in this order:

1. **P0 evidence foundation:** version the repeated cross-agent campaign,
   enforce per-run and campaign budgets, generate a public evidence dashboard,
   and keep comparative output behind machine-checkable publication gates.
2. **P1 real evidence campaign:** run Codex and Claude Code from one clean
   commit with exact models and explicit quota approval, then complete redaction
   and independent blinded review.
3. **P2 reviewed registry pilot:** deepen a bounded candidate set, collect
   public domain and adoption evidence, and promote maturity only through the
   existing lifecycle contract.
4. **P3 release readiness:** regenerate deterministic artifacts, decide whether
   the evidence gate supports public comparison, and cut `v0.4.0` from a clean
   release commit.

The P0 plan contains 54 paired runs across three tasks, three conditions, three
trials, and two agents. Its USD 40.50 maximum is an authorization ceiling, not
a spending target. CI validates the campaign but never launches paid agents.
See the [v0.4 Completion Matrix](docs/V0_4_COMPLETION.md).

The release contains no paid agent runs, comparative ranking, or
maturity promotion. The benchmark publication gate remains closed. Five
static-ready skills are pinned to public maturity-review issues for independent
post-release review, and all remain `seed` until those approvals exist.

## v0.3 Release Scope

Status: released in `v0.3.0` as an infrastructure and contract release.

The release establishes a security foundation for community-contributed and
agent-consumed skills:

- Scan untrusted skill packages before loading their instructions into Codex,
  Claude Code, or another agent context.
- Emit stable text, JSON, and SARIF findings for CI and downstream portals.
- Detect prompt-injection, concealed behavior, dangerous execution,
  persistence, ambient credential access, package-boundary violations, and
  understated risk declarations without executing skill content.
- Preserve published release manifests as immutable evidence.

The v0.3 release includes the community skill scanner, six-run Codex/Claude
smoke harness, digest-bound blinded scoring, a read-only skill/site-adapter
resolution contract, registry index contract `0.2.0`, deterministic
skill-quality reporting, deeper tier-1 skill evidence, and tag-time GitHub
artifact provenance. The real-agent evidence track remains separate: run from
a clean commit with exact models and explicit quota approval, complete
independent reviews, and publish only public-safe reviewed results. See
[v0.3 Completion Matrix](docs/V0_3_COMPLETION.md).

## Phase 0: Seed Repository

Status: largely complete locally.

Technical gates:

- Define the skill package format and JSON schema.
- Add the first curated batch of practical HPC skills.
- Add safety, validation, release, and generated-registry checks.
- Add contribution, security, support, governance, review, and release docs.
- Keep examples portable, bounded, and directly adaptable on real clusters.
- Keep `make check` as the local release gate.

Exit evidence:

- `python3 tools/launch_readiness.py --owner <owner> --run-check` reports only
  external GitHub setup warnings.
- `registry/index.json`, `docs/SKILL_CATALOG.md`,
  `docs/REGISTRY_HEALTH.md`, `docs/COMPATIBILITY.md`, package registry data,
  and `registry/releases/v0.1.0.json` are current.

## Phase 1: Public GitHub Launch

Status: complete for the seed repository.

Technical gates:

- Create the public GitHub repository.
- Push `main` and confirm `Validate` and `Package` workflows pass.
- Apply repository metadata, labels, branch ruleset, and milestones from
  `.github/`.
- Enable GitHub Pages from Actions and publish the generated registry site.
- Enable Discussions and create the categories that match
  `.github/DISCUSSION_TEMPLATE/`.
- Open the seed community issues for domain reviewers, next-wave skills, public
  site adapters, and community calls.

Exit evidence:

- `origin` points at the public repository.
- GitHub Actions are green on `main`.
- Pages is reachable.
- Launch issue queue is visible.
- CODEOWNERS has real maintainer handles or documented placeholders.

## Phase 2: Usable Registry

Status: released in `v0.2.0`; adoption and maturity outcomes remain open.

Technical gates:

- Improve search over skill manifests, tags, categories, schedulers, tools, and
  risk metadata.
- Keep generated compatibility tables for schedulers, containers, workflow
  engines, software stacks, and domain collections.
- Expand site adapters so HPC centers can publish public policy mappings
  without forking core skills.
- Add field evidence to selected seed skills through adoption reports.
- Promote selected skills from `seed` to `reviewed` only after domain review.
- Generate and keep current a reviewed-skill pilot packet for reviewer routing,
  issue labels, promotion gates, and public evidence checklists.
- Run the agent benchmark calibration with exact model versions and reviewed,
  public-safe result records before making comparative effectiveness claims.

Exit evidence:

- At least three external adoption reports are filed.
- At least one public site adapter is reviewed or contributed by a real site or
  training environment.
- At least five skills complete maturity review and move to `reviewed`.
- `docs/REVIEW_PACKET_v0.2.0.md` is current and linked from the release notes.
- The calibration report includes paired baseline and skill-enabled trials, or
  the release notes explicitly defer real agent execution without claiming
  measured skill lift.

## Phase 3: CLI And Developer Experience

Status: basic CLI exists.

Technical gates:

- Extend `hpc-skill validate` with optional JSON reporting for downstream
  portals, assistants, and CI dashboards.
- Add template rendering for common scheduler scripts and config files without
  hiding resource impact.
- Add local dry-run checks for commands that may be expensive or risky on
  shared systems.
- Add contributor tooling for skill request intake, reviewer routing, and
  release-note generation.
- Keep registry artifacts stable enough for external consumers.

Exit evidence:

- Downstream tools can consume `registry/index.json` without scraping Markdown.
- Contributors can scaffold, validate, and preview a new skill with one local
  workflow.
- Release owners can cut a deterministic release from a clean checkout.

## Phase 4: Integrations

Status: Codex and Claude Code file-based adapters exist; deeper integrations
and scored cross-agent evidence are in progress.

Priority integration tracks:

- Slurm: batch scripts, accounting, queue inspection, array retry planning,
  dependency chains, maintenance and reservation triage,
  QOS/account limit evidence, output-log triage, OOM memory triage,
  time-limit triage, node-failure triage, license-aware jobs,
  preemption/requeue handling, and optional REST integration.
- Open OnDemand: Batch Connect app templates and user-facing interactive
  workflows.
- Apptainer: image execution, bind mounts, GPU pass-through, MPI launch, and
  reproducibility.
- CMake, Spack, and EasyBuild: scientific software build preflight,
  user-owned install prefixes, stack creation, and module generation.
- HDF5 and NetCDF: parallel I/O build preflight, wrapper evidence, and tiny
  MPI-IO smoke tests.
- Globus and data lifecycle tools: reliable transfer, checksums, staging,
  shared project permissions, node-local scratch, archival, and publication
  handoff.
- Workflow engines: array retry planning, Nextflow, Snakemake, CWL, WDL, Dask,
  Parsl, and Ray.
- Observability: failure triage, output-log triage, QOS/account limit evidence,
  OOM memory and time-limit triage, node-failure triage, efficiency review,
  profiling, Darshan I/O profile analysis, Lustre striping layout planning,
  storage smoke evidence, preemption/requeue evidence, GPU binding diagnostics,
  MPI fabric diagnostics, MPI rank binding diagnostics, hybrid MPI/OpenMP
  layout checks, utilization reports, and training reset checks.

Exit evidence:

- Integration requests can cite a stable manifest contract.
- Each integration track has at least one maintainer or reviewer.
- High-risk integrations have explicit safety review before implementation.

## Phase 5: Open Ecosystem

Status: proposal and governance docs exist; public participation is pending.

Technical gates:

- Recruit maintainership areas for schedulers, storage, containers,
  workflow engines, AI/HPC, bioinformatics, simulation, facility operations,
  training, and registry tooling.
- Publish adapter contribution examples for training clusters, campus clusters,
  national facilities, and cloud HPC environments.
- Add signed releases and provenance for reviewed skills.
- Create a lightweight review board for high-risk or facility-operation skills.
- Encourage public site adapters instead of private forks.

Exit evidence:

- The project has recurring external contributors.
- Reviewed skills cite public evidence and reviewer ownership.
- Site adapters document public local policy without exposing private details.
- The registry is useful both as documentation and as machine-readable input for
  portals, assistants, and workflow tools.

## Skill Coverage Direction

The first wave emphasizes recurring support and onboarding workflows:

- Scheduler basics across Slurm, PBS/OpenPBS, LSF, HTCondor, Grid Engine, and
  failed-array retry planning, including output-log, memory, time-limit, and
  node-failure triage.
- Storage and data movement: scratch, node-local temporary storage, quota,
  shared project permissions and ACLs, file descriptor pressure, staging,
  checksums, rsync, Globus, object storage, archive preparation, Darshan I/O
  profile analysis, Lustre striping layout planning, and IOR/MDTest smoke
  evidence.
- Software stacks: modules, compiler/MPI matrices, CMake build preflight,
  Conda, virtualenv, Spack, EasyBuild, parallel HDF5/NetCDF preflight,
  BLAS/OpenMP thread pools, containers, and reproducible run capture.
- Interactive and teaching workflows: Open OnDemand Batch Connect templates,
  Jupyter, TensorBoard, Streamlit, RStudio, VS Code tunnels, workshop reset
  checks, and language-specific batch jobs.
- AI/HPC: GPU sanity checks, CPU thread-pool control, PyTorch DDP, NCCL,
  DeepSpeed, Ray, Dask, JAX, file descriptor pressure in data loaders,
  Hugging Face Accelerate, TensorFlow, and monitoring.
- Domain workflows: bioinformatics, molecular dynamics, electronic structure,
  CFD, weather, workflow engines including Parsl, MPI, OpenMP, and performance
  evidence, including CMake build preflight, parallel HDF5/NetCDF preflight,
  Darshan I/O profile analysis, and Lustre striping layout planning for
  data-heavy codes.
- Facility support: read-only usage, node, module tree, pending reason,
  maintenance/reservation, OOM memory, time-limit, node-failure, file
  descriptor pressure, shared directory permissions, and efficiency triage.

Future skills should be prioritized when they reduce repeated support tickets,
have public references, can be validated without private cluster access, and
fit a clear reviewer area.

## Design Principles

- Skills should be understandable before they are executable.
- Destructive, expensive, or shared-system actions must be explicit and
  documented.
- Cluster-specific assumptions belong in placeholders or site adapters.
- Examples should teach safe defaults first.
- Generated artifacts should be deterministic and validated in CI.
- The registry should help users move from "it ran once" to reproducible,
  supportable HPC workflows.
