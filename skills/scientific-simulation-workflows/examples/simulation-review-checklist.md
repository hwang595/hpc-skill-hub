# Simulation Workflow Review Checklist

Use this checklist before moving from a small smoke case to a production
scientific simulation run.

## Inputs

- Required input files are present in the intended working directory.
- Relative paths inside input decks, control files, and include files are
  reviewed.
- Initial conditions, restart files, mesh files, topology files, pseudopotentials,
  force fields, or license-dependent inputs are named in the run notes.
- A small public tutorial case or reduced-size smoke case has been identified.

## Runtime

- Scheduler script requests nodes, tasks, CPUs per task, memory, GPUs, and time
  limits that match the software decomposition model.
- MPI launcher and software executable come from compatible modules, containers,
  or site wrappers.
- OpenMP, BLAS, GPU, and MPI environment variables are recorded.
- Container bind mounts include only the input, output, and software paths
  needed by the run.

## Launch

- The first run is a plan, dry-run, validation, or short smoke test when the
  software supports it.
- Production submission is explicit and separate from input checks.
- Output, restart, checkpoint, stdout, stderr, and application logs have stable
  paths.
- Long simulations include checkpoint/restart notes before scale-up.

## Post-Processing

- Post-processing commands are separate from the simulation launch command.
- Expected output files and lightweight validation checks are listed.
- Large output trees are not copied, deleted, compressed, or archived without an
  explicit review step.
- Plots, summaries, or derived files include enough provenance to trace the
  original run.

## Log Triage

- Logs are scanned for memory, MPI, GPU, convergence, license, filesystem, and
  walltime signals.
- First failing rank, timestep, iteration, solver, or file path is captured when
  available.
- Resource changes are based on evidence from logs, scheduler accounting, or a
  smaller reproduced case.
