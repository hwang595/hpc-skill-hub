# Performance Profile Basic

Use this skill when a workload is slow, memory hungry, or unexpectedly variable
and the user needs first-pass evidence before deeper profiling.

## Example

```bash
bash examples/profile-command.sh ./my_program --input data.txt
```

## Output

The script creates a timestamped directory with:

- command metadata.
- `/usr/bin/time -v` output when available.
- GPU telemetry when `nvidia-smi` is available.
- process exit code.

## Safety Notes

The wrapper itself is `low` risk, but the command being profiled may allocate
compute time, write files, or consume large resources.
