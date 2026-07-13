# IOR MDTest Storage Smoke

Use this skill to collect small, reviewable IOR and MDTest evidence from a
Slurm allocation before a filesystem, storage, or performance support handoff.
It tests one bounded workload shape and target path; it is not a site acceptance
test, production benchmark, or basis for cross-system performance rankings.

## Prerequisites

- Confirm the site permits user-started storage benchmarks on the selected
  scratch or project filesystem. Do not use home, login-node-local, archival,
  or unapproved shared paths.
- Obtain a reviewed account, debug partition, MPI stack/launcher, IOR/MDTest
  installation, existing benchmark root, short walltime, and cleanup owner.
- Check concurrent maintenance, outages, purge policy, quotas, and whether the
  storage team wants cache state or other context recorded.
- Keep the provided smoke caps. Larger task, data, file, iteration, or depth
  settings belong in a separately reviewed benchmark plan.

## Inputs And Outputs

Inputs are an existing `BENCH_ROOT`, local policy confirmation, and bounded
Slurm/IOR/MDTest parameters. Plan-only mode prints metadata and exact commands
without creating files. An approved run creates one marker-protected directory
containing metadata, commands, tool versions, IOR/MDTest output, and a summary.

## Workflow

1. Complete `examples/site-policy-checklist.md` and run the non-creating
   preflight:

   ```bash
   bash examples/storage-smoke-preflight.sh <approved-benchmark-root>
   ```

   If the approved root does not yet exist, show the planned path first. Create
   it only after review with `CREATE_BENCH_ROOT=1`.
2. Replace `<account>` and `<debug-partition>`, load site-approved MPI, IOR, and
   MDTest modules, and review `MPI_LAUNCHER` with local launcher guidance.
3. Submit the batch script in plan-only mode. It checks tools and limits, prints
   the exact commands, and exits without creating a run directory:

   ```bash
   sbatch examples/ior-mdtest-smoke.sbatch
   ```

4. After reviewing the Slurm log and receiving explicit policy approval, submit
   with both execution gates:

   ```bash
   RUN_BENCHMARK=1 CONFIRM_STORAGE_POLICY=1 \
     BENCH_ROOT=<approved-benchmark-root> sbatch examples/ior-mdtest-smoke.sbatch
   ```

5. Summarize the marked run and preserve the raw output:

   ```bash
   python3 examples/summarize-results.py <run-directory>
   ```

6. Cleanup is separate and marker-guarded. Review the exact run directory before
   opting into recursive deletion:

   ```bash
   CONFIRM_DELETE=1 bash examples/cleanup-run.sh <run-directory>
   ```

## Failure Modes

- Missing `srun`, IOR, MDTest, or Python indicates an incomplete module/runtime
  setup; do not guess replacement modules or launchers.
- A missing, non-directory, or non-writable benchmark root blocks execution.
  Plan-only mode may still show what needs local resolution.
- Values above smoke caps are rejected rather than silently creating a larger
  workload. Use a separate reviewed benchmark for larger experiments.
- An existing run directory is never reused. Choose a new label and preserve the
  earlier evidence before retrying.
- IOR succeeding while MDTest fails, or the reverse, is partial evidence. Keep
  both raw outputs and do not collapse data and metadata behavior into one score.
- Results can vary with contention, cache state, striping, clients, and site
  conditions. One small sample cannot establish a general performance claim.

## Validation

Plan-only success means no run directory or marker was created and the log shows
the reviewed target, caps, tools, metadata, and commands. Run success means IOR
and MDTest both completed, required files and marker exist, the summary helper
accepts the bundle, and the measured scope matches the approved request.

## Resource And Cost

The default requests one node, four tasks, 2 GiB of memory, ten minutes, about
256 MiB of aggregate IOR transfer for the default file-per-process shape, and 32
MDTest items per rank. The script caps tasks, block/transfer sizes, segments,
items, iterations, and depth. Even bounded tests create shared filesystem and
metadata load, so schedule them according to local policy and avoid repetition.

## Cleanup

Plan-only and default preflight modes create nothing. Approved runs leave one
marked directory and the Slurm log. The cleanup helper requires explicit
confirmation, a path under `ior-mdtest-smoke`, and the marker file. Preserve raw
evidence first; recursive deletion remains a review-required destructive action.

## Site Adaptation

Accounts, partitions, MPI launchers, modules, allowed roots, striping, cache
guidance, quotas, and result interpretation are site-specific. Record only
public or user-approved values and redact usernames, projects, paths, hostnames,
allocation ids, and unpublished topology before sharing.

## Safety Notes

This skill is `medium` risk because approved execution consumes allocation and
can load shared storage. Never auto-submit it, bypass either execution gate,
raise smoke caps in place, run on an unapproved filesystem, or present one run as
site-wide performance. Cleanup remains explicit and must be reviewed separately.
