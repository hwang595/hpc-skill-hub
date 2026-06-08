# Reproducible Run Capture

Use this skill when a result, failure, or support request needs enough context
for another person to understand how a command was run.

## Example

Capture a short command:

```bash
bash examples/capture-run.sh python my_script.py --input data.txt
```

Optionally checksum a small manifest of input files:

```bash
INPUT_MANIFEST=examples/input-files.txt bash examples/capture-run.sh ./my_program
```

## Captured Evidence

- command and arguments.
- working directory, hostname, timestamp, and kernel details.
- loaded modules when the module command is available.
- sorted environment variables.
- git commit and dirty-state summary when run inside a git checkout.
- optional input checksums.
- stdout, stderr, and exit code.

## Safety Notes

This skill is `low` risk as a wrapper, but the command being captured may submit
jobs, write files, move data, or consume resources. Captured logs can contain
private paths, project names, usernames, or dataset identifiers, so review
output before sharing publicly.

## Success Criteria

- The capture directory contains command, metadata, environment, stdout, stderr,
  and exit-code files.
- A collaborator can identify the code version, input list, and environment.
- Sensitive paths or identifiers are redacted before attaching to public issues.
