# mpi4py On Slurm

Use this skill when a Python workload uses `mpi4py` and should run across
multiple Slurm tasks with a clear MPI module, Python environment, launcher, log,
and output pattern.

## Example

Review the account, partition, MPI module, and optional Python environment
placeholders, then submit from this skill directory:

```bash
sbatch examples/mpi4py-slurm.sbatch
```

To run a different script or activate a prepared Python environment:

```bash
MPI_MODULE=<site-mpi-module> \
PYTHON_ENV=/path/to/venv \
PYTHON_SCRIPT=path/to/my_mpi_program.py \
OUTPUT_DIR=results/mpi4py-run \
  sbatch examples/mpi4py-slurm.sbatch
```

Use the same MPI implementation at install time and run time. A common failure
mode is building or installing `mpi4py` against one MPI implementation, then
loading a different MPI module before launching the job.

## Pattern

- Load the site MPI module that matches the `mpi4py` package.
- Activate the prepared Python environment after loading MPI.
- Check `python -c "from mpi4py import MPI"` before launching ranks.
- Prefer the site-recommended launcher. The example uses `srun`; some MPI
  stacks may require `mpiexec` or additional Slurm MPI flags.
- Keep logs and outputs under explicit directories.
- Record Python version, executable path, MPI library version, rank layout, and
  launcher choice in the job log.
- Keep package installation separate from production runs unless the site
  explicitly supports package builds on compute nodes.

## Safety Notes

This skill is `medium` risk because it submits multi-task jobs and can amplify
environment mistakes across many ranks. Start with a short, small allocation.
Avoid mixing MPI wheels, Conda MPI packages, and site MPI modules unless you
have confirmed compatibility with local support guidance.

## Success Criteria

- `sbatch` accepts the script after site placeholders are replaced.
- Every rank prints the expected world size and a hostname.
- The log records the Python executable, Python version, mpi4py version, and
  MPI library version.
- Rank report outputs are written under the requested output directory.
- The MPI implementation used by `mpi4py` matches the runtime launcher and site
  module.
