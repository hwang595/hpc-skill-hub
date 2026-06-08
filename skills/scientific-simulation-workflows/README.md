# Scientific Simulation Workflows

Use this skill when a researcher or support engineer needs a conservative,
reviewable workflow for preparing, running, checking, and post-processing
scientific simulation jobs on HPC systems.

This is an umbrella skill. Prefer the domain-specific skills for detailed
software launch patterns, such as `gromacs-on-slurm`, `lammps-on-slurm`,
`namd-on-slurm`, `openfoam-on-slurm`, `wrf-on-slurm`,
`quantum-espresso-on-slurm`, and `cp2k-on-slurm`.

## Examples

Create a plan-only packet for a small simulation run:

```bash
SIM_SOFTWARE=gromacs \
SIM_INPUTS="topol.top conf.gro smoke.mdp" \
SIM_COMMAND="gmx grompp -f smoke.mdp -c conf.gro -p topol.top -o smoke.tpr" \
bash examples/simulation-run-plan.sh
```

Scan one or more existing logs:

```bash
python3 examples/check-simulation-log.py --log run.log --log scheduler.err
```

Write JSON for downstream support tickets or review packets:

```bash
python3 examples/check-simulation-log.py --json --log run.log
```

## Pattern

- Identify the simulation family and choose the most specific available skill.
- Check required input files before submitting or scaling jobs.
- Record software, executable, scheduler template, MPI/OpenMP/GPU settings,
  working directory, hostname, and relevant scheduler variables.
- Start with a small smoke run or public tutorial case before production
  inputs.
- Review log output for memory, MPI, GPU, convergence, license, filesystem,
  and walltime signals.
- Keep post-processing commands separate from simulation launch commands.
- Save enough notes for another person to reproduce the environment and task
  shape.

## Software Families

| Domain | Common software | Follow-up skills |
| --- | --- | --- |
| Molecular dynamics | GROMACS, LAMMPS, NAMD | `gromacs-on-slurm`, `lammps-on-slurm`, `namd-on-slurm` |
| CFD | OpenFOAM | `openfoam-on-slurm` |
| Weather and climate | WRF | `wrf-on-slurm` |
| Materials and electronic structure | Quantum ESPRESSO, CP2K, VASP | `quantum-espresso-on-slurm`, `cp2k-on-slurm` |
| Computational chemistry | Gaussian, ORCA | `license-aware-slurm-job`, `reproducible-run-capture` |
| Multiphysics and finite elements | COMSOL, ANSYS, Abaqus | `license-aware-slurm-job`, `reproducible-run-capture` |

## Safety Notes

This skill is `medium` risk because simulation workloads can consume many CPU
or GPU hours, write large output trees, and expose private project paths in
logs. The run-plan example defaults to plan-only mode. It does not submit jobs,
move data, delete data, or run `SIM_COMMAND` unless `RUN_SIMULATION=1` is set.

Review generated notes before sharing them publicly. Logs can contain usernames,
project identifiers, allocation names, file paths, and unpublished input names.

## Success Criteria

- The run plan records software, command, scheduler template, input checks,
  output location, and explicit launch/post-processing notes.
- Reproducibility notes include scheduler, MPI/OpenMP/GPU, and version context
  that can be reviewed before scaling.
- Log triage highlights common failure categories with line numbers and
  suggested follow-up checks.
- The user can decide whether to use a domain-specific skill, run a small smoke
  test, adjust resources, or collect more evidence before production runs.
