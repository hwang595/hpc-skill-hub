# TensorFlow Multiworker On Slurm

Use this skill when a TensorFlow or Keras workload uses
`tf.distribute.MultiWorkerMirroredStrategy` and needs a small Slurm smoke test
before real training.

## Example

Edit account, partition, resource requests, environment setup, and
`TF_WORKER_PORT`, then submit a dry run:

```bash
sbatch examples/tensorflow-multiworker.sbatch
```

The example prints the selected worker addresses, task count, worker port,
`TF_CONFIG` inputs, GPU visibility, and launch command. After reviewing the
plan, submit with:

```bash
RUN_TENSORFLOW_SMOKE=1 sbatch examples/tensorflow-multiworker.sbatch
```

## Pattern

- Start with one short GPU allocation before scaling across nodes.
- Load or activate the same TensorFlow environment used by the real training
  job.
- Run one TensorFlow worker task per Slurm node for the first smoke test.
- Build the TensorFlow worker list from `scontrol show hostnames` and a fixed
  worker port.
- Set `TF_CONFIG` before importing TensorFlow.
- Map `SLURM_PROCID` to the TensorFlow task index.
- Keep the smoke test separate from model training so package, scheduler, GPU,
  and collective issues are easier to isolate.

## Safety Notes

This skill is `medium` risk because it requests GPU resources and can start
multiple distributed worker processes. Keep wall time short, start with one
node, avoid real datasets in the smoke test, and confirm site policy before
opening ports across nodes. The included Python script does not download models,
read datasets, write checkpoints, or push to external services.

## Success Criteria

- Every Slurm task starts on the expected node.
- `TF_CONFIG` contains the expected worker list and task index.
- The smoke script imports TensorFlow successfully.
- The selected distribution strategy reports the expected number of replicas.
- A tiny tensor reduction completes and every worker reports `status=ok`.
