# Training Cluster Reset Checklist

Use this checklist with a local site contact. It is intentionally written as a
review aid rather than an executable cleanup script.

## Before The Workshop

- Confirm the workshop schedule, expected learner count, and support contacts.
- Confirm public documentation links, login instructions, and account creation
  steps.
- Confirm the training partition, reservation, or queue policy.
- Confirm short CPU jobs, interactive sessions, and Jupyter exercises can run.
- Confirm required modules, containers, Python environments, and example data
  are visible from learner accounts.
- Confirm scratch, project, and home quota expectations.
- Confirm the escalation path for login, scheduler, filesystem, module, and
  network problems.

## During The Workshop

- Watch queue depth and failed jobs with read-only scheduler commands.
- Keep a visible issue log with timestamps and public-safe summaries.
- Avoid changing shared policy during instruction unless the site owner
  approves it.
- Record any exercise that requires site-specific instructions.

## After The Workshop

- Collect feedback while details are fresh.
- Review failed jobs and support tickets for repeated failure modes.
- Decide which files, allocations, reservations, or accounts need cleanup under
  local policy.
- Redact usernames, account names, hostnames, and private paths before sharing
  notes publicly.
- Open skill requests or site-adapter issues for reusable lessons.

## Do Not Put In The Public Registry

- Private hostnames, usernames, allocation names, or internal project ids.
- Destructive cleanup commands.
- Account or quota administration steps.
- Unpublished security, incident, or identity-management procedures.
