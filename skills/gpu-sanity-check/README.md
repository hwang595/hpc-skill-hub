# GPU Sanity Check

Use this skill to separate scheduler allocation, device visibility, GPU runtime,
and Python framework failures before changing an application. It is intended for
a short Slurm smoke test when a GPU job cannot see devices or behaves differently
on login and compute nodes; it is not a performance or burn-in benchmark.

## Prerequisites

- Confirm that the cluster uses Slurm and identify a public or user-supplied GPU
  partition, account, GPU request syntax, and runtime module policy.
- Review the request with the user before consuming a GPU allocation.
- Keep `<account>` and `<gpu-partition>` unresolved until local policy supplies
  them. Do not guess module names, GPU types, constraints, or QOS values.
- The framework probe is optional. A missing PyTorch installation does not prove
  that the scheduler or GPU is broken.

## Inputs And Outputs

The input is a reviewed one-GPU Slurm request. The output is `slurm-<job-id>.out`
with scheduler variables, vendor management output, and an optional PyTorch
visibility report. The log reviewer consumes that saved file and writes only a
summary to standard output.

## Workflow

1. Inspect `examples/gpu-sanity.sbatch`; verify account, partition, memory,
   walltime, GPU syntax, and any site-required runtime setup.
2. Replace placeholders with user-approved values. Prefer a debug partition and
   the shortest practical walltime.
3. If the user explicitly approves allocation, submit the reviewed copy with
   `sbatch <reviewed-script>` and record the returned job id.
4. Review the log without another allocation:

   ```bash
   python3 examples/review-gpu-log.py slurm-<job-id>.out
   ```

5. Compare scheduler evidence, vendor CLI evidence, and framework evidence in
   that order. Preserve the original log when escalating to site support.

## Interpreting Results

- Empty allocation variables suggest the probe did not run inside the expected
  job allocation or the site exports different variables.
- A visible allocation but failed `nvidia-smi` or `rocm-smi` points toward the
  node driver, runtime setup, permissions, or a vendor mismatch.
- A working vendor CLI with `torch.cuda.is_available() == False` narrows the
  problem to the Python environment, framework build, or runtime compatibility.
- Multiple visible devices for a one-GPU request can indicate site-specific
  isolation behavior. Do not change device masks until local policy is known.
- A pending or rejected job is a scheduler-policy issue; route it to pending or
  QOS/account triage instead of treating it as GPU runtime evidence.

## Validation

Success means the job ran on a compute node, the scheduler exposed the expected
allocation, exactly the reviewed device set was visible, and at least one
site-supported vendor or framework probe succeeded. Record inconclusive probes
as inconclusive rather than converting them into a pass.

## Resource And Cost

The batch example requests one GPU, four CPUs, 16 GiB of memory, and ten minutes.
Those values consume shared allocation quota even when the probe exits early.
Reduce them only when local policy and the runtime permit; do not scale this
sanity check to multiple nodes or GPUs.

## Cleanup

The probe creates only the Slurm output file in the submission directory. Keep
it for diagnosis or remove it after review according to project retention
policy. Cancel a stuck job with `scancel <job-id>` only after explicit user
approval and confirmation that the id belongs to this test.

## Site Adaptation

GPU request syntax may use GRES, TRES, typed GPUs, constraints, or site wrappers.
Runtime modules and whether vendor CLIs are available also vary. Resolve these
through a public site adapter or user-provided documentation, and redact private
hostnames, accounts, paths, and allocation identifiers before sharing logs.

## Safety Notes

This skill is `medium` risk because it can request scarce GPU resources. The log
reviewer is read-only, but job output may expose hostnames, paths, environment
details, and project identifiers. Never auto-submit the example or publish raw
logs without review.
