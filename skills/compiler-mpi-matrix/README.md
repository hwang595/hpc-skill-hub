# Compiler MPI Matrix

Use this skill when an application build or MPI run may be using mismatched
compiler, MPI, module, or library paths.

## Example

Collect a report after loading the intended compiler and MPI modules:

```bash
bash examples/compiler-mpi-report.sh
```

To opt into a tiny MPI compile smoke test:

```bash
COMPILE_SMOKE=1 bash examples/compiler-mpi-report.sh
```

## What To Look For

- `mpicc`, `mpicxx`, and `mpifort` wrappers from the same MPI installation.
- Compiler wrappers showing the expected underlying compiler family.
- Loaded modules that mix incompatible compiler or MPI families.
- `LD_LIBRARY_PATH`, `LIBRARY_PATH`, `CPATH`, and `CMAKE_PREFIX_PATH` pointing
  to the intended stack.
- `ldd` output that resolves libraries from the same stack as the compiler.

## Safety Notes

This skill is `low` risk. The default report is read-only. The optional smoke
compile writes a small user-owned binary into the report directory and does not
submit a job.

## Success Criteria

- The report records loaded modules and compiler/MPI wrapper paths.
- MPI wrappers reveal the expected compiler underneath.
- Optional smoke compilation succeeds with the same wrapper intended for the
  application.
- Evidence can be attached to a support request without private paths if
  sensitive values are redacted.
