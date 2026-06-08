# Maturity Review

Maturity review is the process for moving a skill from `seed` to `reviewed`,
`field-tested`, or `maintained`.

The goal is not to make every skill perfect. The goal is to make evidence,
scope, risk, and ownership visible enough that users know how much confidence
to place in the skill.

## Maturity Levels

- `seed`: the skill has a manifest, README, examples, references, and passes
  static validation.
- `reviewed`: a maintainer with relevant domain knowledge has checked scope,
  safety, portability, examples, and references.
- `field-tested`: someone other than the original author has exercised the
  skill in a real HPC environment and recorded public, non-sensitive notes.
- `maintained`: the skill has an active owner, current references, and a review
  path for future changes.

Promotion should happen in a pull request that updates `skill.json`, generated
registry files, and supporting evidence.

## Evidence By Level

To promote to `reviewed`, include:

- The skill id and current maturity.
- Reviewer name or GitHub handle.
- Domain area: scheduler, storage, software stacks, workflows, AI/HPC,
  bioinformatics, simulation, facility operations, or training.
- Confirmation that examples are safe for shared HPC systems.
- Confirmation that assumptions, inputs, outputs, and risks are visible.
- Confirmation that public references are current enough for seed adoption.
- `make check` output from the pull request.

To promote to `field-tested`, also include:

- Public description of the environment type, such as campus Slurm cluster,
  training cluster, cloud HPC environment, or lab-managed cluster.
- Scheduler, container runtime, module system, and storage assumptions that are
  safe to disclose.
- What was run or reviewed.
- What changed because of the test.
- Any site-specific details that should move to a site adapter instead of the
  core skill.

To promote to `maintained`, also include:

- Active maintainer or maintainer group.
- Expected review cadence or upstream reference check.
- Ownership for examples and domain-specific behavior.
- Any known gaps that should remain open issues.

## Review Questions

- Does the skill solve one clear task?
- Is the risk level accurate for the most powerful example or recommendation?
- Are hidden site assumptions called out?
- Are examples conservative about resources, data movement, and shared systems?
- Are private hostnames, usernames, allocation names, tokens, internal project
  identifiers, security procedures, and private paths absent?
- Does the skill belong in the current collections?
- Should any local policy be represented as a site adapter instead?
- Does the reviewer have the right domain context for the risk level?

## Pull Request Expectations

A maturity promotion pull request should:

- Update `maturity` in `skills/<skill-id>/skill.json`.
- Update the README if the review uncovered clearer assumptions or safety
  notes.
- Refresh generated files with:

  ```bash
  python3 tools/build_index.py
  python3 tools/build_health.py
  python3 tools/build_compatibility.py
  make check
  ```

- Link the maturity review issue.
- Include only public, non-sensitive evidence.

## When To Use Safety Review Instead

Open a safety review issue before maturity promotion when the skill:

- Touches facility operations, quotas, accounting, node health, or shared
  software environments.
- Encourages cleanup, deletion, publication, archive, or transfer actions.
- Could reveal private operational policy.
- Changes risk labels, schemas, validation behavior, or high-risk guidance.

Maturity review and safety review can happen together, but safety concerns
should be resolved before a skill is promoted.
