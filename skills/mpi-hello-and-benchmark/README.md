# MPI Hello And Benchmark

Use this skill to verify that a selected compiler wrapper, MPI runtime, Slurm
launcher, and allocation can execute one small rank per requested task. Despite
the historical name, the default workflow is a placement and connectivity smoke
test; it does not produce a portable latency or bandwidth benchmark.

## Prerequisites

- Confirm that the cluster uses Slurm and identify a user-approved account,
  partition, MPI module, node count, tasks per node, memory, and walltime.
- Use one compatible compiler/MPI stack. Do not mix an executable built against
  one MPI implementation with another implementation's launcher or libraries.
- Confirm the site's supported Slurm MPI plugin or launcher guidance. `srun`
  behavior can depend on how Slurm and the MPI implementation were built.
- Review the two-node request before submission. A one-node run cannot prove
  node-to-node launch or placement.

## Inputs And Outputs

Inputs are `hello_mpi.c`, the reviewed Slurm resource request, and the local MPI
module name. The job creates a temporary binary in job-local temporary storage,
prints rank, size, and hostname lines to `slurm-<job-id>.out`, then removes the
temporary binary. The offline reviewer reads a saved log and prints a rank and
host summary without contacting Slurm.

## Workflow

1. Review `examples/run-mpi.sbatch`. Replace `<account>` and `<partition>` or
   provide equivalent user-approved command-line overrides. Supply the module
   only from local policy:

   ```bash
   export HPC_SKILL_HUB_MPI_MODULE=<mpi-module>
   ```

2. Check shell syntax and unresolved placeholders before any submission. Verify
   that two nodes and four total ranks are an acceptable smoke-test request.
3. If the user explicitly approves the allocation, submit the reviewed script:

   ```bash
   sbatch <reviewed-run-mpi.sbatch>
   ```

4. Preserve the output log and review it offline:

   ```bash
   python3 examples/review-mpi-log.py \
     --expected-ranks 4 --expected-hosts 2 slurm-<job-id>.out
   ```

5. Only after the hello test passes should a user choose an implementation- and
   fabric-specific performance benchmark with locally reviewed message sizes,
   repetitions, process placement, and result interpretation.

## Failure Modes

- Missing `module`, `mpicc`, or `srun` means the batch environment is incomplete;
  do not guess a replacement module or launcher.
- Compile or link errors usually indicate wrapper, header, library, or toolchain
  inconsistency. Capture `mpicc` identity and loaded modules before rebuilding.
- Every rank failing at launch suggests a launcher/plugin or runtime mismatch;
  one rank failing can indicate node, process, or application evidence.
- Duplicate or missing rank numbers, inconsistent communicator size, or fewer
  hostnames than expected means the placement test is inconclusive or failed.
- A timeout after partial output requires scheduler and MPI logs; increasing
  walltime does not resolve a transport or launcher mismatch.

## Validation

Success requires a clean compile, exactly one output line for every rank from
zero through `size - 1`, one consistent communicator size, and the expected node
distribution. For the default script, four ranks should appear across two
hostnames. A successful hello run validates this small launch shape only; it does
not certify application scaling, fabric health under load, or performance.

## Resource And Cost

The default example requests two nodes, four total CPU tasks, 2 GiB of memory,
and ten minutes. It consumes shared allocation and node time even though the MPI
program runs briefly. Use a debug partition where available, but do not silently
reduce to one node when the stated goal is node-to-node validation.

## Cleanup

The script removes its temporary binary and build directory on exit without
recursive deletion. The Slurm output log remains in the submission directory;
retain it as evidence or remove it under project policy. Cancel a stuck job only
after explicit approval and confirmation of the job id.

## Site Adaptation

MPI module names, compiler families, PMI/PMIx support, launcher flags,
partitions, accounts, and network plugins are site-specific. Resolve them from a
public adapter or user-provided documentation. Redact accounts, hostnames, paths,
module trees, and internal fabric details before publishing logs.

## Safety Notes

This skill is `medium` risk because it can reserve multiple nodes. Static source
and log review are read-only. Never auto-submit the example, turn the smoke test
into a large benchmark, or generalize results across clusters or MPI stacks.
