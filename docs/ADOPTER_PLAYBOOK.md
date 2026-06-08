# Adopter Playbook

This playbook helps HPC centers, research groups, tool maintainers, and
instructors try HPC Skill Hub without committing to a fork or a long migration.

The safest first adoption is a small public pilot: use existing seed skills,
record what worked, contribute one public site adapter or skill request, and
avoid moving private cluster policy into the core registry.

## Adoption Tracks

Choose one primary track for the first pilot.

| Track | First useful contribution | Good evidence |
| --- | --- | --- |
| HPC center | Public site adapter | Public docs links, partitions, storage classes, container notes, and support boundaries. |
| Research group | Domain skill request or draft skill | Tool assumptions, small smoke test, common failures, and safe scheduler defaults. |
| Tool maintainer | Integration skill | Scheduler profile, container guidance, validation command, and upstream references. |
| Instructor | Training/onboarding skill or collection feedback | Workshop preflight notes, learner failure modes, and short-running examples. |

## 30 Day Pilot

Use the registry internally before asking users to depend on it.

1. Pick one collection, such as `core-hpc`, `software-stacks`,
   `training-onboarding`, or `facility-ops`.
2. Run `make check` locally to confirm the repository is healthy.
3. Review three to five skills against local public documentation.
4. Open skill requests for missing workflows.
5. Open a site adapter request if public local policy would help users adapt
   core skills.
6. Record private findings outside the public repository and summarize only
   public-safe lessons in issues.

## 60 Day Pilot

Turn the first review into reusable public artifacts.

1. Create a draft site adapter or draft skill pull request.
2. Add public documentation links and placeholders for accounts, partitions,
   users, and paths.
3. Run:

   ```bash
   python3 tools/hpc_skill.py validate
   make check
   ```

4. Ask for domain review from the relevant maintainer area.
5. Open safety review for any facility operations, cleanup, accounting, quota,
   node health, or shared software-stack concerns.
6. Keep site-specific details in the adapter, not in core skills.

## 90 Day Pilot

Decide whether to promote, expand, or pause adoption.

1. Open maturity review for skills that have real review evidence.
2. Promote only when public evidence supports the requested maturity.
3. Identify one maintainer or reviewer for the adopted collection or adapter.
4. Write down gaps as skill requests instead of one-off local patches.
5. Share an adoption report issue with public-safe outcomes and blockers.

## Adoption Report

An adoption report should answer:

- Which track did you try?
- Which collection, skill, or adapter did you use?
- What worked without local modification?
- What required a site adapter?
- Which assumptions were unclear?
- Which examples felt too risky, expensive, or site-specific?
- What public documentation helped reviewers?
- What should the project prioritize next?

Use the adoption report issue template so maintainers can compare feedback
across sites and domains.

## Public-Safe Evidence

Good public evidence:

- Environment type, such as campus Slurm cluster, training cluster, cloud HPC,
  lab-managed cluster, or containerized test environment.
- Public documentation URLs.
- Public partition or queue names when already documented.
- Placeholder paths such as `/project/<project>` or `/scratch/<user>`.
- Redacted command output showing success criteria.

Do not publish:

- Private hostnames, usernames, account names, allocation names, tokens, or
  internal project identifiers.
- Private storage paths, dataset names, support tickets, or incident details.
- Unpublished security, identity-management, quota, accounting, or node
  operations procedures.

## Success Metrics

For a small pilot, useful metrics are:

- Skills reviewed by domain experts.
- Skill requests opened from repeated support questions.
- Public site adapters proposed or merged.
- Maturity reviews opened with public evidence.
- Repeated support questions reduced or turned into reusable skills.
- Workshops or onboarding sessions completed with documented preflight notes.

Do not treat download counts or stars as the main signal during seed stage.
The better signal is whether the registry converts repeated private support
knowledge into public, reviewable, reusable artifacts.
