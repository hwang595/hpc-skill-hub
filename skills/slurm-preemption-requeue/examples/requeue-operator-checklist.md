# Manual Requeue Operator Checklist

Use this checklist before running a manual command such as:

```bash
scontrol requeue <job-id>
```

## Confirm First

- The job owner or authorized coordinator requested the requeue.
- The job has `--requeue` enabled or the site default allows requeue.
- The workload writes restartable checkpoint state to durable storage.
- Output files are append-safe, versioned, or cleaned by the application before
  resume.
- The next run will not double-charge, double-submit, or duplicate downstream
  workflow stages.
- The user understands that the batch script starts again from the beginning.

## Collect Evidence

```bash
squeue -j <job-id> -o "%.18i %.9P %.30j %.8u %.2t %.10M %.6D %R"
scontrol show job <job-id>
```

Record the reason for requeue in the support ticket, pull request, lab notes,
or site-approved change log without exposing private hostnames or allocations.

## Avoid Requeue When

- The workload is not idempotent.
- Final outputs may be overwritten or mixed with partial outputs.
- The checkpoint format changed since the previous run.
- The job failed because of a persistent input, license, quota, permission, or
  software environment problem.
- Site policy requires admin review for the relevant partition or QOS.
