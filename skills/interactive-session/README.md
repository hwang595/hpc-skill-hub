# Interactive Session

Use this skill for short debugging sessions, notebook launches, and interactive
development on compute resources.

## Examples

```bash
bash examples/slurm-shell.sh
bash examples/jupyter-on-node.sh
```

## Safety Notes

Interactive jobs consume shared resources while the shell or notebook is open.
Use short wall times, close idle sessions, and prefer a debug partition when
your site provides one.

## Success Criteria

- The shell hostname is a compute node, not the login node.
- `squeue -u "$USER"` shows the interactive job.
- Notebook or tunnel instructions point to the allocated node and selected port.
