# MPI Rank Binding Diagnostics

Use this skill when an MPI job is slower than expected, rank placement looks
uneven, CPU binding is unclear, or `--ntasks`, `--ntasks-per-node`, and
`--cpus-per-task` may not match the application layout.

## Example

Replace `<account>` and `<partition>`, then submit in dry-run mode first:

```bash
sbatch examples/mpi-rank-binding-diagnostics.sbatch
```

Dry-run mode writes the intended compile and launch command without running the
MPI probe. To collect evidence from a tiny test job:

```bash
RUN_MPI_BINDING_PROBE=1 \
MPI_MODULE=<mpi-module> \
MPI_TASKS=4 \
CPU_BIND=verbose,cores \
  sbatch examples/mpi-rank-binding-diagnostics.sbatch
```

Keep the initial job short and small. Use the same node type, MPI module, and
launcher policy that the real workload uses before comparing results.

## Pattern

- Request a small representative Slurm allocation.
- Load the MPI module that matches the application build.
- Record `SLURM_*` variables, node list, CPU topology, and optional NUMA or
  hwloc evidence.
- Compile a tiny MPI probe with the same `mpicc` wrapper.
- Launch with `srun --cpu-bind=<policy>` and a small task count.
- Compare reported rank, host, processor name, visible CPUs, and affinity list.
- Change one placement setting at a time before collecting another report.

## Safety Notes

This skill is `medium` risk because it submits a Slurm job and launches MPI
ranks. The default job shape is intentionally tiny, and `RUN_MPI_BINDING_PROBE`
defaults to `0` so users can inspect the launch plan before running. Avoid using
large node counts, production inputs, or long walltimes for placement diagnosis.

## Success Criteria

- Dry-run mode prints compile and launch commands with the expected task count
  and binding policy.
- `topology.txt` records Slurm variables and visible CPU topology.
- `rank-affinity.tsv` contains one row per MPI rank.
- Rank placement matches the intended task shape across nodes.
- Affinity lists are consistent with the selected Slurm binding policy and
  `cpus-per-task`.
