# Open OnDemand Batch Connect

Use this skill when an HPC support, portal, or training team needs a small,
reviewable Open OnDemand Batch Connect app skeleton for a Slurm-backed
interactive workflow.

The example app is intentionally conservative. It records the rendered session
context, exports `SLURM_EXPORT_ENV=ALL` for Slurm compatibility review, and
defaults to a placeholder script that starts no long-running service unless the
site replaces it with an approved command.

## Examples

```bash
bash examples/validate-batch-connect-app.sh examples/batch-connect-app
find examples/batch-connect-app -maxdepth 3 -type f | sort
```

Copy the skeleton only into a development or review area approved by the local
Open OnDemand maintainers. Do not deploy it into a production dashboard until
the site has reviewed authentication, reverse proxy behavior, scheduler
settings, partitions, accounts, logs, and data exposure.

## Adaptation Points

- Replace `<cluster-id>`, `<account>`, `<debug-partition>`, and `<module>`.
- Replace `template/script.sh` with the site-approved application launcher.
- Keep wall time, task counts, memory, GPU requests, and service ports bounded.
- Prefer portable `script` options such as `accounting_id`, `queue_name`, and
  `wall_time` before using resource-manager-specific `native` arguments.
- Keep app logs, output directories, and connection details public-safe before
  sharing examples upstream.

## Safety Notes

This skill is `medium` risk because Batch Connect apps submit jobs and may
expose web services, logs, environment variables, file names, or user data
through a portal session. Treat app deployment as a site-owned change, not a
user-owned script edit.

## Success Criteria

- The app skeleton has `manifest.yml`, `form.yml.erb`, `submit.yml.erb`, and a
  reviewed `template/` directory.
- Scheduler fields use placeholders or site-approved values.
- A portal maintainer has reviewed authentication, proxying, logging, cleanup,
  and user-visible output.
- The first test run uses a development area, short wall time, and a non-public
  pilot group.
