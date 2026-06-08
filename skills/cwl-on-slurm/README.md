# CWL On Slurm

Use this skill when a workflow author wants to run a Common Workflow Language
workflow with `cwltool` inside a Slurm allocation using explicit output, cache,
temporary directory, and run record paths.

## Example

Create a launch plan with the bundled tiny CWL tool:

```bash
sbatch examples/cwl-smoke.sbatch
```

After loading a site-approved `cwltool` environment, run the smoke test:

```bash
RUN_CWL=1 sbatch examples/cwl-smoke.sbatch
```

Adapt it to a real CWL document:

```bash
RUN_CWL=1 \
CWL_DOCUMENT=/path/to/workflow.cwl \
CWL_JOB_FILE=/path/to/inputs.yml \
CWL_OUT_DIR=/path/to/results \
  sbatch examples/cwl-smoke.sbatch
```

## Pattern

- Run `cwltool` inside a Slurm allocation for small or moderate local CWL
  workflows.
- Use workflow engines with native batch backends for large scatter-heavy
  workflows that should submit many scheduler jobs.
- Put `CWL_CACHE_DIR`, `CWL_TMP_DIR`, and `CWL_TMP_OUT_DIR` on storage suitable
  for intermediate workflow files.
- Preserve the exact CWL document, job input object, cwltool version, and
  launch command with the run record.
- Start with the bundled smoke test and then a small representative input
  before production-scale data.

## Safety Notes

This skill is `medium` risk because CWL workflows can launch arbitrary command
line tools, produce large intermediate files, and overload shared filesystems if
cache and temporary paths are poorly chosen. The wrapper defaults to dry-run
mode and runs `cwltool` only when `RUN_CWL=1` is set. Review container,
network, and filesystem policy before running external CWL workflows.

## Success Criteria

- The dry-run log records the CWL document, job file, output directory, cache
  directory, temporary directories, cwltool path, and Slurm allocation details.
- With `RUN_CWL=1`, `cwltool` validates the CWL document and writes outputs to
  the configured output directory.
- The run record captures cwltool version and command provenance.
- Intermediate cache and temporary files are kept away from fragile home
  directories.
