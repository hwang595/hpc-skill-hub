# WDL On Slurm

Use this skill when a workflow author wants to run a small Workflow
Description Language workflow with `miniwdl` inside a Slurm allocation using
explicit run directory, input JSON, output JSON, and provenance controls.

## Example

Create a launch plan with the bundled tiny WDL workflow:

```bash
sbatch examples/wdl-smoke.sbatch
```

After loading a site-approved `miniwdl` environment, run the smoke test:

```bash
RUN_WDL=1 sbatch examples/wdl-smoke.sbatch
```

Adapt it to a real WDL document:

```bash
RUN_WDL=1 \
WDL_DOCUMENT=/path/to/workflow.wdl \
WDL_INPUT_JSON=/path/to/inputs.json \
WDL_RUN_DIR=/path/to/wdl-runs \
  sbatch examples/wdl-smoke.sbatch
```

## Pattern

- Run `miniwdl` inside a Slurm allocation for small or moderate local WDL
  workflows.
- Use a workflow engine configuration reviewed for the site before scaling to
  scatter-heavy or container-heavy workflows.
- Put `WDL_RUN_DIR` on scratch or project storage suitable for task working
  directories.
- Preserve the exact WDL document, input JSON, miniwdl version, output JSON,
  and launch command with the run record.
- Start with the bundled smoke test and then a small representative input
  before production-scale data.

## Safety Notes

This skill is `medium` risk because WDL workflows can launch arbitrary command
line tasks, produce large intermediate directories, and may invoke containers
depending on workflow requirements. The wrapper defaults to dry-run mode and
runs `miniwdl` only when `RUN_WDL=1` is set. Review container, network,
filesystem, and runtime-default policy before running external WDL workflows.

## Success Criteria

- The dry-run log records the WDL document, input JSON, run directory, output
  JSON path, miniwdl executable, optional runtime defaults, and Slurm allocation
  details.
- With `RUN_WDL=1`, `miniwdl run` writes an output JSON and creates a run
  directory under the configured location.
- The run record captures miniwdl version and command provenance.
- Workflow task directories are kept away from fragile home directories.
