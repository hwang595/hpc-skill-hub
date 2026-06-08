# JAX Distributed On Slurm

Use this skill when a JAX workload needs a small, reviewable Slurm smoke test
before running real distributed training, simulation, or accelerator-heavy
array computations.

## Example

Edit account, partition, resource requests, and environment setup lines, then
submit a dry run:

```bash
sbatch examples/jax-distributed.sbatch
```

The example prints the selected coordinator address, process count, visible
accelerators, and command that would run. After reviewing the plan, submit with:

```bash
RUN_JAX_SMOKE=1 sbatch examples/jax-distributed.sbatch
```

## Pattern

- Start with one short GPU allocation before scaling across nodes.
- Load or activate the same JAX environment used by the real workload.
- Pick process 0 on the first Slurm node as the coordinator.
- Export `JAX_COORDINATOR_ADDRESS` and `JAX_NUM_PROCESSES`; derive the process
  id from Slurm rank variables inside each launched process.
- Initialize JAX before running any JAX computation when more than one process
  participates.
- Capture backend, local devices, process index, process count, and a tiny
  compiled computation in the Slurm log.

## Safety Notes

This skill is `medium` risk because it requests GPU resources and may open a
coordinator port inside a compute allocation. Keep the wall time short, start
with one node, use a site-approved partition, and avoid long training jobs until
the smoke test succeeds. The included Python script does not download data,
write checkpoints, or allocate large arrays.

## Success Criteria

- Every Slurm task starts and imports JAX successfully.
- Each process reports its host, process id, process count, backend, and local
  devices.
- Multi-process runs initialize the JAX distributed runtime before computation.
- The smoke computation completes and prints `status=ok` on each process.
- The log is small enough to attach to a public-safe issue or support request
  after removing site-specific account or host details if needed.
