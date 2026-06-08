# v0.2.0 Release Notes

Status: in development.

## Summary

`v0.2.0` is the reviewed-skill pilot release. It turns the seed registry from a
large catalog into a reviewable queue: maintainers can identify first review
candidates, route them by domain focus, create maturity-review issues, and
promote skills only after public-safe evidence exists.

The release does not automatically mark skills as `reviewed`. It adds the
process and generated artifacts needed to make those promotions auditable.

## Registry Contents

- Skills: 96.
- Collections: 12.
- Site adapters: 2, including 1 example adapter and 1 public-doc-backed draft
  adapter.
- Skill maturity target: select seed skills for first `reviewed` review.
- Risk labels: low and medium only.

## Added

- A generated reviewed-skill pilot packet at
  `docs/REVIEW_PACKET_v0.2.0.md`.
- A `tools/review_packet.py` command that builds or checks the pilot packet
  from `registry/index.json` and `tools/review_candidates.py` scoring.
- Suggested maturity-review issue titles, labels, review focus areas, evidence
  summaries, and promotion gates for the first review queue.
- A `v0.2.0` release manifest target at `registry/releases/v0.2.0.json` so the
  already-published `v0.1.0` snapshot can remain immutable.
- CI coverage for the reviewed-skill pilot packet and the current release
  manifest.

## Maintainer Workflow

Use the packet to start review work:

```bash
python3 tools/review_packet.py --check
python3 tools/review_packet.py --json --limit 12
python3 tools/review_candidates.py --collection data-movement --limit 8
```

For each selected skill:

1. Open a `maturity-review` issue.
2. Assign a domain reviewer based on the packet review focus.
3. Add `safety-review` when the packet suggests it or when admin, facility,
   quota, accounting, or shared software behavior is in scope.
4. Confirm examples, assumptions, references, and risk labels.
5. Promote from `seed` to `reviewed` only in a pull request that links the
   review issue and passes `make check`.

## Known Limitations

- The packet uses repository metadata and static evidence; it is not a domain
  review decision.
- `field-tested` and `maintained` maturity still require adoption reports or
  explicit maintainer ownership beyond this release.
- Site adapters remain draft until a real site or training environment reviews
  public policy mappings.

## Release Checks

Before tagging `v0.2.0`, maintainers should confirm:

- `make check` passes locally and in GitHub Actions.
- `docs/REVIEW_PACKET_v0.2.0.md` is current.
- `registry/releases/v0.2.0.json` is current and attached to the GitHub
  release.
- At least the first maturity-review issues are opened or explicitly deferred.
- No maturity promotion lacks public review evidence.
