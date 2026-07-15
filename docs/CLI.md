# CLI

`tools/hpc_skill.py` is a zero-dependency command-line interface for exploring
the generated registry index and scaffolding new contributions.

Run it from the repository root:

```bash
python3 tools/hpc_skill.py list
python3 tools/hpc_skill.py search slurm
python3 tools/hpc_skill.py show slurm-submit-job --examples
python3 tools/hpc_skill.py collections
python3 tools/hpc_skill.py collection core-hpc
python3 tools/hpc_skill.py health
python3 tools/hpc_skill.py review candidates
python3 tools/hpc_skill.py review status job-failure-triage
python3 tools/hpc_skill.py validate
python3 tools/hpc_skill.py intake ./community-skill.zip --json
python3 tools/hpc_skill.py receipt create ./community-skill.zip --json
python3 tools/hpc_skill.py security skills/slurm-submit-job
python3 tools/hpc_skill.py adapters
python3 tools/hpc_skill.py adapter example-campus-cluster
python3 tools/hpc_skill.py resolve slurm-submit-job --adapter example-campus-cluster
```

Install the package during development to use the `hpc-skill` command:

```bash
python3 -m pip install .
hpc-skill list
hpc-skill collection core-hpc
hpc-skill resolve slurm-submit-job --adapter example-campus-cluster --json
hpc-skill intake ./community-skill.zip --json
hpc-skill receipt create ./community-skill.zip --json
hpc-skill security ./community-skill --format json
```

The installed command can run read-only discovery and review-status commands from the packaged
registry snapshot. When a full checkout is available, it prefers the current
repository's `registry/index.json`, `registry/health.json`, and
`registry/review-status.json`, and `registry/release-status.json`. For commands
that validate or write repository files, run from the repository root or set
`HPC_SKILL_HUB_ROOT` to the repository root.

For code changes without reinstalling:

```bash
PYTHONPATH=src python3 -m hpc_skill_hub collections
```

## Scaffolding Contributions

Create a draft skill:

```bash
python3 tools/hpc_skill.py scaffold skill my-new-skill --category education --tool bash
```

Create a draft site adapter:

```bash
python3 tools/hpc_skill.py scaffold site-adapter my-campus-cluster --name "My Campus Cluster"
```

Scaffolds are written into the current repository by default. Use `--root` for
experiments or CI smoke tests:

```bash
python3 tools/hpc_skill.py scaffold skill ci-test-skill --root /tmp/hpc-skill-hub-scaffold
```

After editing scaffolded files, run:

```bash
python3 tools/hpc_skill.py validate --skill my-new-skill
python3 tools/build_index.py
python3 tools/build_health.py
python3 tools/hpc_skill.py validate
make check
```

## Validating Contributions

Validate one skill while iterating:

```bash
python3 tools/hpc_skill.py validate --skill slurm-submit-job
```

Validate the full registry before opening a pull request:

```bash
python3 tools/hpc_skill.py validate
```

The full command checks manifest metadata, generated registry index freshness,
registry health freshness, compatibility table freshness, and the safety audit.
It also blocks high or critical community skill security findings. Single-skill
validation skips generated registry checks and audits/scans only that skill
directory.

## Scanning Community Skills

Establish a bounded quarantine boundary before reading an untrusted directory
or archive:

```bash
hpc-skill intake ./community-skill
hpc-skill intake ./community-skill.zip --json
hpc-skill intake ./community-skill.tar.gz --policy ../policy.json --json
```

`ready-for-review` and `review-required` exit `0`; `blocked` exits `1`; input or
policy errors exit `2`. All P1 reports keep `context_loading_allowed: false`.
See [Quarantined Community Intake](COMMUNITY_INTAKE.md).

## Creating And Verifying Intake Receipts

Create a deterministic review-required receipt from fresh P1 intake:

```bash
hpc-skill receipt create ./community-skill.zip \
  --output ./review/community-skill.receipt.json \
  --json
```

After a maintainer creates an external exact-binding decision, finalize and
verify the receipt:

```bash
hpc-skill receipt create ./community-skill.zip \
  --decision ./review/community-skill.decision.json \
  --output ./review/community-skill.accepted.json \
  --json

hpc-skill receipt verify ./review/community-skill.accepted.json \
  --source ./community-skill.zip \
  --json
```

Decisions, receipts, and external policies must remain outside a directory
contribution. `accepted` is limited to exact maintainer intake disposition; it
does not establish domain correctness or independent review. See
[Community Intake Receipts](INTAKE_RECEIPTS.md).

For source that is already expanded inside a reviewed boundary, run the static
scanner directly:

Scan an HPC Skill Hub package, agent `SKILL.md` directory, or parent directory
without executing its content:

```bash
hpc-skill security ./community-skill
hpc-skill security ./community-skill --format json
hpc-skill security ./community-skill --format sarif
```

The default threshold fails on `high` and `critical`; lower-severity findings
produce a `review` verdict. See [Community Skill Security](SKILL_SECURITY.md).

## Reviewing Maturity Evidence

Inspect the bounded v0.4 review queue and one candidate:

```bash
hpc-skill review candidates --release v0.4.0
hpc-skill review status shared-project-permissions-triage --json
hpc-skill review packet --release v0.4.0
```

Validate a source bundle from a repository checkout:

```bash
hpc-skill review check \
  reviews/v0.4.0/shared-project-permissions-triage.json \
  --json
```

`ok: true` means the bundle is structurally valid and current. It does not mean
the skill is promotion-ready. The status remains `awaiting-review` until a
public issue, exact review commit, reviewer independence attestation and domain approval, any required
safety approval, and a maintainer decision are recorded.

## Filtering Skills

```bash
python3 tools/hpc_skill.py list --category scheduler
python3 tools/hpc_skill.py list --scheduler slurm
python3 tools/hpc_skill.py list --risk medium
python3 tools/hpc_skill.py list --tag gpu
```

## Resolving Public Site Policy

Resolve a portable skill through one public site adapter:

```bash
hpc-skill resolve slurm-submit-job \
  --adapter nersc-perlmutter-public \
  --json
```

The result includes the skill source, complete public adapter policy, an
explicit skill override when one exists, scheduler compatibility, and review
reasons. `mapped` means an explicit override exists, `compatible-unmapped`
means the schedulers are compatible but no skill-specific override exists, and
`incompatible` returns exit code 2. Every resolution requires local review and
preserves unknown account, partition, module, storage, and endpoint values.

## JSON Output

Discovery commands support JSON output for automation:

```bash
python3 tools/hpc_skill.py show gpu-sanity-check --json
python3 tools/hpc_skill.py collection core-hpc --json
python3 tools/hpc_skill.py health --json
python3 tools/hpc_skill.py adapters --json
python3 tools/hpc_skill.py resolve slurm-submit-job --adapter example-campus-cluster --json
```

## Updating The Index

The CLI reads `registry/index.json`. Rebuild the index after changing skills or
site adapters:

```bash
python3 tools/build_index.py
python3 tools/build_index.py --check
python3 tools/build_health.py
python3 tools/build_health.py --check
python3 tools/build_compatibility.py
python3 tools/build_compatibility.py --check
python3 tools/build_skill_reviews.py
python3 tools/build_skill_reviews.py --check
python3 tools/build_package_data.py
python3 tools/build_package_data.py --check
python3 tools/validate_registry_artifacts.py
```

## Trust Policy Packs

The installed CLI loads `community-default@0.1.0` from package data. An
operator-reviewed policy stored outside the scan target can strengthen the
baseline with `hpc-skill security <path> --policy <policy.json>`. See
[Trust Policy Packs](TRUST_POLICY_PACKS.md) for severity, exception, and
provenance rules.

Future work includes template rendering and reviewed site-aware generation for
common scheduler and workflow files.
