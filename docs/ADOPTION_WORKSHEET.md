# Adoption Pilot Worksheet

Use this worksheet during a small HPC Skill Hub pilot. It helps a center,
research group, tool maintainer, or instructor separate public-safe findings
from private operational notes before opening issues or pull requests.

See [Adopter Playbook](ADOPTER_PLAYBOOK.md), [Adoption Guide](ADOPTION_GUIDE.md),
and [Site Adapters](SITE_ADAPTERS.md) for the surrounding process.

## Pilot Metadata

| Field | Public-safe answer |
| --- | --- |
| Pilot track | HPC center / research group / tool maintainer / instructor |
| Environment type | Campus Slurm / training cluster / cloud HPC / lab cluster / other |
| Public documentation URLs |  |
| Collection under review |  |
| Contact role | Maintainer / RSE / support staff / instructor / user |
| Review window | 30 day / 60 day / 90 day |

## Collections And Skills Tried

| Collection or skill | What was reviewed | Result | Follow-up |
| --- | --- | --- | --- |
|  | README / example / manifest / CLI output | worked / unclear / needs adapter / needs skill request |  |

## Local Adaptation Notes

Record only public-safe patterns here. Keep private findings in local notes.

| Topic | Public-safe note | Belongs in |
| --- | --- | --- |
| Partitions or queues |  | site adapter / skill request / docs |
| Storage classes |  | site adapter / skill request / docs |
| Module names |  | site adapter / skill request / docs |
| Container runtime |  | site adapter / skill request / docs |
| Data transfer tools |  | site adapter / skill request / docs |
| Workflow engine defaults |  | site adapter / skill request / docs |
| Safety or cost concern |  | safety review / skill request / docs |

## Evidence To Publish

Good public evidence includes public docs links, redacted command output, small
synthetic smoke tests, and environment descriptions that do not identify private
systems.

| Evidence | Public location or placeholder |
| --- | --- |
| Public docs link |  |
| Redacted command output |  |
| Small input or smoke-test description |  |
| Skill request title |  |
| Site adapter request title |  |
| Maturity review title |  |

## Public-Safe Checklist

- [ ] No private hostnames, login nodes, service endpoints, or topology details.
- [ ] No usernames, account names, allocation names, project ids, or tokens.
- [ ] No private storage paths, dataset names, support tickets, or incident ids.
- [ ] No unpublished security, identity, quota, accounting, or node procedures.
- [ ] Placeholders use forms such as `<account>`, `<partition>`,
      `/project/<project>`, and `/scratch/<user>`.
- [ ] Any risky action is framed as a safety review before being proposed as a
      skill or adapter change.

## 30 Day Checkpoint

- [ ] One collection or domain area was reviewed.
- [ ] Three to five skills were checked against local public documentation.
- [ ] Missing workflows were captured as candidate skill requests.
- [ ] Any site-specific public policy was captured as a site adapter candidate.
- [ ] Private findings were kept out of public issues.

## 60 Day Checkpoint

- [ ] A draft site adapter, skill request, or documentation pull request exists.
- [ ] `python3 tools/hpc_skill.py validate` and `make check` pass locally.
- [ ] A domain reviewer has been identified.
- [ ] Safety-sensitive findings have a safety review issue or local owner.

## 90 Day Checkpoint

- [ ] Public-safe outcomes are summarized in an adoption report issue.
- [ ] Any field-tested skill has public evidence for maturity review.
- [ ] One owner is named for follow-up review or adapter maintenance.
- [ ] Remaining gaps are tracked as issues instead of private patches.

## Suggested Public Summary

```markdown
Track:
Environment type:
Collection or skill reviewed:
What worked:
What needed a site adapter:
Public docs used:
Next contribution:
```
