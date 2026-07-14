# Citation

If HPC Skill Hub helps your work, cite the release or commit you used. This
matters because skills, schemas, examples, and safety guidance can change over
time.

## Recommended Citation

Use [CITATION.cff](../CITATION.cff) as the source of truth for citation
metadata. After the repository is published on GitHub, cite the tagged release
URL for the version you used.

For the current release candidate (cite its commit until the tag is published):

```text
HPC Skill Hub Maintainers. HPC Skill Hub. Version 0.5.0.
Open registry of reusable, reviewable skills for high performance computing
workflows.
```

## What To Cite

- Cite a release tag when using a published version.
- Cite a commit hash when relying on unreleased behavior.
- Cite the relevant upstream tool, workflow engine, or scientific software
  project separately when a skill integrates that project.
- Cite local site documentation separately when your work depends on a site
  adapter or local cluster policy.

## Updating Citation Metadata

When cutting a release, maintainers should review:

- `CITATION.cff`
- `docs/RELEASE_NOTES_v<version>.md`
- `CHANGELOG.md`
- Any DOI or archive metadata created outside this repository
