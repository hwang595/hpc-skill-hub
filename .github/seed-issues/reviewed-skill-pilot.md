The seed registry is ready for a first `reviewed` maturity pilot. The goal is
to pick a small, public-safe batch of seed skills, route them to domain
reviewers, and record enough evidence to promote them without creating private
cluster dependencies.

Maintainer prep:

```bash
python3 tools/review_candidates.py --limit 12
python3 tools/review_candidates.py --json --limit 12
```

Use the report as a starting queue. It ranks seed skills by local metadata,
examples, references, tests, collection coverage, README presence, risk level,
and reviewer routing. It is not a maturity decision by itself.

Suggested pilot shape:

- Select 6 to 12 low-risk or well-bounded seed skills across at least three
  reviewer areas.
- Assign a domain reviewer for each selected skill using
  `docs/DOMAIN_REVIEWERS.md`.
- Open or link one maturity review issue per selected skill using the maturity
  review template.
- Confirm examples, references, portability, site assumptions, and risk labels.
- Keep all evidence public-safe: no private hostnames, allocation names,
  usernames, internal paths, ticket numbers, unpublished policy, or private
  dataset names.
- Update `maturity` only through a pull request that refreshes generated
  registry artifacts and passes `make check`.

Good first reviewer areas for this pilot include scheduler and allocation,
storage and data movement, software environments, read-only facility
operations, and MPI/performance evidence. Medium-risk skills can join the pilot
when a domain reviewer confirms resource bounds, cleanup behavior, and site
assumptions are clear.

Definition of done:

- The selected pilot skill list is posted in this issue.
- Each selected skill has an assigned reviewer or a clear missing-reviewer note.
- At least one skill has a reviewed promotion pull request, or the issue
  records exactly which evidence is missing before promotion.
- Follow-up gaps are split into focused issues labeled `maturity-review`,
  `needs-domain-review`, `documentation`, `skill-request`, or `safety-review`.
