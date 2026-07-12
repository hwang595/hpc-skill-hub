# Release Provenance

Tagged HPC Skill Hub releases use GitHub artifact attestations to bind the
release manifest, source distribution, and wheel to the GitHub Actions workflow
that built them.

The `Package` workflow runs [`actions/attest@v4`](https://github.com/actions/attest)
only for tags matching `v*`. Pull request and ordinary branch builds still
build and test distributions, but they do not create release attestations.

## Attested Subjects

For a tag such as `v0.3.0`, the workflow attests:

- `registry/releases/v0.3.0.json`
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

Before publishing a release, confirm that:

1. The tag points at the reviewed release commit.
2. The versioned release manifest is committed and passes immutable snapshot
   validation.
3. The tag-triggered `Package` workflow succeeds.
4. Each attached release artifact passes `gh attestation verify`.
5. The GitHub release notes link the source commit and versioned manifest.

GitHub documents the permission and verification model in
[Using artifact attestations to establish provenance for builds](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).
