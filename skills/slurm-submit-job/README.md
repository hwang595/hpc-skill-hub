# Slurm Submit Job

Use this skill to translate a reviewed CPU, MPI, GPU, or array workload into a
Slurm batch script with explicit site placeholders and conservative smoke-test
resources. It helps prepare and validate a script; submission remains a separate
user-approved action because it allocates shared compute resources.

## Prerequisites

- Confirm that the target scheduler is Slurm and that submission is allowed
  from the current host.
- Obtain account, partition, QOS, module, filesystem, and GPU syntax from a
  public site adapter or the user. Never infer private cluster policy.
- Identify the command, working directory, input/output paths, expected runtime,
  task shape, memory basis, and whether the application is MPI- or GPU-aware.
- Preserve placeholders until each local value has been reviewed.

## Inputs And Outputs

Inputs are the workload command and reviewed resource/site values. The prepared
output is an sbatch script. After explicit submission, `sbatch` prints a job id
and Slurm writes the configured stdout/stderr files.

## Workflow

1. Select the smallest matching example:

   | Workload | Example | Key resource decision |
   | --- | --- | --- |
   | One process with threads | `cpu.sbatch` | CPUs per task and memory per job |
   | MPI ranks across nodes | `mpi.sbatch` | Nodes, tasks per node, compatible MPI |
   | One GPU process | `gpu.sbatch` | Site GPU request syntax and runtime |
   | Repeated independent items | `array.sbatch` | Array range, concurrency, input mapping |

2. Copy the example to a task-local path and replace only reviewed placeholders.
3. Set a short smoke-test walltime and a small representative input. Request
   memory in the unit and scope expected by local policy.
4. Run the static reviewer before contacting Slurm:

   ```bash
   bash examples/review-sbatch.sh <reviewed-script>
   ```

5. When available, the user may choose to run `sbatch --test-only
   <reviewed-script>`. This contacts Slurm and is site/version dependent, but
   does not submit the job.
6. Show the final script, resource/cost summary, output path, and cleanup plan.
   Submit with `sbatch <reviewed-script>` only after explicit user approval.

## Failure Modes

- Invalid account, partition, QOS, reservation, or GPU syntax requires local
  policy evidence; do not cycle through guessed values.
- A pending job is not a submission failure. Inspect its reason with
  `slurm-pending-reason-triage` before changing resources.
- Exit `127` or module errors usually mean environment setup failed before the
  workload. Compare login and compute-node module/runtime assumptions.
- MPI launch failures can come from a launcher/runtime mismatch. Keep compiler,
  MPI library, and launcher from one compatible site-supported stack.
- Missing output can result from a working-directory or filename pattern issue;
  inspect the job record before resubmitting.

## Validation

Before submission, shell syntax must pass, all angle-bracket placeholders must
be resolved, resource directives must match the workload shape, and output paths
must be writable. After submission, record the job id, verify the expected queue
state, and confirm the smoke-test output contains the expected command result.
A queued job is accepted by Slurm but is not yet proof that the workload works.

## Resource And Cost

Every submitted example can consume shared CPU, memory, GPU, filesystem, and
allocation quota. Arrays multiply the per-task request by concurrent tasks; MPI
jobs multiply ranks and nodes. State the total request and walltime limit before
submission, and avoid reserving GPUs or multiple nodes for a CPU-only smoke test.

## Cleanup

The static reviewer writes no files. A submitted smoke test creates scheduler
records and output logs; retain useful evidence or remove task-local files under
project policy. Use `scancel <job-id>` only with explicit approval after checking
that the id belongs to this workload. Do not delete scientific outputs as part
of generic cleanup.

## Site Adaptation

Account requirements, default memory scope, QOS, partitions, modules, GPU GRES
or TRES syntax, array limits, and allowed filesystems vary by site. Keep values
such as `<account>`, `<partition>`, `<gpu-partition>`, and `<mpi-module>` visible
until resolved. Do not publish private accounts, hostnames, paths, or policy.

## Safety Notes

This skill is `medium` risk because `sbatch` allocates shared resources and the
workload command may write data or trigger downstream actions. Static review is
read-only. Never auto-submit examples, silently expand an array, or run an
unreviewed application command.
