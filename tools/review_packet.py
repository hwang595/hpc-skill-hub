#!/usr/bin/env python3
"""Build a reviewed-skill pilot packet for a target release."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

from review_candidates import build_payload


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERSION = "v0.2.0"
DEFAULT_LIMIT = 12


def normalize_version(version: str) -> str:
    return version if version.startswith("v") else f"v{version}"


def default_output(version: str) -> Path:
    normalized = normalize_version(version)
    return ROOT / "docs" / f"REVIEW_PACKET_{normalized}.md"


def suggested_labels(candidate: Dict[str, Any]) -> List[str]:
    labels = ["maturity-review", "needs-domain-review"]
    categories = set(candidate.get("categories", []))
    if candidate.get("risk_level") != "low" or "admin" in categories:
        labels.append("safety-review")
    if candidate.get("risk_level") == "low":
        labels.append("good-first-issue")
    return labels


def enriched_candidates(candidates: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []
    for candidate in candidates:
        item = dict(candidate)
        item["issue_title"] = f"Maturity review: {candidate['id']}"
        item["suggested_labels"] = suggested_labels(candidate)
        item["promotion_target"] = "reviewed"
        item["next_step"] = (
            "Open a maturity-review issue, assign the review focus owner, and "
            "confirm public-safe evidence before changing skill maturity."
        )
        enriched.append(item)
    return enriched


def focus_groups(candidates: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for candidate in candidates:
        groups.setdefault(candidate["review_focus"], []).append(candidate)

    return [
        {
            "review_focus": focus,
            "candidate_count": len(items),
            "skill_ids": [candidate["id"] for candidate in items],
        }
        for focus, items in sorted(groups.items())
    ]


def build_review_packet(
    version: str, limit: int, collection: str | None
) -> Dict[str, Any]:
    source = build_payload(limit=limit, collection=collection)
    candidates = enriched_candidates(source["candidates"])
    return {
        "target_version": normalize_version(version),
        "milestone": f"{normalize_version(version)} reviewed-skill pilot",
        "generated_from": source["generated_from"],
        "skill_count": source["skill_count"],
        "seed_skill_count": source["seed_skill_count"],
        "candidate_count": source["candidate_count"],
        "risk_counts": source["risk_counts"],
        "collection": source["collection"],
        "limit": source["limit"],
        "candidates": candidates,
        "focus_groups": focus_groups(candidates),
        "promotion_gate": [
            "Maturity-review issue is open and linked from the pull request.",
            "A domain reviewer confirms scope, examples, assumptions, and references.",
            "Safety review is completed when suggested by risk level or admin scope.",
            "The pull request updates skill.json, generated registry artifacts, and release notes.",
            "Public evidence excludes hostnames, usernames, allocations, tickets, tokens, and private paths.",
            "make check passes locally and in GitHub Actions.",
        ],
    }


def escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def markdown_list(values: Iterable[str]) -> List[str]:
    return [f"- {value}" for value in values]


def markdown(packet: Dict[str, Any]) -> str:
    lines = [
        f"# {packet['target_version']} Reviewed-Skill Pilot Packet",
        "",
        "This packet is generated from `registry/index.json` through",
        "`tools/review_packet.py`. It routes seed skills toward first domain",
        "review without promoting maturity automatically.",
        "",
        "## Summary",
        "",
        f"- Target version: `{packet['target_version']}`",
        f"- Milestone: `{packet['milestone']}`",
        f"- Skills: {packet['skill_count']}",
        f"- Seed skills: {packet['seed_skill_count']}",
        f"- Candidate pool: {packet['candidate_count']}",
        f"- Display limit: {packet['limit']}",
        f"- Collection filter: `{packet['collection'] or 'all'}`",
        f"- Risk counts: {json.dumps(packet['risk_counts'], sort_keys=True)}",
        "",
        "## Promotion Gate",
        "",
        *markdown_list(packet["promotion_gate"]),
        "",
        "## Reviewer Queue",
        "",
        "| Review focus | Candidates | Skill ids |",
        "| --- | ---: | --- |",
    ]

    if not packet["focus_groups"]:
        lines.append("| _None_ | 0 |  |")
    else:
        for group in packet["focus_groups"]:
            lines.append(
                "| "
                f"{escape_table(group['review_focus'])} | "
                f"{group['candidate_count']} | "
                f"{escape_table(', '.join(f'`{skill_id}`' for skill_id in group['skill_ids']))} |"
            )

    lines.extend(
        [
            "",
            "## Candidate Issues",
            "",
            "| Skill | Risk | Score | Review focus | Suggested labels | Evidence |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )

    if not packet["candidates"]:
        lines.append("| _None_ |  |  |  |  |  |")
    else:
        for candidate in packet["candidates"]:
            lines.append(
                "| "
                f"`{candidate['id']}` | "
                f"`{candidate['risk_level']}` | "
                f"{candidate['score']} | "
                f"{escape_table(candidate['review_focus'])} | "
                f"{escape_table(', '.join(candidate['suggested_labels']))} | "
                f"{escape_table(', '.join(candidate['evidence']))} |"
            )

    lines.extend(
        [
            "",
            "## Issue Body Template",
            "",
            "Use this template for each candidate before changing maturity:",
            "",
            "```markdown",
            "## Skill",
            "",
            "- Skill id: `<skill-id>`",
            "- Current maturity: `seed`",
            "- Requested maturity: `reviewed`",
            "- Review focus: `<review-focus>`",
            "",
            "## Evidence",
            "",
            "- [ ] Domain reviewer has checked scope and assumptions.",
            "- [ ] Examples are conservative for shared HPC systems.",
            "- [ ] Risk level matches the strongest action in the skill.",
            "- [ ] Public references are current enough for adoption.",
            "- [ ] No private hostnames, usernames, allocations, tickets, tokens, or internal paths are included.",
            "- [ ] `make check` passes in the linked pull request.",
            "",
            "## Follow-up",
            "",
            "- PR: `<link>`",
            "- Safety review issue, if needed: `<link>`",
            "- Adoption report, if available: `<link>`",
            "```",
            "",
            "## Maintainer Notes",
            "",
            "- Do not promote a skill only because it scores highly in this packet.",
            "- Use `safety-review` when the skill touches admin evidence, facility operations, shared software policy, quotas, or larger side effects.",
            "- Use adoption reports for `field-tested`; this packet targets `reviewed` only.",
            "",
        ]
    )
    return "\n".join(lines)


def check_output(output: Path, expected: str) -> List[str]:
    if not output.exists():
        return [f"{output.relative_to(ROOT)} is missing"]
    if output.read_text(encoding="utf-8") != expected:
        return [
            f"{output.relative_to(ROOT)} is stale; run tools/review_packet.py"
        ]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a reviewed-skill pilot packet for a target release"
    )
    parser.add_argument(
        "--target-version",
        default=DEFAULT_VERSION,
        help="Target release version, for example v0.2.0 or 0.2.0.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Maximum number of candidates to include.",
    )
    parser.add_argument(
        "--collection",
        help="Only include candidates that belong to this collection id.",
    )
    parser.add_argument(
        "--output",
        help="Markdown output path. Defaults to docs/REVIEW_PACKET_<version>.md.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--check", action="store_true", help="Fail if output is stale.")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")

    packet = build_review_packet(args.target_version, args.limit, args.collection)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0

    output = Path(args.output) if args.output else default_output(args.target_version)
    if not output.is_absolute():
        output = ROOT / output
    expected = markdown(packet)

    if args.check:
        errors = check_output(output, expected)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Review packet is current in {output.relative_to(ROOT)}.")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    print(f"Wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
