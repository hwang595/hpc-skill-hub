# Hugging Face Accelerate On Slurm

Use this skill when a Transformers, Diffusers, or native PyTorch workload uses
Hugging Face Accelerate and needs a small Slurm smoke test before real training.

## Example

Edit account, partition, resource requests, environment setup, and
`ACCELERATE_PROCESSES_PER_NODE`, then submit a dry run:

```bash
sbatch examples/accelerate-slurm.sbatch
```

The example prints the selected main process address, machine count, total
process count, mixed precision setting, and launch command. After reviewing the
plan, submit with:

```bash
RUN_ACCELERATE_SMOKE=1 sbatch examples/accelerate-slurm.sbatch
```

## Pattern

- Start with one short GPU allocation before scaling across nodes.
- Load or activate the same Accelerate and PyTorch environment used by the real
  training job.
- Run one launcher task per Slurm node, and let Accelerate spawn local worker
  processes on that node.
- Use the first Slurm node as the main process address.
- Set `--num_machines`, `--num_processes`, `--machine_rank`,
  `--main_process_ip`, and `--main_process_port` explicitly.
- Keep the smoke test separate from model training so package, scheduler, GPU,
  and collective issues are easier to isolate.

## Safety Notes

This skill is `medium` risk because it requests GPU resources and can start
multiple distributed worker processes. Keep wall time short, start with one
node, avoid real datasets in the smoke test, and confirm site policy before
opening ports across nodes. The included Python script does not download models,
read datasets, write checkpoints, or push to external services.

## Success Criteria

- Every Slurm launcher task starts on the expected node.
- `accelerate launch` receives explicit machine count, process count, machine
  rank, main process IP, and port values.
- The smoke script imports Accelerate and PyTorch successfully.
- The Accelerate state reports the expected number of processes.
- A tiny tensor collective completes and rank 0 reports the expected sum.
