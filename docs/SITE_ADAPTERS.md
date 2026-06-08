# Site Adapters

Site adapters let HPC centers describe local policy and infrastructure without
forking core skills.

Core skills should stay portable. A site adapter answers local questions:

- Which Slurm partitions should users choose?
- What account or allocation placeholders should examples use?
- Which modules are recommended for MPI, GPU, Python, containers, or workflows?
- Which storage paths are durable, temporary, backed up, or high-throughput?
- Which generic skill examples need local warnings or substitutions?

## Directory Layout

```text
site-adapters/
  example-campus-cluster/
    site.json
    README.md
```

`site.json` is machine-readable metadata. `README.md` explains local assumptions
in human terms.

## Adapter Status

- `example`: Demonstrates format only.
- `draft`: Proposed by a site or user group.
- `reviewed`: Reviewed by maintainers for structure and safe public content.
- `deprecated`: Kept for history, but no longer recommended.

## Contribution Guidance

- Use public-facing names and URLs only.
- Use placeholders for accounts, projects, users, hostnames, and internal paths.
- Do not publish private cluster topology, security procedures, or unpublished
  service endpoints.
- Prefer policy summaries over long local documentation copies.
- Link to public site documentation when available.

## How Skills Use Adapters

A future CLI can combine:

1. A core skill such as `slurm-submit-job`.
2. A site adapter such as `example-campus-cluster`.
3. User inputs such as wall time, memory, partition, or container image.

The result can be a site-aware script or checklist while preserving a clean,
portable core registry.
