# VS Code Tunnel On Slurm

Use this skill when users need an IDE session on a compute node instead of a
login node, and the site allows VS Code Remote Tunnels or equivalent outbound
tunnel services.

The example defaults to plan-only mode. It prints the intended command and
environment, then exits. Set `RUN_VSCODE_TUNNEL=1` only after checking local
policy and selecting a short allocation.

## Examples

```bash
bash examples/vscode-tunnel-preflight.sh /path/to/project
sbatch examples/vscode-tunnel.sbatch
RUN_VSCODE_TUNNEL=1 sbatch examples/vscode-tunnel.sbatch
```

## Adaptation Points

- Replace `<account>` and `<debug-partition>`.
- Keep the Slurm time limit short, especially for workshop environments.
- Use a generic tunnel name that does not expose private host, project, or user
  information.
- Set `VSCODE_PROJECT_DIR` to a project or scratch path that is appropriate for
  interactive editing.
- Avoid running the tunnel on login nodes; start it from an allocated compute
  node.

## Safety Notes

This skill is `medium` risk because VS Code tunnels create a long-running remote
development session, consume allocated compute resources, and use outbound
network access. Some facilities prohibit or restrict these services. Review the
site policy checklist before enabling `RUN_VSCODE_TUNNEL=1`.

## Success Criteria

- The Slurm log shows a compute hostname and selected project directory.
- `code tunnel --help` works in the job environment.
- The tunnel only runs inside the scheduled allocation.
- The user cancels the Slurm job when the IDE session is finished.
