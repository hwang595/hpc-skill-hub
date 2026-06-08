# Maintainer Guide

For maintainer rotation, role ownership, and operational continuity, see
[Maintainer Handoff](MAINTAINER_HANDOFF.md).

## Review Checklist

- The skill id matches the directory name.
- The README explains target users, assumptions, and risks.
- Examples avoid private hostnames, usernames, accounts, tokens, and dataset
  paths.
- Resource requests are conservative.
- Medium and high-risk skills explain cost, side effects, and rollback or
  cleanup expectations.
- Upstream references point to primary documentation where possible.
- `python3 tools/validate_skills.py` passes.

## Release Guidance

Until the registry reaches version `0.1.0`, use lightweight tags only when a
meaningful batch of skills or schema changes lands.

Suggested release notes sections:

- Added skills.
- Changed skill metadata.
- Validator changes.
- Breaking schema changes.
- Security or safety notes.

## Ownership

Each skill should eventually have at least one domain maintainer. Facility
operations, admin, and security-sensitive skills should require review from a
maintainer with production HPC experience.
