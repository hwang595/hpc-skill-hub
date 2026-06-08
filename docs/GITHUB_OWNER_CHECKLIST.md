# GitHub Owner Checklist

Use this checklist when the repository owner or sponsoring organization is
ready to publish HPC Skill Hub on GitHub. It focuses on permissions and
public-launch decisions that cannot be proven from the local checkout.

## Owner Identity

- Choose the GitHub owner for `<owner>/hpc-skill-hub`.
- Decide whether the repository belongs under an individual account, a lab, a
  center, a university organization, or a neutral project organization.
- Confirm the owner can keep the repository public and accept outside
  contributions under the project license.
- Confirm the owner can publish GitHub Pages from Actions.

## Required Permissions

The publishing account needs permission to:

- Create a public repository named `hpc-skill-hub`.
- Push the initial `main` branch.
- Edit repository description, topics, features, and homepage URL.
- Enable Issues, Discussions, Pages, Dependabot alerts, and security features.
- Create labels, milestones, starter issues, and discussion categories.
- Apply branch rulesets after the first successful workflow runs.
- Create annotated tags and GitHub releases.

## Maintainer Map

Before launch, identify at least one person or team for each queue:

- Repository administration and release ownership.
- Registry schema, validator, generated artifact, and CLI maintenance.
- Scheduler, workflow-engine, software-stack, container, data, GPU/MPI,
  domain, site-adapter, and facility-operations review.
- Security or sensitive-report intake.
- Community triage for issues, discussions, and first-time contributors.

Update `.github/CODEOWNERS` after these GitHub users or teams exist. Use
[Review Routing](REVIEW_ROUTING.md), [Domain Reviewers](DOMAIN_REVIEWERS.md),
and [Contributor Ladder](CONTRIBUTOR_LADDER.md) as the policy sources.

## Public Safety Review

Before pushing publicly:

- Review [Public Launch Packet](PUBLIC_LAUNCH_PACKET.md).
- Run `python3 tools/launch_readiness.py --owner <owner> --run-check`.
- Run `python3 tools/launch_evidence.py --owner <owner> --run-check` and attach
  the report to the launch decision record or owner handoff.
- Confirm no private hostnames, usernames, allocation names, internal project
  ids, private paths, tickets, credentials, or unpublished cluster policy are
  present.
- Confirm site adapters are based on public documentation or clearly marked
  examples.
- Confirm starter issues and discussion prompts invite public-safe evidence,
  not private logs or support-ticket contents.

## Launch Decision Record

Record the launch decision in a public issue, discussion, or decision record
before running networked commands. Include:

- GitHub owner and repository URL.
- Launch maintainer and backup contact.
- First release owner.
- Whether Discussions and Pages will be enabled at launch.
- Whether branch rulesets will be applied immediately after the first green
  `Validate` and `Package` workflows.
- Any known public-scope limitations or deferred governance decisions.

## Final Preflight

Run the ordered dry-run plan:

```bash
python3 tools/github_publish_plan.py --owner <owner> --run-check
python3 tools/launch_evidence.py --owner <owner> --run-check
```

Then follow [GitHub Publishing Guide](GITHUB_PUBLISHING.md) and
[GitHub Repository Setup](GITHUB_REPOSITORY_SETUP.md) in the authenticated
environment.
