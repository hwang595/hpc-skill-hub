#!/usr/bin/env python3
"""Explore the HPC Skill Hub registry from the command line."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def find_repo_root() -> Path:
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


def load_index() -> Dict[str, Any]:
    index_path = get_root() / "registry" / "index.json"
    if not index_path.exists():
        raise SystemExit("registry/index.json is missing; run tools/build_index.py")
    with index_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_health() -> Dict[str, Any]:
    health_path = get_root() / "registry" / "health.json"
    if not health_path.exists():
        raise SystemExit("registry/health.json is missing; run tools/build_health.py")
    with health_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def skill_matches(skill: Dict[str, Any], args: argparse.Namespace) -> bool:
    if args.category and args.category not in skill["categories"]:
        return False
    if args.tag and args.tag not in skill["tags"]:
        return False
    if args.risk and args.risk != skill["risk_level"]:
        return False
    if args.scheduler and args.scheduler not in skill["schedulers"]:
        return False
    return True


def cmd_list(args: argparse.Namespace) -> int:
    index = load_index()
    skills = [skill for skill in index["skills"] if skill_matches(skill, args)]
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
    query = " ".join(args.query).lower()
    skills = [skill for skill in index["skills"] if query in searchable_text(skill)]
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
        "tools": [{"name": tool, "required": True}],
        "inputs": [
            {
                "name": "input",
                "type": "string",
                "required": False,
                "description": "Describe user-provided input.",
            }
        ],
        "outputs": [{"name": "output", "description": "Describe produced output."}],
        "artifacts": ["README.md", "examples/example.sh"],
        "examples": [{"title": "Example command", "path": "examples/example.sh"}],
        "tests": [
            {
                "type": "static",
                "command": f"python3 tools/validate_skills.py --skill {args.skill_id}",
                "description": "Validate the manifest and referenced artifacts.",
            }
        ],
        "references": [
            {
                "title": "HPC Skill Hub skill specification",
                "url": "https://github.com/hpc-skill-hub/hpc-skill-hub",
            }
        ],
    }

    readme = f"""# {name}

Use this skill when a user needs help with a specific HPC task.

## Assumptions

- Replace this section with scheduler, module, storage, container, or workflow assumptions.
- Use placeholders for site-specific values such as `<account>` and `<partition>`.

## Example

```bash
bash examples/example.sh
```

## Safety Notes

This scaffold is marked `{args.risk}` risk. Update the risk level before review.

## Success Criteria

- Define what the user should see when the skill works.
- Add manual or integration tests as the skill matures.
"""

    example = """#!/usr/bin/env bash
set -euo pipefail

echo "Replace this scaffold with a safe, reviewable HPC example."
"""

    write_json(skill_dir / "skill.json", manifest)
    (skill_dir / "README.md").write_text(readme, encoding="utf-8")
    example_path = examples_dir / "example.sh"
    example_path.write_text(example, encoding="utf-8")
    example_path.chmod(0o755)
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Explore HPC Skill Hub skills and site adapters"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List skills")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--tag", help="Filter by tag")
    list_parser.add_argument("--risk", choices=["low", "medium", "high"], help="Filter by risk")
    list_parser.add_argument("--scheduler", help="Filter by scheduler")
    list_parser.add_argument("--json", action="store_true", help="Emit JSON")
    list_parser.set_defaults(func=cmd_list)

    search_parser = subparsers.add_parser("search", help="Search skills")
    search_parser.add_argument("query", nargs="+", help="Search query")
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

    scaffold_parser = subparsers.add_parser("scaffold", help="Create new registry entries")
    scaffold_subparsers = scaffold_parser.add_subparsers(dest="scaffold_type", required=True)

    scaffold_skill = scaffold_subparsers.add_parser("skill", help="Create a skill scaffold")
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

    scaffold_adapter = scaffold_subparsers.add_parser(
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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
