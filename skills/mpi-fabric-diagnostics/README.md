# MPI Fabric Diagnostics

Use this skill when a multi-node MPI job runs slowly, hangs during startup, or
appears to fall back to an unexpected transport. It collects public-safe
evidence about the MPI launcher, Open MPI components, UCX, libfabric, PMIx,
optional InfiniBand device visibility, and a tiny communication probe.

## Example

Replace `<account>` and `<partition>`, then submit in dry-run mode first:

```bash
sbatch examples/mpi-fabric-diagnostics.sbatch
```

Dry-run mode writes the environment and tool report, then prints the compile
and launch plan. To run the small MPI communication probe:

```bash
RUN_MPI_FABRIC_PROBE=1 \
MPI_MODULE=<mpi-module> \
MPI_TASKS=4 \
  sbatch examples/mpi-fabric-diagnostics.sbatch
```

Optional transport hints such as `UCX_TLS`, `UCX_NET_DEVICES`, `FI_PROVIDER`,
or Open MPI MCA settings should come from site documentation or maintainer
guidance. Avoid guessing network interface names in public examples.

## Pattern

- Load the same MPI module used by the application.
- Record Slurm, MPI, UCX, libfabric, PMIx, and launcher environment variables.
- Capture `ompi_info`, `ucx_info`, `fi_info`, and `ibv_devinfo` output when
  those tools are available.
- Compile a tiny MPI probe with the same `mpicc` wrapper.
- Launch through `srun` with a small multi-node task shape.
- Compare rank placement, hostname pairs, small-message latency, and large-message
  bandwidth before changing transport hints.
- Change one transport setting at a time and keep each report with the Slurm job
  id and module stack.

## Safety Notes

This skill is `medium` risk because it submits a Slurm job and can exercise the
cluster interconnect. Defaults are intentionally small, and
`RUN_MPI_FABRIC_PROBE` defaults to `0`. Tool output may contain internal device
names, interface names, hostnames, or topology details, so sanitize evidence
before sharing it publicly.

## Success Criteria

- Dry-run mode records available MPI, UCX, libfabric, and Slurm evidence.
- The compile and `srun` command lines match the expected MPI module and task
  shape.
- `mpi-fabric-probe.tsv` contains rank placement and at least one pairwise
  timing row when the probe is enabled.
- Reports are collected before forcing transport variables or MCA settings.
- Any escalation to site networking or MPI maintainers includes sanitized logs
  and the exact module stack.
