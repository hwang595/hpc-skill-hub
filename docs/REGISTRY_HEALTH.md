# Registry Health

This report is generated from `registry/index.json` by `tools/build_health.py`.

## Summary

- Skills: 94
- Site adapters: 2
- Collections: 12
- Uncollected skills: 0

## Risk Distribution

| Risk | Count |
| --- | ---: |
| `low` | 25 |
| `medium` | 69 |

## Maturity Distribution

| Maturity | Count |
| --- | ---: |
| `seed` | 94 |

## Status Distribution

| Status | Count |
| --- | ---: |
| `draft` | 94 |

## Collection Coverage

| Collection | Skills |
| --- | ---: |
| `ai-hpc` | 20 |
| `bioinformatics-workflows` | 7 |
| `containers` | 7 |
| `core-hpc` | 26 |
| `data-movement` | 14 |
| `facility-ops` | 10 |
| `gpu-mpi-performance` | 27 |
| `scheduler-basics` | 10 |
| `simulation-workflows` | 20 |
| `software-stacks` | 30 |
| `training-onboarding` | 27 |
| `workflow-engines` | 11 |

## Uncollected Skills

All skills are included in at least one collection.

## Risk By Skill

| Skill | Risk |
| --- | --- |
| `apptainer-mpi-on-slurm` | medium |
| `apptainer-run-container` | medium |
| `blas-openmp-thread-control` | low |
| `blast-on-slurm` | medium |
| `checkpoint-restart-workflow` | medium |
| `checksum-manifest-create` | low |
| `cluster-usage-report-readonly` | low |
| `cmake-hpc-build-preflight` | medium |
| `compiler-mpi-matrix` | low |
| `conda-mamba-on-hpc` | medium |
| `container-build-for-hpc` | medium |
| `cp2k-on-slurm` | medium |
| `cwl-on-slurm` | medium |
| `darshan-io-profile-analysis` | low |
| `dask-jobqueue-on-slurm` | medium |
| `dataset-staging-to-scratch` | medium |
| `deepspeed-on-slurm` | medium |
| `easybuild-install-software` | medium |
| `file-descriptor-limit-triage` | low |
| `gatk-workflow-on-hpc` | medium |
| `globus-transfer-dataset` | medium |
| `gpu-memory-triage` | low |
| `gpu-sanity-check` | medium |
| `grid-engine-submit-job` | medium |
| `gromacs-on-slurm` | medium |
| `htcondor-submit-job` | medium |
| `huggingface-accelerate-on-slurm` | medium |
| `hybrid-mpi-openmp-slurm` | medium |
| `interactive-session` | medium |
| `ior-mdtest-storage-smoke` | medium |
| `jax-distributed-on-slurm` | medium |
| `job-failure-triage` | low |
| `julia-on-slurm` | medium |
| `jupyter-on-slurm` | medium |
| `lammps-on-slurm` | medium |
| `large-file-archive-prepare` | medium |
| `license-aware-slurm-job` | medium |
| `lsf-submit-job` | medium |
| `lustre-striping-layout-planning` | medium |
| `matlab-batch-on-slurm` | medium |
| `module-environment-debug` | low |
| `module-tree-health-check` | low |
| `mpi-fabric-diagnostics` | medium |
| `mpi-hello-and-benchmark` | medium |
| `mpi-rank-binding-diagnostics` | medium |
| `mpi4py-on-slurm` | medium |
| `namd-on-slurm` | medium |
| `nccl-diagnostics` | medium |
| `nextflow-on-slurm` | medium |
| `nf-core-on-slurm` | medium |
| `node-health-readonly-triage` | low |
| `node-local-scratch-staging` | medium |
| `object-storage-transfer` | medium |
| `open-ondemand-batch-connect` | medium |
| `openfoam-on-slurm` | medium |
| `openmp-thread-affinity` | medium |
| `parallel-hdf5-netcdf-preflight` | medium |
| `parsl-on-slurm` | medium |
| `pbs-submit-job` | medium |
| `performance-profile-basic` | low |
| `python-virtualenv-on-hpc` | low |
| `pytorch-ddp-on-slurm` | medium |
| `quantum-espresso-on-slurm` | medium |
| `quota-and-filesystem-triage` | low |
| `ray-on-slurm` | medium |
| `reproducible-run-capture` | low |
| `rscript-on-slurm` | medium |
| `rstudio-on-slurm` | medium |
| `rsync-data-transfer` | medium |
| `scratch-storage-management` | low |
| `shared-project-permissions-triage` | low |
| `slurm-array-retry-plan` | medium |
| `slurm-efficiency-report` | low |
| `slurm-gpu-binding-diagnostics` | medium |
| `slurm-job-array-patterns` | medium |
| `slurm-job-dependency-chain` | medium |
| `slurm-maintenance-reservation-triage` | low |
| `slurm-monitor-job` | low |
| `slurm-oom-memory-triage` | low |
| `slurm-pending-reason-triage` | low |
| `slurm-preemption-requeue` | medium |
| `slurm-qos-account-limit-triage` | low |
| `slurm-resource-estimator` | low |
| `slurm-submit-job` | medium |
| `slurm-time-limit-triage` | low |
| `snakemake-on-slurm` | medium |
| `spack-environment-create` | medium |
| `streamlit-on-slurm` | medium |
| `tensorboard-on-slurm` | medium |
| `tensorflow-multiworker-on-slurm` | medium |
| `training-cluster-reset-checklist` | medium |
| `vscode-tunnel-on-slurm` | medium |
| `wdl-on-slurm` | medium |
| `wrf-on-slurm` | medium |
