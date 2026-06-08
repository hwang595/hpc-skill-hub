# Site Policy Checklist

Confirm these items before starting a VS Code tunnel on an HPC system:

- Outbound VS Code Remote Tunnels or comparable developer tunnel services are
  allowed by the facility.
- The tunnel starts only inside a scheduled compute allocation.
- The selected project directory does not expose restricted data.
- The tunnel name avoids private hostname, username, project, ticket, or grant
  details.
- The time limit is short and the job is cancelled when the IDE session ends.
- Authentication uses the user's own approved account.
- Stale tunnel registrations are removed according to local support guidance.
