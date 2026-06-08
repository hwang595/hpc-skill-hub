# License-Aware Slurm Job

Use this skill when a workload depends on limited licensed software and the
job should request the matching Slurm license resource before it starts. This
is useful for MATLAB, commercial simulation tools, EDA tools, compilers, or
other applications where users can otherwise start a job that later fails
because the license seat is unavailable.

## Example

Run the planner in dry-run mode first:

```bash
ACCOUNT=<account> \
PARTITION=<partition> \
LICENSE_RESOURCE=<license-resource> \
LICENSE_COUNT=1 \
APP_MODULE=<module-name> \
APP_COMMAND='hostname' \
  bash examples/license-aware-slurm-job.sh
```

The planner writes a read-only status report and prints the `sbatch` command it
would use. To submit only the dry-run Slurm template:

```bash
SUBMIT_LICENSED_JOB=1 \
RUN_LICENSED_APP=0 \
ACCOUNT=<account> \
PARTITION=<partition> \
LICENSE_RESOURCE=<license-resource> \
LICENSE_COUNT=1 \
APP_MODULE=<module-name> \
APP_COMMAND='hostname' \
  bash examples/license-aware-slurm-job.sh
```

Set `RUN_LICENSED_APP=1` only after the account, partition, license resource,
module, and command have been reviewed on the target site.

If a site permits read-only license-manager checks, set `LMUTIL_LICENSE_SPEC`
for the planner. Do not publish private license server names, ports, feature
names, or raw status output in public issues or examples.

## Pattern

- Confirm whether the site tracks the application through Slurm licenses,
  external license-manager tooling, both, or neither.
- Use `scontrol show lic` when visible to users to inspect configured Slurm
  license resources.
- Keep the license request explicit with `sbatch --licenses=<resource>:<count>`
  or a reviewed `#SBATCH --licenses=` line.
- Submit a tiny dry-run job with `RUN_LICENSED_APP=0` before running the
  licensed command.
- Load only the required application module.
- Run a small representative command before production workloads.
- Record job id, module, command, requested license resource, and optional
  status evidence in user-owned logs.

## Safety Notes

This skill is `medium` risk because it can submit Slurm jobs and may reserve
scarce license tokens. The default planner does not submit a job. The template
does not run the licensed application unless `RUN_LICENSED_APP=1` is set.
License names and status output may reveal local policy, vendor usage, or
private server details, so sanitize evidence before sharing it publicly.

## Success Criteria

- The planner records visible Slurm license evidence or clearly reports that
  it is unavailable to the user.
- The printed `sbatch` command includes the expected `--licenses` request.
- The first submitted job exits before running the application when
  `RUN_LICENSED_APP=0`.
- A tiny licensed command runs only after explicit review with
  `RUN_LICENSED_APP=1`.
- Public documentation uses placeholders or site adapters instead of private
  license server details.
