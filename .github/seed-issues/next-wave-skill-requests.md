This issue tracks focused requests that would make good early contributions
after the seed release.

Good next-wave skills should be:

- Small enough to review in one pull request.
- Backed by public references.
- Validatable without private cluster access.
- Clear about scheduler, storage, account, and module assumptions.
- Conservative about resource use and shared-system impact.

Candidate areas:

- `training-cluster-reset-checklist`: repeatable public preflight and cleanup
  guidance for workshops.
- `cwl-on-slurm`: conservative CWL execution patterns for Slurm-backed HPC.
- `wdl-on-slurm`: conservative WDL execution patterns for Slurm-backed HPC.
- `quantum-espresso-on-slurm`: starter simulation skill with MPI sizing and
  restart planning.

Please open separate skill request issues when claiming one so scope, risk, and
validation can be discussed before implementation.
