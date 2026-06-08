#!/usr/bin/env python3
"""Explore the HPC Skill Hub registry from the command line."""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "registry" / "index.json"


def load_index() -> Dict[str, Any]:
    if not INDEX_PATH.exists():
        raise SystemExit("registry/index.json is missing; run tools/build_index.py")
    with INDEX_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def emit_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def wrap(value: str, width: int = 76) -> str:
    return "\n".join(textwrap.wrap(value, width=width)) if value else ""


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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
