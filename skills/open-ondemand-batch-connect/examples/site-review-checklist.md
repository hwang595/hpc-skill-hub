# Site Review Checklist

Confirm these items before deploying a Batch Connect app beyond a development
or pilot area:

- The app is reviewed by local Open OnDemand maintainers.
- The target cluster id, account, queue, wall time, task count, memory, and GPU
  requests follow public local policy.
- Authentication, authorization, reverse proxy behavior, and connection cards
  are site-approved.
- Environment setup uses reviewed modules, containers, or wrapper scripts.
- User-visible logs do not expose private paths, tokens, service URLs, or
  sensitive environment variables.
- The app cleans up temporary files and cancels idle scheduler jobs when
  sessions end.
- The app has a rollback plan and is tested first with a small pilot group.
