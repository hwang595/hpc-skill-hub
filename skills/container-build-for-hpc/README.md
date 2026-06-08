# Container Build For HPC

Use this skill when a user needs to create an Apptainer/Singularity-compatible
image for an HPC workload.

## Example

Record a build plan without building:

```bash
bash examples/build-plan.sh examples/Container.def my-image.sif
```

Build only after confirming site policy and filesystem location:

```bash
BUILD_IMAGE=1 bash examples/build-plan.sh examples/Container.def my-image.sif
```

## Pattern

- Keep the definition file in version control.
- Build in a site-approved location, not on a busy login filesystem.
- Use user-owned cache and output paths.
- Record runtime, host, command, and definition file path.
- Test the resulting image with a small command before submitting production
  jobs.

## Safety Notes

This skill is `medium` risk because image builds can download layers, write
large files, and stress shared filesystems. The example defaults to plan-only
mode and requires `BUILD_IMAGE=1` before it runs a build command.

## Success Criteria

- The build plan records the exact command and runtime.
- The SIF output path is user-owned and on a suitable filesystem.
- The image runs a small inspection command with `apptainer exec`.
- Build logs are kept with enough metadata for support or reproducibility.
