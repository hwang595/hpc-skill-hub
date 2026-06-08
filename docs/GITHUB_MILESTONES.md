# GitHub Milestones

Use milestones to group public launch work, reviewed-skill promotion, adapter
growth, and longer-running ecosystem requests.

Milestone metadata lives in `.github/milestones.json`. It is intentionally
small and stable so maintainers can review the roadmap before applying it to a
public GitHub repository.

## Seed Milestones

| Milestone | Purpose |
| --- | --- |
| `v0.1.0 seed launch` | Publish the first public registry snapshot, generated site, release manifest, and community launch queue. |
| `v0.2.0 reviewed-skill pilot` | Promote the first reviewed skills, collect adoption reports, and recruit domain reviewers. |
| `v0.3.0 integrations and adapters` | Expand site adapters, downstream registry integrations, and compatibility contracts. |
| `ecosystem backlog` | Track longer-running requests that need owners, RFCs, site evidence, or domain review. |

## Create Milestones

After the repository is pushed and `gh` is authenticated, inspect:

```bash
python3 tools/github_milestones.py --repo <owner>/hpc-skill-hub
```

Run the printed commands when they look correct. The command generator does not
mutate GitHub by itself.

## Triage Use

- Put release blockers and final launch tasks in `v0.1.0 seed launch`.
- Put maturity review work and early field-test evidence in
  `v0.2.0 reviewed-skill pilot`.
- Use the reviewed-skill pilot starter issue and
  `python3 tools/review_candidates.py --limit 12` to seed the first batch of
  maturity review work for `v0.2.0 reviewed-skill pilot`.
- Put site adapter and downstream integration work in
  `v0.3.0 integrations and adapters`.
- Put broad requests in `ecosystem backlog` until a maintainer can split them
  into focused issues, RFCs, safety reviews, or skill requests.
