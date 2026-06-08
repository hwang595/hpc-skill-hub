# Quantum ESPRESSO On Slurm

Use this skill when a simulation team wants to run Quantum ESPRESSO `pw.x`
jobs on Slurm with explicit MPI layout, pseudopotential, scratch, output, and
restart controls.

## Example

Create a dry-run launch plan:

```bash
sbatch examples/qe-pwscf-smoke.sbatch
```

After loading a site-approved Quantum ESPRESSO module or container and placing
the required pseudopotential in a durable directory, run the small SCF example:

```bash
RUN_QE=1 \
QE_PSEUDO_DIR=/path/to/pseudopotentials \
  sbatch examples/qe-pwscf-smoke.sbatch
```

The bundled silicon template references `Si.pbe-n-kjpaw_psl.1.0.0.UPF`.
Replace the template or pseudopotential filename to match your site's reviewed
pseudopotential policy.

## Pattern

- Start with a short SCF smoke test before relaxations, phonons, large k-point
  grids, or production cutoffs.
- Put `outdir` on scratch or project storage designed for parallel I/O.
- Use `wfcdir` intentionally; node-local storage can help performance but may
  require copying files back before restarts or follow-on calculations.
- Keep the generated input file, stdout, module/container evidence, and Slurm
  allocation details together.
- Use `QE_MAX_SECONDS` below the Slurm wall time so `pw.x` can stop cleanly
  before the scheduler kills the job.
- Keep pseudopotential files versioned and documented in the run record.

## Safety Notes

This skill is `medium` risk because Quantum ESPRESSO jobs can consume many MPI
ranks, write large wavefunction files, and stress shared filesystems. The
wrapper defaults to dry-run mode and executes `pw.x` only when `RUN_QE=1` is
set. Keep smoke tests short, review pseudopotentials and cutoffs with a domain
expert, and use site-approved scratch paths for `outdir` and `wfcdir`.

## Success Criteria

- The launch plan records MPI layout, executable, input template, generated
  input path, pseudopotential directory, scratch paths, and wall-time guard.
- With `RUN_QE=1`, `pw.x` starts through Slurm and writes the configured output
  file.
- The generated input and output are preserved with the run record.
- Restart state under `outdir` and `wfcdir` is documented before follow-on
  calculations.
