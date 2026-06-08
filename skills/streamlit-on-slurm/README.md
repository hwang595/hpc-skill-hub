# Streamlit On Slurm

Use this skill when a Python data app or AI demo should run inside a scheduled
Slurm allocation instead of on a login node.

The Slurm example defaults to plan-only mode. It checks the Python environment,
prints the intended Streamlit command, and exits. Set `RUN_STREAMLIT_APP=1` only
after confirming local policy for user-started web apps and tunnels.

## Examples

```bash
bash examples/streamlit-preflight.sh examples/streamlit_app.py
sbatch examples/streamlit-app.sbatch
RUN_STREAMLIT_APP=1 STREAMLIT_APP=examples/streamlit_app.py sbatch examples/streamlit-app.sbatch
bash examples/tunnel-template.sh <compute-host> 8501 8501
```

## Adaptation Points

- Replace `<account>`, `<debug-partition>`, and `<login-host>`.
- Load the site-approved Python, Conda, Mamba, or virtualenv environment before
  submitting the job.
- Set `STREAMLIT_APP` to a reviewed app entrypoint.
- Choose a port allowed by local policy, defaulting to `8501`.
- Keep the wall time short and cancel idle apps.

## Safety Notes

This skill is `medium` risk because Streamlit starts a browser-accessible web
server, may expose data through the app UI, and consumes allocated compute
resources until stopped. Use SSH tunnels or site portals only when approved by
local policy.

## Success Criteria

- The Slurm log shows a compute hostname, app path, and selected port.
- `streamlit run` is available in the selected Python environment.
- The app runs only inside a scheduled compute allocation.
- The user closes the tunnel and cancels the Slurm job when finished.
