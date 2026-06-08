# Site Policy Checklist

Confirm these items before starting TensorBoard on Slurm:

- User-started web monitors are allowed on compute nodes.
- SSH tunnels, Open OnDemand proxying, or any other access method follows local
  policy.
- The log directory does not expose restricted data, private paths, tokens, or
  sensitive sample artifacts through TensorBoard.
- The selected port is allowed and not already in use.
- The monitor uses a short wall time and an appropriate interactive or debug
  partition.
- TensorBoard reads from durable training logs rather than forcing training jobs
  to write to slow or unsuitable storage.
- The tunnel is closed and the Slurm job is cancelled when monitoring is done.
