# Skill Specification

Each skill lives under `skills/<skill-id>/` and must contain `skill.json` and
`README.md`.

## Required Manifest Fields

- `id`: lowercase kebab-case identifier matching the directory name.
- `name`: human-readable name.
- `version`: semantic version for the skill package.
- `status`: `draft`, `reviewed`, or `deprecated`.
- `summary`: one-sentence summary.
- `description`: longer explanation of the task.
- `categories`: one or more supported categories from the schema.
- `tags`: searchable labels.
- `maintainers`: people or teams responsible for the skill.
- `license`: license for examples and documentation.
- `maturity`: `seed`, `reviewed`, `field-tested`, or `maintained`.
- `risk_level`: `low`, `medium`, or `high`.
- `tools`: commands or systems used by the skill.
- `inputs`: expected user inputs.
- `outputs`: files, checks, scripts, or reports produced by the skill.
- `artifacts`: files that must exist inside the skill package.
- `examples`: example files users can adapt.
- `tests`: static, dry-run, manual, or integration validation.
- `references`: upstream documentation links.

## Risk Level Guidance

Use `low` when a skill only reads state, teaches a concept, or generates a
template. Use `medium` when it submits jobs, transfers data, writes user files,
or consumes shared resources. Use `high` when it touches admin state, shared
software stacks, accounting, quotas, node health, or security boundaries.

## README Guidance

Every README should explain:

- When to use the skill.
- What cluster assumptions it makes.
- How to adapt the examples.
- What risks or costs the user should understand.
- How to validate success.

## Example Guidance

Examples should prefer placeholders for site-specific values:

```text
<account>
<partition>
<project>
<cluster>
<collection-id>
```

Scripts should use conservative resource requests and clear output paths.
