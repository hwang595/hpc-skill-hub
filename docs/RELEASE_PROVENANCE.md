# Release Provenance

Tagged HPC Skill Hub releases use GitHub artifact attestations to bind the
release manifest, source distribution, and wheel to the GitHub Actions workflow
that built them.

The `Package` workflow runs [`actions/attest@v4`](https://github.com/actions/attest)
only for tags matching `v*`. Pull request and ordinary branch builds still
build and test distributions, but they do not create release attestations.

## Attested Subjects

For a tag such as `v0.5.0`, the workflow attests:

- `registry/releases/v0.5.0.json`
- every source distribution under `dist/`
- every wheel under `dist/`

The wheel job tests distributions with read-only repository permission and
uploads the exact files as a workflow artifact. A separate tag-only attestation
job downloads those tested files, generates signed build provenance using a
short-lived Sigstore certificate, and uploads the attestation to GitHub's
attestations API. Only that tag-only job receives `id-token: write` and
`attestations: write`.

## Verification

After downloading a release artifact, verify its attestation against the public
repository:

```bash
gh attestation verify <artifact-path> \
  --repo <owner>/hpc-skill-hub
```

Verification proves that the artifact digest was attested by this repository's
GitHub Actions workflow. It does not replace review of the release manifest,
skill security findings, maturity evidence, or the source commit.

## Recorded Verification

After verification, maintainers record the public release facts in
`registry/provenance/<version>.json`. The schema-bound receipt includes the tag
and commit, release and workflow URLs, completion timestamps, exact artifact
names and SHA-256 digests, and the `gh-attestation-verify` outcome. The current
receipt is included in installed package data, and
`registry/release-status.json` opens the provenance gate only when the receipt
matches the immutable release manifest.

The checked-in receipt is an auditable maintainer record, not a replacement for
the GitHub/Sigstore attestation. Consumers that need cryptographic verification
should download the named subject and run `gh attestation verify` themselves.

Before publishing a release, confirm that:

1. The tag points at the reviewed release commit.
2. The versioned release manifest is committed and passes immutable snapshot
   validation.
3. The tag-triggered `Package` workflow succeeds.
4. Each attached release artifact passes `gh attestation verify`.
5. The GitHub release notes link the source commit and versioned manifest.
6. The provenance receipt records the verified subject digests and successful
   tag workflow without changing the published manifest.

GitHub documents the permission and verification model in
[Using artifact attestations to establish provenance for builds](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).
