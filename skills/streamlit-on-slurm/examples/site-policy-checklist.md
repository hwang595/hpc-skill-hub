# Site Policy Checklist

Confirm these items before starting a Streamlit app on Slurm:

- User-started web apps are allowed on compute nodes.
- SSH tunnels, Open OnDemand proxying, or any other access method follows local
  policy.
- The app does not expose restricted data, secrets, tokens, or private paths.
- The selected port is allowed and not already in use.
- The app uses a short wall time and an appropriate interactive or debug
  partition.
- Python package caches and virtual environments are on suitable storage.
- The tunnel is closed and the Slurm job is cancelled when the app is no longer
  needed.
