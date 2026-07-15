# Quarantined Community Intake

Community contributions are untrusted before their instructions, examples, or
metadata enter an agent context. The v0.6 P1 intake command establishes a
bounded, no-execution review boundary for a directory, ZIP archive, or TAR
archive:

```bash
hpc-skill intake ./community-skill --json
hpc-skill intake ./community-skill.zip --json
python3 tools/quarantine_skill_intake.py ./community-skill.tar.gz --json
```

Do not read `SKILL.md`, README files, examples, or embedded instructions before
running intake. A successful P1 result makes a bundle eligible for human
review; it does not accept the skill or authorize context loading.

## Intake Sequence

The command performs these steps without executing package content or using the
network:

1. Identify a regular directory, ZIP archive, or TAR archive. A symbolic-link
   source is blocked.
2. Create a temporary quarantine workspace outside the contribution.
3. Inventory normalized relative paths and enforce structural and resource
   limits before writing accepted file bytes.
4. Reject links, special files, nested archives, executable or opaque binary
   content, and non-UTF-8 review text.
5. Copy accepted files with non-executable permissions. Archive members are
   read individually; the implementation never calls `extractall`.
6. Run `community-default@0.1.0` against the staged copy only when boundary
   checks have no findings.
7. Remove the quarantine workspace before returning a report.
8. Return paths, byte counts, digests, findings, and scanner provenance without
   returning instruction content or a temporary filesystem path.

Directory trees are traversed through directory file descriptors; every child
directory and file is opened relative to its reviewed parent without following
symbolic links. File identity, type, size, and modification metadata are
checked before and after the bounded read to detect source replacement. A
platform without the required descriptor-relative primitives fails closed and
asks the operator to provide a ZIP or TAR snapshot instead.

## Default Limits

| Boundary | Default |
| --- | ---: |
| Compressed archive bytes | 5,000,000 |
| Directory or archive entries | 512 |
| Regular files | 256 |
| Bytes per file | 1,000,000 |
| Total regular-file bytes | 5,000,000 |
| Compression ratio | 100:1 |
| Relative path depth | 12 components |
| Relative path length | 240 UTF-8 bytes |

Portable case-insensitive path collisions, absolute or Windows drive paths,
`..` traversal, control characters, Windows reserved names, ambiguous trailing
dots or spaces, reserved VCS/cache/build directories, encrypted ZIP members,
TAR hard links, and file/directory prefix aliases are blocked. ZIP and TAR
containers, including gzip-, bzip2-, and xz-compressed TAR files supported by
the Python standard library, are accepted as top-level inputs. Nested archives
are not recursively opened.

## Status And Exit Codes

Reports follow
[`community-skill-intake-report.schema.json`](../schemas/community-skill-intake-report.schema.json).

| Status | Meaning | CLI exit |
| --- | --- | ---: |
| `ready-for-review` | Boundary checks passed and the security policy returned `pass`. Human review is still required. | 0 |
| `review-required` | The scanner returned `review` or `pass-with-exceptions`. Review every finding and exact exception binding. | 0 |
| `blocked` | A boundary check failed or the scanner returned `block`. Do not load or adopt the content. | 1 |

Missing inputs, unsupported containers, invalid external policies, unreadable
files, or other operational failures exit `2` and write an error to stderr.
Every structured report sets `summary.context_loading_allowed` to `false` and
records that no execution occurred and no instruction content was returned.

## External Policy

An operator-reviewed policy may strengthen the packaged baseline:

```bash
hpc-skill intake ./community-skill.zip \
  --policy ../review-policy.json \
  --json
```

The policy must live outside the contribution. A package cannot grant itself
exceptions. Existing monotonic severity, expiration, exact-finding digest, and
redaction rules continue to apply; see [Trust Policy Packs](TRUST_POLICY_PACKS.md).

## P1 Boundary

P1 reports prove only that the local parser, limits, quarantine cleanup, and
static policy behaved as recorded for the observed input. They are not durable
acceptance receipts and do not prove operational correctness, maintainer
approval, independent review, adoption, maturity, or agent performance. P2 will
bind reviewer disposition and accepted context digests to a portable receipt.
