# Agent Benchmark Artifacts

Store only redacted artifacts referenced by reviewed result files. Raw harness
output stays outside the repository until a maintainer checks it for private
operational details, credentials, local paths, and unpublished site policy.

Use one directory per `run_id`. Keep final responses, changed-file manifests,
and narrowly selected diffs when they are needed to audit a score. Do not
publish complete private transcripts by default.

The blinded review finalizer stages only the redacted `final-output.txt` for
each scored run. Never commit blind salts, private mappings, raw run roots, or
reviewer working directories.
