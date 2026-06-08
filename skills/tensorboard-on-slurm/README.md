# TensorBoard On Slurm

Use this skill when TensorBoard should inspect training logs from a scheduled
Slurm allocation instead of running a web monitor on a login node.

The Slurm example defaults to plan-only mode. It checks the TensorBoard CLI,
summarizes the log directory, prints the intended command, and exits. Set
`RUN_TENSORBOARD=1` only after confirming local policy for user-started web
monitors and tunnels.

## Examples

```bash
bash examples/tensorboard-preflight.sh /path/to/logdir
sbatch examples/tensorboard-server.sbatch
RUN_TENSORBOARD=1 TENSORBOARD_LOGDIR=/path/to/logdir sbatch examples/tensorboard-server.sbatch
bash examples/tunnel-template.sh <compute-host> 6006 6006
```

## Adaptation Points

- Replace `<account>`, `<debug-partition>`, and `<login-host>`.
- Load the site-approved Python, TensorFlow, PyTorch, or TensorBoard
  environment before submitting the job.
- Set `TENSORBOARD_LOGDIR` to the durable directory containing event files.
- Keep TensorBoard bound to local or tunneled access unless the site provides a
  managed proxy.
- Keep the allocation short and cancel idle monitor jobs.

## Safety Notes

This skill is `medium` risk because TensorBoard starts a browser-accessible web
server and may expose training metadata, file names, hyperparameters, or sample
artifacts through the UI. Use SSH tunnels or site portals only when approved by
local policy.

## Success Criteria

- The Slurm log shows a compute hostname, log directory, and selected port.
- `tensorboard --version` works in the selected environment.
- The log directory contains event-like files or a reviewed reason why it is
  currently empty.
- The user closes the tunnel and cancels the Slurm job when finished.
