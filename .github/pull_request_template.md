## Summary

Describe the skill, documentation, or tooling change.

## Change Type

- [ ] New skill.
- [ ] Skill update.
- [ ] Site adapter.
- [ ] Schema or tooling.
- [ ] Documentation or governance.
- [ ] CI, packaging, or generated registry output.

## Validation

- [ ] `python3 tools/validate_skills.py`
- [ ] `python3 tools/build_index.py --check`
- [ ] `python3 tools/build_health.py --check`
- [ ] `python3 tools/audit_safety.py`
- [ ] `python3 tools/scan_skill_security.py skills/<skill-id>`
- [ ] `python3 -m unittest discover -s tests`
- [ ] `make check`
- [ ] Generated files are current, if applicable.

## Risk

- [ ] No commands allocate compute resources.
- [ ] Commands allocate only user-owned resources and document expected impact.
- [ ] This changes shared/admin behavior and needs high-risk review.

## Safety And Privacy

- [ ] No usernames, tokens, allocation names, private hostnames, internal
      project identifiers, or unpublished cluster policy are included.
- [ ] Examples use placeholders for site-specific values.
- [ ] Expensive, destructive, or state-changing commands are opt-in or clearly
      documented.

## Site-Specific Assumptions

List scheduler, module, storage, account, partition, container, or network
assumptions that may not hold on other clusters.

## Reviewer Notes

Use `docs/REVIEW_ROUTING.md` to list domain expertise needed, requested
reviewers, upstream references used, and any follow-up issues that should be
opened after merge.
