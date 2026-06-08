# IOR MDTest Storage Smoke

Use this skill when a user needs small, reviewable storage performance evidence
from a Slurm allocation before asking a filesystem, storage, or performance
team for help.

The Slurm example defaults to plan-only mode. It prints the IOR and MDTest
commands, records the target run directory, and exits. Set `RUN_BENCHMARK=1`
only after confirming local policy for shared filesystem benchmarks.

## Examples

```bash
bash examples/storage-smoke-preflight.sh
sbatch examples/ior-mdtest-smoke.sbatch
RUN_BENCHMARK=1 BENCH_ROOT="${SCRATCH}/ior-mdtest-smoke" sbatch examples/ior-mdtest-smoke.sbatch
python3 examples/summarize-results.py "${SCRATCH}/ior-mdtest-smoke/<job-id>"
CONFIRM_DELETE=1 bash examples/cleanup-run.sh "${SCRATCH}/ior-mdtest-smoke/<job-id>"
```

## Adaptation Points

- Replace `<account>` and `<debug-partition>`.
- Load the site-approved MPI, IOR, and MDTest modules before submitting.
- Set `BENCH_ROOT` to a scratch or project filesystem that policy allows for
  tiny benchmark runs.
- Keep `IOR_BLOCK_SIZE`, `IOR_TRANSFER_SIZE`, `IOR_SEGMENTS`,
  `MDTEST_ITEMS`, and `SLURM_NTASKS` small until a storage maintainer approves
  larger tests.
- Decide whether evidence should use `srun`, `mpirun`, or `mpiexec` through
  `MPI_LAUNCHER`.

## Safety Notes

This skill is `medium` risk because even small I/O benchmarks can create load
on shared filesystems and may be mistaken for production storage acceptance
tests. The defaults are intentionally tiny and plan-only. Do not run this skill
on login-node filesystems, home directories, or shared project paths without
explicit site guidance.

## Success Criteria

- The Slurm log records host, task count, target directory, tool versions, and
  exact benchmark commands.
- IOR and MDTest outputs are saved in a single marked run directory.
- The run uses a short allocation and bounded task, file, and metadata counts.
- Cleanup removes only the marked benchmark run directory after results are
  captured.
