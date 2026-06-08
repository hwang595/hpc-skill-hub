---
name: Safety review
about: Request review for risk, privacy, shared-system impact, or high-risk skill behavior
title: "Safety review: "
labels: ["safety-review"]
---

## Area To Review

Which skill, example, tool, site adapter, workflow, or document needs review?

## Risk Type

- [ ] Allocates compute or GPU resources.
- [ ] Moves, publishes, deletes, overwrites, or archives data.
- [ ] Changes software environments, modules, containers, or build outputs.
- [ ] Mentions facility operations, admin behavior, quotas, accounting, or node
      health.
- [ ] Could expose private hostnames, paths, allocations, users, datasets, or
      security procedures.

## Expected Behavior

What should be safe, bounded, reversible, or clearly disclosed?

## Evidence

Link the relevant file, pull request, public documentation, or command output.

## Review Needed

What maintainer expertise is needed? For example: Slurm, storage, security,
software stacks, AI/HPC, bioinformatics, simulation, or facility operations.
