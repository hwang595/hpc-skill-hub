---
name: Maturity review
about: Request review to promote a skill from seed to reviewed, field-tested, or maintained
title: "Maturity review: "
labels: ["maturity-review"]
---

## Skill

- Skill id:
- Current maturity:
- Requested maturity: reviewed / field-tested / maintained

## Review Scope

Which domain area does this review cover? For example: scheduler, storage,
software stacks, workflow engines, AI/HPC, bioinformatics, simulation, facility
operations, or training.

## Evidence

- [ ] README assumptions and safety notes are clear.
- [ ] Examples are conservative and inspectable.
- [ ] Risk level matches the most powerful example or recommendation.
- [ ] References are public and current enough for seed adoption.
- [ ] `make check` passes in the pull request.

## Field-Test Evidence

If requesting `field-tested`, describe the public environment type, what was
run or reviewed, and what changed because of the test. Do not include private
hostnames, usernames, allocation names, internal project identifiers, private
paths, or unpublished policy.

## Ownership

If requesting `maintained`, name the maintainer or maintainer group and the
expected review cadence.

## Related Links

Link the pull request, public documentation, safety review, site adapter, or
discussion that supports this request.
