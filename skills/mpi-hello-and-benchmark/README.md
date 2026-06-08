# MPI Hello And Benchmark

Use this skill to confirm that the selected compiler, MPI module, Slurm launcher,
and node allocation work together.

## Example

```bash
sbatch examples/run-mpi.sbatch
```

## Success Criteria

- `mpicc` compiles `hello_mpi.c`.
- Output shows the expected number of ranks.
- Hostnames show whether ranks were placed across one or more nodes.

## Safety Notes

This skill is `medium` risk because it submits a job, but the default workload is
short and lightweight.
