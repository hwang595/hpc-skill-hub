# NERSC Perlmutter Public Adapter

This draft site adapter maps portable HPC Skill Hub guidance to public NERSC
Perlmutter documentation. It is not an official NERSC-maintained adapter and
should remain `draft` until reviewed by NERSC staff or maintainers with current
site knowledge.

## Public Assumptions

- Perlmutter uses Slurm for batch scheduling.
- Perlmutter jobs should specify a NERSC project account and an architecture
  constraint such as `cpu` or `gpu`.
- Most production jobs should use the `regular` QOS; `debug` is for code
  development, testing, and debugging.
- Perlmutter uses Lmod for modules.
- Perlmutter scratch should be referenced through `$SCRATCH` or `$PSCRATCH` and
  is temporary, purged storage.
- NERSC recommends Globus and data transfer nodes for significant data
  movement.
- NERSC documents Shifter and podman-hpc container workflows; generic
  Apptainer examples should be adapted through site review.

## Useful Skill Overrides

- `slurm-submit-job`: add NERSC account, QOS, and CPU/GPU constraints.
- `gpu-sanity-check`: request GPU nodes and explicit GPU resources.
- `dataset-staging-to-scratch`: use `$SCRATCH` or `$PSCRATCH` for active job
  I/O and move important outputs to durable storage.
- `globus-transfer-dataset`: prefer the NERSC DTN Globus endpoint for large
  transfers.
- `apptainer-run-container`: translate generic container guidance to NERSC
  Shifter or podman-hpc documentation.

## What This Adapter Avoids

- Private hostnames beyond public documentation links.
- Usernames, project ids, tokens, allocation names, or internal paths.
- Exact queue limits that should be checked against current NERSC policy.
- Operational details that belong in private site documentation.

## Public References

- [Running Jobs on Perlmutter](https://docs.nersc.gov/systems/perlmutter/running-jobs/)
- [NERSC Queue Policies](https://docs.nersc.gov/jobs/policy/)
- [NERSC Resource Usage Policies](https://docs.nersc.gov/policies/resource-usage/)
- [NERSC Filesystems Overview](https://docs.nersc.gov/filesystems/)
- [Perlmutter Scratch](https://docs.nersc.gov/filesystems/perlmutter-scratch/)
- [NERSC Data Transfer Nodes](https://docs.nersc.gov/systems/dtn/)
- [NERSC Globus](https://docs.nersc.gov/services/globus/)
- [NERSC Lmod](https://docs.nersc.gov/environment/lmod/)
- [NERSC Containers](https://docs.nersc.gov/development/containers/)
