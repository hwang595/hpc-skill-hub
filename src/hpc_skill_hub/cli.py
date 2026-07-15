#!/usr/bin/env python3
"""Explore the HPC Skill Hub registry from the command line."""

from __future__ import annotations

import argparse
import importlib.resources as resources
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .intake import IntakeError, intake_package, text_report as intake_text_report
from .reviews import (
    assess_bundle,
    candidates_text,
    markdown_report,
    repo_path,
    skill_status_text,
)
from .security import sarif_report, scan_target, text_report
from .security_policy import SecurityPolicyError


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PACKAGE_NAME = "hpc_skill_hub"
SITE_ADAPTER_RESOLUTION_SCHEMA = (
    "https://hpc-skill-hub.org/schemas/site-adapter-resolution.schema.json"
)


def discover_repo_root() -> Optional[Path]:
    candidates: List[Path] = []
    env_root = os.environ.get("HPC_SKILL_HUB_ROOT")
    if env_root:
        candidates.append(Path(env_root))
    candidates.append(Path.cwd())
    current = Path(__file__).resolve()
    candidates.extend(current.parents)

    for candidate in candidates:
        if (candidate / "registry" / "index.json").exists() and (candidate / "skills").exists():
            return candidate
    return None


def find_repo_root() -> Path:
    root = discover_repo_root()
    if root:
        return root
    raise SystemExit(
        "Could not find HPC Skill Hub registry root. Run from the repository root "
        "or set HPC_SKILL_HUB_ROOT."
    )


ROOT: Optional[Path] = None


def get_root() -> Path:
    global ROOT
    if ROOT is None:
        ROOT = find_repo_root()
    return ROOT


def load_packaged_json(filename: str) -> Dict[str, Any]:
    try:
        data_path = resources.files(PACKAGE_NAME).joinpath(
            "data", "registry", filename
        )
        with data_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(
            f"packaged registry data is missing: data/registry/{filename}"
        )


def load_index() -> Dict[str, Any]:
    root = discover_repo_root()
    if root:
        index_path = root / "registry" / "index.json"
        if not index_path.exists():
            raise SystemExit("registry/index.json is missing; run tools/build_index.py")
        with index_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return load_packaged_json("index.json")


def load_health() -> Dict[str, Any]:
    root = discover_repo_root()
    if root:
        health_path = root / "registry" / "health.json"
        if not health_path.exists():
            raise SystemExit("registry/health.json is missing; run tools/build_health.py")
        with health_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return load_packaged_json("health.json")


def load_review_status() -> Dict[str, Any]:
    root = discover_repo_root()
    if root:
        status_path = root / "registry" / "review-status.json"
        if not status_path.exists():
            raise SystemExit(
                "registry/review-status.json is missing; run tools/build_skill_reviews.py"
            )
        with status_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return load_packaged_json("review-status.json")


def emit_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def wrap(value: str, width: int = 76) -> str:
    return "\n".join(textwrap.wrap(value, width=width)) if value else ""


def title_from_id(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split("-"))


def table(rows: List[List[str]], headers: List[str]) -> str:
    all_rows = [headers] + rows
    widths = [max(len(str(row[index])) for row in all_rows) for index in range(len(headers))]
    lines = [
        "  ".join(headers[index].ljust(widths[index]) for index in range(len(headers))),
        "  ".join("-" * widths[index] for index in range(len(headers))),
    ]
    for row in rows:
        lines.append("  ".join(str(row[index]).ljust(widths[index]) for index in range(len(headers))))
    return "\n".join(lines)


def skill_collection_membership(index: Dict[str, Any]) -> Dict[str, List[str]]:
    membership: Dict[str, List[str]] = {}
    for collection in index.get("collections", []):
        for skill_id in collection.get("skill_ids", []):
            membership.setdefault(skill_id, []).append(collection["id"])
    return {skill_id: sorted(collections) for skill_id, collections in membership.items()}


def skill_matches(
    skill: Dict[str, Any],
    args: argparse.Namespace,
    membership: Optional[Dict[str, List[str]]] = None,
) -> bool:
    if args.category and args.category not in skill["categories"]:
        return False
    if args.tag and args.tag not in skill["tags"]:
        return False
    if args.risk and args.risk != skill["risk_level"]:
        return False
    if args.scheduler and args.scheduler not in skill["schedulers"]:
        return False
    if getattr(args, "maturity", None) and args.maturity != skill["maturity"]:
        return False
    if getattr(args, "status", None) and args.status != skill["status"]:
        return False
    if getattr(args, "tool", None) and args.tool not in skill["tools"]:
        return False
    if getattr(args, "collection", None):
        collections = membership.get(skill["id"], []) if membership else []
        if args.collection not in collections:
            return False
    return True


def cmd_list(args: argparse.Namespace) -> int:
    index = load_index()
    membership = skill_collection_membership(index)
    skills = [skill for skill in index["skills"] if skill_matches(skill, args, membership)]
    if args.json:
        emit_json(skills)
        return 0

    rows = [
        [
            skill["id"],
            ",".join(skill["categories"]),
            skill["risk_level"],
            skill["maturity"],
            skill["summary"],
        ]
        for skill in skills
    ]
    if not rows:
        print("No skills matched.")
        return 1
    print(table(rows, ["id", "categories", "risk", "maturity", "summary"]))
    return 0


def searchable_text(skill: Dict[str, Any]) -> str:
    parts = [
        skill["id"],
        skill["name"],
        skill["summary"],
        skill["description"],
        " ".join(skill["categories"]),
        " ".join(skill["tags"]),
        " ".join(skill["tools"]),
        " ".join(skill["schedulers"]),
    ]
    return " ".join(parts).lower()


def cmd_search(args: argparse.Namespace) -> int:
    index = load_index()
    membership = skill_collection_membership(index)
    query = " ".join(args.query).lower()
    skills = [
        skill
        for skill in index["skills"]
        if query in searchable_text(skill) and skill_matches(skill, args, membership)
    ]
    if args.json:
        emit_json(skills)
        return 0

    if not skills:
        print(f"No skills matched: {query}")
        return 1
    rows = [[skill["id"], skill["risk_level"], skill["summary"]] for skill in skills]
    print(table(rows, ["id", "risk", "summary"]))
    return 0


def find_by_id(items: Iterable[Dict[str, Any]], item_id: str) -> Optional[Dict[str, Any]]:
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def cmd_show(args: argparse.Namespace) -> int:
    index = load_index()
    skill = find_by_id(index["skills"], args.skill_id)
    if not skill:
        print(f"Unknown skill: {args.skill_id}", file=sys.stderr)
        return 1
    if args.json:
        emit_json(skill)
        return 0

    print(f"{skill['name']} ({skill['id']})")
    print("=" * (len(skill["name"]) + len(skill["id"]) + 3))
    print(wrap(skill["summary"]))
    print()
    print(wrap(skill["description"]))
    print()
    print(f"Version: {skill['version']}")
    print(f"Status: {skill['status']}")
    print(f"Maturity: {skill['maturity']}")
    print(f"Risk: {skill['risk_level']}")
    print(f"Categories: {', '.join(skill['categories'])}")
    print(f"Tags: {', '.join(skill['tags'])}")
    if skill["schedulers"]:
        print(f"Schedulers: {', '.join(skill['schedulers'])}")
    print(f"Tools: {', '.join(skill['tools'])}")
    print(f"README: {skill['readme']}")
    if args.examples:
        print()
        print("Examples:")
        for example in skill["examples"]:
            print(f"- {example['title']}: {example['path']}")
    return 0


def cmd_adapters(args: argparse.Namespace) -> int:
    index = load_index()
    adapters = index["site_adapters"]
    if args.json:
        emit_json(adapters)
        return 0
    if not adapters:
        print("No site adapters found.")
        return 1
    rows = [
        [adapter["id"], adapter["status"], adapter["scheduler"], adapter["summary"]]
        for adapter in adapters
    ]
    print(table(rows, ["id", "status", "scheduler", "summary"]))
    return 0


def cmd_adapter(args: argparse.Namespace) -> int:
    index = load_index()
    adapter = find_by_id(index["site_adapters"], args.adapter_id)
    if not adapter:
        print(f"Unknown site adapter: {args.adapter_id}", file=sys.stderr)
        return 1
    if args.json:
        emit_json(adapter)
        return 0

    print(f"{adapter['name']} ({adapter['id']})")
    print("=" * (len(adapter["name"]) + len(adapter["id"]) + 3))
    print(wrap(adapter["summary"]))
    print()
    print(f"Status: {adapter['status']}")
    print(f"Institution type: {adapter['institution_type']}")
    print(f"Scheduler: {adapter['scheduler']}")
    print(f"Partitions: {', '.join(adapter['partitions'])}")
    print(f"Skill overrides: {', '.join(adapter['skill_overrides'])}")
    print(f"README: {adapter['readme']}")
    return 0


def site_adapter_resolution(
    skill: Dict[str, Any], adapter: Dict[str, Any]
) -> Dict[str, Any]:
    policy = adapter["public_policy"]
    adapter_scheduler = adapter.get("scheduler")
    skill_schedulers = set(skill.get("schedulers", []))
    scheduler_compatible = not skill_schedulers or adapter_scheduler in skill_schedulers
    override = next(
        (
            item
            for item in policy.get("skill_overrides", [])
            if item.get("skill_id") == skill["id"]
        ),
        None,
    )
    if not scheduler_compatible:
        resolution_status = "incompatible"
    elif override is not None:
        resolution_status = "mapped"
    else:
        resolution_status = "compatible-unmapped"

    reasons = ["Site policy must be confirmed locally before operational use."]
    if adapter["status"] != "reviewed":
        reasons.append(f"Adapter status is {adapter['status']}, not reviewed.")
    if skill["maturity"] not in {"field-tested", "maintained"}:
        reasons.append(f"Skill maturity is {skill['maturity']}.")
    if not scheduler_compatible:
        reasons.append(
            f"Skill schedulers {sorted(skill_schedulers)} do not include {adapter_scheduler}."
        )
    elif override is None:
        reasons.append("The adapter has no explicit override for this skill.")

    return {
        "$schema": SITE_ADAPTER_RESOLUTION_SCHEMA,
        "schema_version": "0.1.0",
        "resolution_status": resolution_status,
        "skill": {
            key: skill[key]
            for key in (
                "id",
                "version",
                "status",
                "maturity",
                "risk_level",
                "schedulers",
                "readme",
                "examples",
            )
        },
        "adapter": {
            key: adapter[key]
            for key in ("id", "status", "institution_type", "scheduler", "readme")
        },
        "compatibility": {
            "scheduler_compatible": scheduler_compatible,
            "explicit_override": override is not None,
        },
        "public_policy": policy,
        "override": override,
        "review": {
            "required": True,
            "reasons": reasons,
            "rules": [
                "Preserve placeholders until the user confirms public local values.",
                "Do not infer unpublished accounts, partitions, modules, paths, or endpoints.",
                "Require explicit user intent before submitting jobs or changing shared state.",
            ],
        },
    }


def cmd_resolve(args: argparse.Namespace) -> int:
    index = load_index()
    skill = find_by_id(index["skills"], args.skill_id)
    if not skill:
        print(f"Unknown skill: {args.skill_id}", file=sys.stderr)
        return 1
    adapter = find_by_id(index["site_adapters"], args.adapter_id)
    if not adapter:
        print(f"Unknown site adapter: {args.adapter_id}", file=sys.stderr)
        return 1
    if not isinstance(adapter.get("public_policy"), dict):
        print(
            "Site adapter resolution requires registry index schema 0.2.0 or later.",
            file=sys.stderr,
        )
        return 1
    payload = site_adapter_resolution(skill, adapter)
    if args.json:
        emit_json(payload)
    else:
        print(f"Resolution: {payload['resolution_status']}")
        print(f"Skill: {skill['id']} v{skill['version']} ({skill['maturity']}, {skill['risk_level']})")
        print(f"Adapter: {adapter['id']} ({adapter['status']}, {adapter['scheduler']})")
        print(f"Skill README: {skill['readme']}")
        print(f"Adapter README: {adapter['readme']}")
        if payload["override"] is not None:
            print(f"Override: {payload['override']['notes']}")
        print("Review required: yes")
        for reason in payload["review"]["reasons"]:
            print(f"- {reason}")
    return 2 if payload["resolution_status"] == "incompatible" else 0


def cmd_collections(args: argparse.Namespace) -> int:
    index = load_index()
    collections = index.get("collections", [])
    if args.json:
        emit_json(collections)
        return 0
    if not collections:
        print("No collections found.")
        return 1
    rows = [
        [
            collection["id"],
            collection["status"],
            str(len(collection["skill_ids"])),
            ", ".join(collection["audience"]),
            collection["summary"],
        ]
        for collection in collections
    ]
    print(table(rows, ["id", "status", "skills", "audience", "summary"]))
    return 0


def cmd_collection(args: argparse.Namespace) -> int:
    index = load_index()
    collection = find_by_id(index.get("collections", []), args.collection_id)
    if not collection:
        print(f"Unknown collection: {args.collection_id}", file=sys.stderr)
        return 1
    if args.json:
        emit_json(collection)
        return 0

    skill_by_id = {skill["id"]: skill for skill in index["skills"]}
    print(f"{collection['name']} ({collection['id']})")
    print("=" * (len(collection["name"]) + len(collection["id"]) + 3))
    print(wrap(collection["summary"]))
    print()
    print(f"Status: {collection['status']}")
    print(f"Audience: {', '.join(collection['audience'])}")
    print(f"Manifest: {collection['path']}")
    print()
    print("Skills:")
    for skill_id in collection["skill_ids"]:
        skill = skill_by_id.get(skill_id)
        if skill:
            print(f"- {skill_id}: {skill['summary']}")
        else:
            print(f"- {skill_id}: missing from registry")
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    health = load_health()
    if args.json:
        emit_json(health)
        return 0

    print("Registry Health")
    print("===============")
    print(f"Skills: {health['skill_count']}")
    print(f"Site adapters: {health['site_adapter_count']}")
    print(f"Collections: {health['collection_count']}")
    print(f"Uncollected skills: {len(health['uncollected_skill_ids'])}")
    print()
    print("Risk:")
    for risk, count in health["risk_counts"].items():
        print(f"- {risk}: {count}")
    print()
    print("Maturity:")
    for maturity, count in health["maturity_counts"].items():
        print(f"- {maturity}: {count}")
    if health["uncollected_skill_ids"]:
        print()
        print("Uncollected skills:")
        for skill_id in health["uncollected_skill_ids"]:
            print(f"- {skill_id}")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    from .doctor import doctor_report, doctor_text

    report = doctor_report(require_mcp=args.require_mcp)
    if args.json:
        emit_json(report)
    else:
        print(doctor_text(report))
    return 0 if report["ok"] else 1


def review_release(payload: Dict[str, Any], release: Optional[str]) -> bool:
    return release is None or payload.get("release") == release


def cmd_review_candidates(args: argparse.Namespace) -> int:
    payload = load_review_status()
    if not review_release(payload, args.release):
        print(f"No review queue found for release: {args.release}", file=sys.stderr)
        return 1
    if args.json:
        emit_json(
            {
                "release": payload["release"],
                "candidate_count": payload["candidate_count"],
                "static_ready_count": payload["static_ready_count"],
                "promotion_ready_count": payload["promotion_ready_count"],
                "candidates": payload["skills"],
            }
        )
    else:
        print(candidates_text(payload))
    return 0


def cmd_review_status(args: argparse.Namespace) -> int:
    payload = load_review_status()
    if not review_release(payload, args.release):
        print(f"No review queue found for release: {args.release}", file=sys.stderr)
        return 1
    skill = find_by_id(payload.get("skills", []), args.skill_id)
    if not skill:
        print(f"No review bundle found for skill: {args.skill_id}", file=sys.stderr)
        return 1
    if args.json:
        emit_json(skill)
    else:
        print(skill_status_text(skill))
    return 0


def cmd_review_check(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else get_root()
    bundle_path = repo_path(root, args.review_file)
    if bundle_path is None or not bundle_path.is_file():
        print(
            "Review file must be an existing repository-relative path.",
            file=sys.stderr,
        )
        return 2
    try:
        with (root / "registry" / "index.json").open(encoding="utf-8") as handle:
            index = json.load(handle)
        with (root / "registry" / "skill-quality.json").open(encoding="utf-8") as handle:
            quality = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"Cannot load registry review inputs: {exc}", file=sys.stderr)
        return 2
    assessment = assess_bundle(root, bundle_path, index, quality)
    payload = {
        "ok": not assessment["validation_errors"],
        "promotion_ready": assessment["promotion_ready"],
        "assessment": assessment,
    }
    if args.json:
        emit_json(payload)
    else:
        print(skill_status_text(assessment))
        if assessment["validation_errors"]:
            print("Validation errors:", file=sys.stderr)
            for error in assessment["validation_errors"]:
                print(f"- {error}", file=sys.stderr)
    return 1 if assessment["validation_errors"] else 0


def cmd_review_packet(args: argparse.Namespace) -> int:
    payload = load_review_status()
    if not review_release(payload, args.release):
        print(f"No review queue found for release: {args.release}", file=sys.stderr)
        return 1
    if args.json:
        emit_json(payload)
    else:
        print(markdown_report(payload), end="")
    return 0


def add_review_subcommands(subparsers: argparse._SubParsersAction) -> None:
    candidates = subparsers.add_parser(
        "candidates", help="List evidence-backed maturity review candidates"
    )
    candidates.add_argument("--release", help="Filter by release")
    candidates.add_argument("--json", action="store_true", help="Emit JSON")
    candidates.set_defaults(func=cmd_review_candidates)

    status = subparsers.add_parser("status", help="Show one skill review status")
    status.add_argument("skill_id", help="Skill id")
    status.add_argument("--release", help="Filter by release")
    status.add_argument("--json", action="store_true", help="Emit JSON")
    status.set_defaults(func=cmd_review_status)

    check = subparsers.add_parser("check", help="Validate one source review bundle")
    check.add_argument("review_file", help="Repository-relative review bundle path")
    check.add_argument("--root", help="Repository root")
    check.add_argument("--json", action="store_true", help="Emit JSON")
    check.set_defaults(func=cmd_review_check)

    packet = subparsers.add_parser("packet", help="Print the generated review packet")
    packet.add_argument("--release", help="Filter by release")
    packet.add_argument("--json", action="store_true", help="Emit JSON")
    packet.set_defaults(func=cmd_review_packet)


def cmd_security(args: argparse.Namespace) -> int:
    target = Path(args.target).expanduser()
    try:
        report = scan_target(
            target,
            fail_on=args.fail_on,
            policy_path=Path(args.policy).expanduser() if args.policy else None,
        )
    except (FileNotFoundError, OSError, SecurityPolicyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    output_format = "json" if args.json else args.format
    if output_format == "json":
        emit_json(report)
    elif output_format == "sarif":
        emit_json(sarif_report(report))
    else:
        print(text_report(report))
    return 1 if (
        report["execution"]["exit_on"] != "none"
        and report["summary"]["verdict"] == "block"
    ) else 0


def cmd_intake(args: argparse.Namespace) -> int:
    source = Path(args.source).expanduser()
    try:
        report = intake_package(
            source,
            policy_path=Path(args.policy).expanduser() if args.policy else None,
        )
    except (FileNotFoundError, IntakeError, OSError, SecurityPolicyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json or args.format == "json":
        emit_json(report)
    else:
        print(intake_text_report(report))
    return 1 if report["summary"]["status"] == "blocked" else 0


def run_step(label: str, command: List[str], root: Path) -> int:
    print(f"==> {label}", flush=True)
    result = subprocess.run(command, cwd=str(root))
    if result.returncode != 0:
        print(f"FAILED: {label}", file=sys.stderr, flush=True)
        return result.returncode
    print(f"OK: {label}", flush=True)
    return 0


def run_step_json(label: str, command: List[str], root: Path) -> Dict[str, Any]:
    result = subprocess.run(
        command,
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "label": label,
        "command": command,
        "returncode": result.returncode,
        "status": "passed" if result.returncode == 0 else "failed",
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def cmd_validate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve() if args.root else get_root()
    if args.skill:
        ensure_id(args.skill)

    tools_dir = root / "tools"
    validate_cmd = [sys.executable, str(tools_dir / "validate_skills.py")]
    if args.skill:
        validate_cmd.extend(["--skill", args.skill])

    steps = [("Validate registry metadata", validate_cmd)]

    if args.skill:
        if not args.skip_safety:
            skill_path = str(root / "skills" / args.skill)
            steps.extend(
                [
                    (
                        "Run safety audit for skill",
                        [sys.executable, str(tools_dir / "audit_safety.py"), skill_path],
                    ),
                    (
                        "Run security scan for skill",
                        [
                            sys.executable,
                            str(tools_dir / "scan_skill_security.py"),
                            skill_path,
                            "--fail-on",
                            "high",
                        ],
                    ),
                ]
            )
    else:
        if not args.skip_generated:
            steps.extend(
                [
                    (
                        "Check generated registry index",
                        [sys.executable, str(tools_dir / "build_index.py"), "--check"],
                    ),
                    (
                        "Check generated registry health",
                        [sys.executable, str(tools_dir / "build_health.py"), "--check"],
                    ),
                    (
                        "Check generated compatibility tables",
                        [
                            sys.executable,
                            str(tools_dir / "build_compatibility.py"),
                            "--check",
                        ],
                    ),
                ]
            )
        if not args.skip_safety:
            steps.extend(
                [
                    (
                        "Run safety audit",
                        [sys.executable, str(tools_dir / "audit_safety.py")],
                    ),
                    (
                        "Run community skill security scan",
                        [
                            sys.executable,
                            str(tools_dir / "scan_skill_security.py"),
                            str(root / "skills"),
                            "--fail-on",
                            "high",
                        ],
                    ),
                ]
            )

    if args.json:
        results = [run_step_json(label, command, root) for label, command in steps]
        ok = all(result["returncode"] == 0 for result in results)
        payload = {
            "ok": ok,
            "root": str(root),
            "skill": args.skill,
            "skip_generated": args.skip_generated,
            "skip_safety": args.skip_safety,
            "step_count": len(results),
            "steps": results,
        }
        emit_json(payload)
        for result in results:
            if result["returncode"] != 0:
                return result["returncode"]
        return 0

    for label, command in steps:
        return_code = run_step(label, command, root)
        if return_code:
            return return_code

    print("Validation completed successfully.")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    ensure_id(args.skill_id)
    args.skill = args.skill_id
    args.skip_generated = True
    return cmd_validate(args)


def ensure_id(value: str) -> None:
    if not ID_RE.match(value):
        raise SystemExit(f"Invalid id '{value}'; use lowercase kebab-case")


def ensure_new_dir(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise SystemExit(f"{path} already exists; pass --force to overwrite scaffold files")
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def cmd_scaffold_skill(args: argparse.Namespace) -> int:
    ensure_id(args.skill_id)
    root = Path(args.root).resolve() if args.root else get_root()
    skill_dir = root / "skills" / args.skill_id
    ensure_new_dir(skill_dir, args.force)
    examples_dir = skill_dir / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)

    name = args.name or title_from_id(args.skill_id)
    summary = args.summary or f"Draft skill scaffold for {name}."
    tool = args.tool or "bash"
    category = args.category
    tools = [{"name": "bash", "required": True}]
    if tool != "bash":
        tools.append({"name": tool, "required": False})

    manifest = {
        "$schema": "../../schemas/skill.schema.json",
        "id": args.skill_id,
        "name": name,
        "version": "0.1.0",
        "status": "draft",
        "summary": summary,
        "description": f"Describe the HPC task, target users, assumptions, and expected outcome for {name}.",
        "categories": [category],
        "tags": [category, "draft"],
        "maintainers": [{"name": "HPC Skill Hub Maintainers"}],
        "license": "MIT",
        "maturity": "seed",
        "risk_level": args.risk,
        "tools": tools,
        "inputs": [
            {
                "name": "working_directory",
                "type": "path",
                "required": False,
                "description": "Directory where the user plans to run or test the workflow.",
            },
            {
                "name": "input_path",
                "type": "string",
                "required": False,
                "description": "Describe user-provided input.",
            }
        ],
        "outputs": [{"name": "output", "description": "Describe produced output."}],
        "artifacts": [
            "README.md",
            "examples/example.sh",
            "examples/check-prereqs.sh",
            "examples/review-checklist.md",
        ],
        "examples": [
            {"title": "Plan-only example command", "path": "examples/example.sh"},
            {"title": "Prerequisite check", "path": "examples/check-prereqs.sh"},
            {"title": "Review checklist", "path": "examples/review-checklist.md"},
        ],
        "tests": [
            {
                "type": "static",
                "command": f"python3 tools/validate_skills.py --skill {args.skill_id}",
                "description": "Validate the manifest and referenced artifacts.",
            },
            {
                "type": "dry-run",
                "command": f"bash skills/{args.skill_id}/examples/example.sh",
                "description": "Run the plan-only example without submitting jobs or moving data.",
            }
        ],
        "references": [
            {
                "title": "HPC Skill Hub skill specification",
                "url": "https://github.com/hwang595/hpc-skill-hub",
            }
        ],
    }

    readme = f"""# {name}

Use this skill when a user needs help with a specific HPC task.

## Intended Users

- Replace this list with the users this skill should serve.
- Keep the first version narrow enough for public review.

## Assumptions

- Replace this section with scheduler, module, storage, container, or workflow assumptions.
- Use placeholders for site-specific values such as `<account>` and `<partition>`.

## Example

```bash
bash examples/example.sh
```

Check local prerequisites without submitting work:

```bash
bash examples/check-prereqs.sh
```

## Safety Notes

This scaffold is marked `{args.risk}` risk. Update the risk level before review.

## Success Criteria

- Define what the user should see when the skill works.
- Add manual or integration tests as the skill matures.
"""

    example = """#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${OUTPUT_DIR:-skill-scaffold-output}"
RUN_EXAMPLE="${RUN_EXAMPLE:-0}"

mkdir -p "${OUTPUT_DIR}"

cat > "${OUTPUT_DIR}/plan.txt" <<'PLAN'
Replace this scaffold with a safe, reviewable HPC example.

Default behavior must stay plan-only. Expensive, destructive, or shared-system
actions should require an explicit RUN_* environment variable.
PLAN

if [ "${RUN_EXAMPLE}" = "1" ]; then
  echo "RUN_EXAMPLE=1 was set. Replace this branch with an explicit guarded action."
else
  echo "Plan-only mode. Wrote ${OUTPUT_DIR}/plan.txt"
fi
"""

    check_prereqs = f"""#!/usr/bin/env bash
set -euo pipefail

echo "Checking basic prerequisites for {args.skill_id}..."

if command -v {tool} >/dev/null 2>&1; then
  echo "found: {tool}"
else
  echo "missing or not loaded: {tool}"
fi

echo "Review site policy, scheduler limits, storage paths, and module/container assumptions before running real work."
"""

    review_checklist = f"""# {name} Review Checklist

Use this checklist before moving `{args.skill_id}` beyond scaffold status.

- [ ] The README explains the target users and task boundary.
- [ ] Examples default to plan-only, dry-run, or read-only behavior.
- [ ] Expensive or destructive actions require explicit opt-in.
- [ ] Scheduler accounts, partitions, hostnames, and private paths use placeholders.
- [ ] Inputs, outputs, artifacts, references, and tests match `skill.json`.
- [ ] Public references are sufficient for an external reviewer.
- [ ] `python3 tools/validate_skills.py --skill {args.skill_id}` passes.
"""

    write_json(skill_dir / "skill.json", manifest)
    (skill_dir / "README.md").write_text(readme, encoding="utf-8")
    example_path = examples_dir / "example.sh"
    example_path.write_text(example, encoding="utf-8")
    example_path.chmod(0o755)
    check_path = examples_dir / "check-prereqs.sh"
    check_path.write_text(check_prereqs, encoding="utf-8")
    check_path.chmod(0o755)
    (examples_dir / "review-checklist.md").write_text(review_checklist, encoding="utf-8")
    print(f"Created skill scaffold: {skill_dir}")
    return 0


def cmd_scaffold_adapter(args: argparse.Namespace) -> int:
    ensure_id(args.adapter_id)
    root = Path(args.root).resolve() if args.root else get_root()
    adapter_dir = root / "site-adapters" / args.adapter_id
    ensure_new_dir(adapter_dir, args.force)

    name = args.name or title_from_id(args.adapter_id)
    scheduler = args.scheduler
    manifest = {
        "$schema": "../../schemas/site-adapter.schema.json",
        "id": args.adapter_id,
        "name": name,
        "status": "draft",
        "summary": f"Draft site adapter for {name}.",
        "institution_type": args.institution_type,
        "contacts": [{"name": "Public HPC support contact", "url": "https://example.edu/hpc"}],
        "scheduler": {
            "type": scheduler,
            "account_placeholder": "<account>",
            "default_partition": "<partition>",
            "job_submit_notes": ["Replace these notes with public local policy."],
        },
        "partitions": [
            {
                "name": "<partition>",
                "purpose": "Describe intended use.",
                "max_walltime": "00:30:00",
                "gpu": False,
            }
        ],
        "modules": {
            "system": "lmod",
            "recommended": [{"purpose": "MPI examples", "module": "<mpi-module>"}],
        },
        "storage": [
            {
                "name": "scratch",
                "path": "/scratch/<user>",
                "intended_use": "Temporary job working directories.",
                "backed_up": False,
            }
        ],
        "policies": [
            {
                "topic": "login-nodes",
                "summary": "Run compute-heavy work through the scheduler.",
            }
        ],
        "skill_overrides": [
            {
                "skill_id": "slurm-submit-job",
                "notes": "Replace placeholders with public local policy.",
            }
        ],
    }

    readme = f"""# {name} Adapter

This draft site adapter maps portable HPC Skill Hub entries to public local
policy for `{name}`.

## What To Replace

- Public support URL.
- Scheduler partition names.
- Module names.
- Storage path placeholders.
- Skill override notes.

## Safety Check

- Do not include private hostnames.
- Do not include usernames, tokens, allocation names, or internal project ids.
- Do not include unpublished security procedures.
"""

    write_json(adapter_dir / "site.json", manifest)
    (adapter_dir / "README.md").write_text(readme, encoding="utf-8")
    print(f"Created site adapter scaffold: {adapter_dir}")
    return 0


def add_skill_filter_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--tag", help="Filter by tag")
    parser.add_argument("--risk", choices=["low", "medium", "high"], help="Filter by risk")
    parser.add_argument(
        "--maturity",
        choices=["seed", "reviewed", "field-tested", "maintained"],
        help="Filter by maturity",
    )
    parser.add_argument(
        "--status",
        choices=["draft", "reviewed", "deprecated"],
        help="Filter by status",
    )
    parser.add_argument("--scheduler", help="Filter by scheduler")
    parser.add_argument("--tool", help="Filter by declared tool")
    parser.add_argument("--collection", help="Filter by collection id")


def add_scaffold_subcommands(subparsers: argparse._SubParsersAction) -> None:
    scaffold_skill = subparsers.add_parser("skill", help="Create a skill scaffold")
    scaffold_skill.add_argument("skill_id", help="New skill id in lowercase kebab-case")
    scaffold_skill.add_argument("--name", help="Human-readable skill name")
    scaffold_skill.add_argument("--summary", help="One-sentence summary")
    scaffold_skill.add_argument(
        "--category",
        default="education",
        choices=[
            "scheduler",
            "containers",
            "software",
            "workflow",
            "data",
            "debugging",
            "performance",
            "gpu",
            "mpi",
            "interactive",
            "admin",
            "education",
        ],
        help="Primary skill category",
    )
    scaffold_skill.add_argument("--risk", default="low", choices=["low", "medium", "high"])
    scaffold_skill.add_argument("--tool", help="Primary tool used by the skill")
    scaffold_skill.add_argument("--root", help="Repository root to write into")
    scaffold_skill.add_argument("--force", action="store_true", help="Overwrite scaffold files")
    scaffold_skill.set_defaults(func=cmd_scaffold_skill)

    scaffold_adapter = subparsers.add_parser(
        "site-adapter", help="Create a site adapter scaffold"
    )
    scaffold_adapter.add_argument("adapter_id", help="New adapter id in lowercase kebab-case")
    scaffold_adapter.add_argument("--name", help="Human-readable site or training environment name")
    scaffold_adapter.add_argument("--scheduler", default="slurm", help="Scheduler type")
    scaffold_adapter.add_argument(
        "--institution-type",
        default="other",
        choices=["example", "university", "national-lab", "company", "cloud", "other"],
    )
    scaffold_adapter.add_argument("--root", help="Repository root to write into")
    scaffold_adapter.add_argument("--force", action="store_true", help="Overwrite scaffold files")
    scaffold_adapter.set_defaults(func=cmd_scaffold_adapter)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Explore HPC Skill Hub skills and site adapters"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List skills")
    add_skill_filter_options(list_parser)
    list_parser.add_argument("--json", action="store_true", help="Emit JSON")
    list_parser.set_defaults(func=cmd_list)

    search_parser = subparsers.add_parser("search", help="Search skills")
    search_parser.add_argument("query", nargs="+", help="Search query")
    add_skill_filter_options(search_parser)
    search_parser.add_argument("--json", action="store_true", help="Emit JSON")
    search_parser.set_defaults(func=cmd_search)

    show_parser = subparsers.add_parser("show", help="Show one skill")
    show_parser.add_argument("skill_id", help="Skill id")
    show_parser.add_argument("--examples", action="store_true", help="Show examples")
    show_parser.add_argument("--json", action="store_true", help="Emit JSON")
    show_parser.set_defaults(func=cmd_show)

    adapters_parser = subparsers.add_parser("adapters", help="List site adapters")
    adapters_parser.add_argument("--json", action="store_true", help="Emit JSON")
    adapters_parser.set_defaults(func=cmd_adapters)

    adapter_parser = subparsers.add_parser("adapter", help="Show one site adapter")
    adapter_parser.add_argument("adapter_id", help="Site adapter id")
    adapter_parser.add_argument("--json", action="store_true", help="Emit JSON")
    adapter_parser.set_defaults(func=cmd_adapter)

    resolve_parser = subparsers.add_parser(
        "resolve", help="Resolve a skill through a public site adapter"
    )
    resolve_parser.add_argument("skill_id", help="Skill id")
    resolve_parser.add_argument("--adapter", dest="adapter_id", required=True)
    resolve_parser.add_argument("--json", action="store_true", help="Emit JSON")
    resolve_parser.set_defaults(func=cmd_resolve)

    collections_parser = subparsers.add_parser("collections", help="List skill collections")
    collections_parser.add_argument("--json", action="store_true", help="Emit JSON")
    collections_parser.set_defaults(func=cmd_collections)

    collection_parser = subparsers.add_parser("collection", help="Show one skill collection")
    collection_parser.add_argument("collection_id", help="Collection id")
    collection_parser.add_argument("--json", action="store_true", help="Emit JSON")
    collection_parser.set_defaults(func=cmd_collection)

    health_parser = subparsers.add_parser("health", help="Show registry health summary")
    health_parser.add_argument("--json", action="store_true", help="Emit JSON")
    health_parser.set_defaults(func=cmd_health)

    doctor_parser = subparsers.add_parser(
        "doctor", help="Diagnose installed data and optional MCP compatibility"
    )
    doctor_parser.add_argument("--json", action="store_true", help="Emit JSON")
    doctor_parser.add_argument(
        "--require-mcp",
        action="store_true",
        help="Fail when the optional MCP dependency or protocol probe is unavailable",
    )
    doctor_parser.set_defaults(func=cmd_doctor)

    review_parser = subparsers.add_parser(
        "review", help="Inspect evidence-backed skill maturity reviews"
    )
    review_subparsers = review_parser.add_subparsers(
        dest="review_command", required=True
    )
    add_review_subcommands(review_subparsers)

    intake_parser = subparsers.add_parser(
        "intake",
        help="Quarantine and scan an untrusted community skill bundle",
    )
    intake_parser.add_argument(
        "source", help="Directory, ZIP archive, or TAR archive to inspect"
    )
    intake_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    intake_parser.add_argument(
        "--json", action="store_true", help="Alias for --format json"
    )
    intake_parser.add_argument(
        "--policy",
        help="Complete external policy pack stored outside the contribution",
    )
    intake_parser.set_defaults(func=cmd_intake)

    security_parser = subparsers.add_parser(
        "security", help="Scan a community skill package for security risks"
    )
    security_parser.add_argument(
        "target", nargs="?", default=".", help="Skill file or directory to scan"
    )
    security_parser.add_argument(
        "--format",
        choices=["text", "json", "sarif"],
        default="text",
        help="Output format",
    )
    security_parser.add_argument("--json", action="store_true", help="Alias for --format json")
    security_parser.add_argument(
        "--fail-on",
        choices=["policy", "none", "low", "medium", "high", "critical"],
        default="policy",
        help="Use the policy threshold, strengthen it, or use none for report-only mode",
    )
    security_parser.add_argument(
        "--policy",
        help="Complete external policy pack that extends community-default@0.1.0",
    )
    security_parser.set_defaults(func=cmd_security)

    validate_parser = subparsers.add_parser(
        "validate", help="Run registry validation checks"
    )
    validate_parser.add_argument(
        "--skill",
        help="Validate one skill id and skip generated registry checks",
    )
    validate_parser.add_argument(
        "--skip-generated",
        action="store_true",
        help="Skip generated index and health freshness checks",
    )
    validate_parser.add_argument(
        "--skip-safety",
        action="store_true",
        help="Skip safety audit checks",
    )
    validate_parser.add_argument("--json", action="store_true", help="Emit JSON")
    validate_parser.add_argument("--root", help="Repository root to validate")
    validate_parser.set_defaults(func=cmd_validate)

    check_parser = subparsers.add_parser(
        "check", help="Validate one skill with optional safety checks"
    )
    check_parser.add_argument("skill_id", help="Skill id to validate")
    check_parser.add_argument(
        "--skip-safety",
        action="store_true",
        help="Skip safety audit checks",
    )
    check_parser.add_argument("--json", action="store_true", help="Emit JSON")
    check_parser.add_argument("--root", help="Repository root to validate")
    check_parser.set_defaults(func=cmd_check)

    scaffold_parser = subparsers.add_parser("scaffold", help="Create new registry entries")
    scaffold_subparsers = scaffold_parser.add_subparsers(dest="scaffold_type", required=True)
    add_scaffold_subcommands(scaffold_subparsers)

    new_parser = subparsers.add_parser("new", help="Create new registry entries")
    new_subparsers = new_parser.add_subparsers(dest="new_type", required=True)
    add_scaffold_subcommands(new_subparsers)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
