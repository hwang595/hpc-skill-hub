# Skill Authoring Guide

This guide turns the registry format into a repeatable authoring workflow for
new HPC skills.

## Authoring Loop

1. Propose the task with a skill request issue.
2. Create a scaffold:

   ```bash
   python3 tools/hpc_skill.py scaffold skill my-new-skill --category education --tool bash
   ```

3. Replace scaffold text with task-specific assumptions, examples, risks, and
   references.
4. Validate one skill while iterating:

   ```bash
   python3 tools/hpc_skill.py validate --skill my-new-skill
   ```

5. Rebuild generated registry artifacts:

   ```bash
   python3 tools/build_index.py
   python3 tools/build_health.py
   python3 tools/build_compatibility.py
   ```

6. Run the full local gate:

   ```bash
   python3 tools/hpc_skill.py validate
   make check
   ```

7. Open a pull request and explain target users, expected environment, and risk
   level.

## Scope Rules

Keep each skill small enough to review:

- One recurring HPC task per skill.
- One primary scheduler, runtime, workflow engine, or tool family.
- Clear boundaries between portable guidance and site-specific policy.
- Examples that a user can copy, inspect, and adapt without hidden state.

Prefer separate skills when a topic crosses a risk boundary. For example,
read-only job accounting and account administration should not live in the same
skill.

## Manifest Guidance

Use `skill.json` to make the skill discoverable and reviewable:

- `summary`: one sentence about the task.
- `description`: what the skill helps users do and when to use it.
- `categories`: choose the smallest accurate set.
- `tags`: include tool names and user-facing search terms.
- `risk_level`: match the most powerful example or action in the skill.
- `maturity`: use `seed` until an independent reviewer has tested the skill.
- `tools`: list commands users must have available.
- `inputs` and `outputs`: describe what users provide and what they should see.
- `tests`: start with static checks, then add dry-run, manual, or integration
  checks as the skill matures.

## README Structure

Every skill README should include:

- When to use the skill.
- Assumptions about scheduler, modules, containers, storage, accounts, or
  network access.
- Step-by-step usage with placeholders for site-specific values.
- Safety notes about cost, resource allocation, data movement, or shared
  systems.
- Success criteria that a user can verify.
- Troubleshooting notes for common failure modes.

Avoid long tutorials inside a skill. Link to primary documentation and keep the
skill focused on the operational path.

## Example Rules

Examples should be conservative and inspectable:

- Use short wall times and modest resource requests.
- Use placeholders such as `<account>`, `<partition>`, `<project>`, and
  `<dataset>`.
- Write outputs to user-owned working directories.
- Print enough context for users to understand success or failure.
- Avoid private hostnames, usernames, allocation names, tokens, and internal
  project identifiers.
- Avoid admin-only actions unless the skill is explicitly high risk and reviewed
  by a domain maintainer.

## Risk Levels

- `low`: read-only diagnostics, templates, explanation, or local validation.
- `medium`: submits jobs, transfers data, writes user-owned files, or consumes
  shared resources.
- `high`: changes shared environments, service state, quotas, accounting,
  node availability, security boundaries, or admin-controlled systems.

When unsure, choose the higher risk and explain why in the README. Risk labels
are a review tool, not a warning label to hide complexity.

## Maturity Levels

- `seed`: initial, reviewable contribution.
- `reviewed`: reviewed by a maintainer for portability, safety, and clarity.
- `field-tested`: tested on at least one real HPC environment by someone other
  than the original author.
- `maintained`: has an active maintainer, passing examples, and current
  references.

Promotion should happen in a pull request so the evidence is visible.

## Review Rubric

Reviewers should check:

- Does the skill solve one clear task?
- Are hidden site assumptions called out?
- Are examples safe for shared HPC systems?
- Is the risk level accurate?
- Are references public and useful?
- Does `make check` pass after generated files are refreshed?
- Should the skill be added to an existing collection or start a new one?
- Does it need a site adapter note instead of changing portable behavior?

## Common Anti-Patterns

- Combining onboarding, debugging, and production automation in one skill.
- Hard-coding one center's private policy into a core skill.
- Using examples that allocate large resources by default.
- Listing tools in prose but not in `skill.json`.
- Shipping a README without a concrete success check.
- Treating a workflow engine profile as portable when it depends on local
  partitions, accounts, storage, or modules.

## Collection Placement

After adding a skill, decide whether it belongs in a collection:

- `core-hpc`: scheduler basics, modules, debugging, storage, onboarding.
- `software-stacks`: modules, containers, compilers, package managers.
- `workflow-engines`: workflow execution patterns and scheduler integration.
- `training-onboarding`: teaching workflows, workshop setup, and new-user
  onboarding.
- `data-movement`: transfer, staging, checksums, and data lifecycle tasks.
- `gpu-mpi-performance`: GPU, MPI, threading, profiling, and scaling checks.

If a skill does not fit, leave it uncollected during review and open an issue to
discuss a new collection.
