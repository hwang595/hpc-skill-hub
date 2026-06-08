# Support

HPC Skill Hub is a public registry of reusable HPC skills, examples, and site
adapter patterns. It is not a replacement for your local HPC center's support
desk or incident response process.

## Where To Ask

- Use a skill request issue for a missing reusable HPC workflow.
- Use a bug report for incorrect metadata, broken examples, validation errors,
  generated registry output, or CLI behavior.
- Use a documentation issue for unclear guidance, missing assumptions, or
  confusing onboarding material.
- Use a site adapter request for public local policy that can be shared without
  private cluster details.
- Use a safety review issue for risk, privacy, shared-system impact, facility
  operations, or high-risk behavior.
- Use a maturity review issue when a skill has evidence to move beyond `seed`.
- Use an adoption report to share public-safe feedback from a pilot.

For urgent local outages, login problems, allocation issues, quota changes,
node incidents, account management, or private data concerns, contact your
local HPC support team.

## What To Include

Public issues should include:

- Skill id, collection id, or site adapter id.
- What you expected to happen.
- What actually happened.
- Public documentation links, if available.
- Redacted command output or validation output.
- Environment type, such as campus Slurm cluster, training cluster, cloud HPC,
  lab-managed cluster, or containerized test environment.

## What Not To Include

Do not post:

- Private hostnames, usernames, account names, allocation names, tokens, or
  internal project identifiers.
- Private storage paths, dataset names, support tickets, or incident details.
- Unpublished security, identity-management, accounting, quota, or node
  operations procedures.
- Large logs containing user data or private cluster policy.

If you discover a security-sensitive problem, follow [Security Policy](SECURITY.md)
instead of opening a public issue.

## Maintainer Response

During the seed stage, maintainers prioritize:

- Safety, privacy, and shared-system risk.
- Broken validation, generated registry output, or release blockers.
- Good first issues for reusable skills and public site adapters.
- Adoption reports that reveal repeated support needs.
- Maturity reviews with public evidence.

Responses may be slower for site-specific debugging that cannot be reproduced
from public information.
