# Slurm Job Dependency Chain

Use this skill when a workflow has a small number of ordered stages and a full
workflow engine would be too much machinery. Typical examples are preprocess,
analyze, and postprocess/report steps.

## Example

Plan the dependency chain without submitting jobs:

```bash
bash examples/dependency-chain.sh --plan /tmp/dependency-demo
```

Submit the generated demo chain only after reviewing the scripts and local
policy:

```bash
bash examples/dependency-chain.sh --submit /tmp/dependency-demo
```

## Dependency Patterns

- `afterok:<jobid>` starts the next stage only after the previous job exits
  successfully.
- `afterany:<jobid>` starts the next stage after the previous job ends with any
  state, which is useful for cleanup or reporting.
- `afternotok:<jobid>` is useful for failure handlers.
- `singleton` can serialize jobs with the same name and user.

Use `afterok` for expensive downstream compute that should not run after a
failed input stage. Use `afterany` for lightweight reporting, cleanup, or log
collection that should run even if an earlier stage fails.

## Safety Notes

This skill is `medium` risk because `--submit` creates Slurm jobs. The default
mode is `--plan`, which only writes demo scripts and prints the intended
`sbatch` commands. Keep initial tests short, avoid large arrays in dependency
chains, and confirm site policy before building many-stage workflows.

## Success Criteria

- The plan records each stage script and dependency type.
- Downstream jobs use the intended upstream job id.
- Cleanup/report stages use `afterany` only when they are safe after failures.
- Logs are distinct for every stage.
- The user can rerun or replace a failed stage without resubmitting unrelated
  work.
