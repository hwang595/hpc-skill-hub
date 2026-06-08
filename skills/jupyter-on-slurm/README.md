# Jupyter On Slurm

Use this skill when a user needs a notebook or JupyterLab session backed by a
compute allocation rather than a login node.

## Example

Replace `<account>`, `<partition>`, and `<python-module>` as needed, then
submit:

```bash
sbatch examples/jupyter-lab.sbatch
```

Watch the Slurm output file for the compute host, port, and Jupyter URL. From
your laptop, adapt the tunnel command printed by the job or use:

```bash
bash examples/tunnel-template.sh <login-node> <compute-node> 8888
```

## Safety Notes

This skill is `medium` risk because a notebook keeps compute resources allocated
while the server is running. Use a short wall time, shut down idle kernels, and
cancel the job when finished. Do not publish notebook tokens or URLs in public
issues.

## Site Notes

Some clusters require a two-hop tunnel through the login node, some provide Open
OnDemand, and some block direct compute-node forwarding. Treat the tunnel
command as a template and follow local user documentation.

## Success Criteria

- The notebook process runs on the compute node named in the Slurm log.
- The selected port is shown in both the log and tunnel command.
- The browser opens only after a local SSH tunnel or site-approved portal is in
  place.
- The job is cancelled or exits when notebook work is complete.
