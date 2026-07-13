#!/usr/bin/env python3
"""Build a deterministic, evidence-based skill quality baseline."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
BENCHMARK_CASE_DIR = ROOT / "benchmarks" / "cases"
AGENT_TASK_DIR = ROOT / "agent-bench" / "tasks"
QUALITY_JSON = ROOT / "registry" / "skill-quality.json"
QUALITY_MD = ROOT / "docs" / "SKILL_QUALITY.md"

DIMENSION_POINTS = 8
STRONG_SCORE = 80
DEVELOPING_SCORE = 65
HEADING_RE = re.compile(r"^##+[ \t]+(.+?)[ \t]*$", re.MULTILINE)
WORD_RE = re.compile(r"\b[\w'-]+\b")
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\$\{?[A-Z][A-Z0-9_]*\}?")

HEADING_ALIASES = {
    "prerequisites": {
        "assumptions",
        "prerequisites",
        "preflight checklist",
        "requirements",
        "before running",
        "before you start",
    },
    "workflow": {
        "example",
        "examples",
        "pattern",
        "workflow",
        "procedure",
        "how to use",
        "design pattern",
        "presets",
    },
    "validation": {
        "success criteria",
        "validation",
        "verify",
        "verification",
        "review the output",
        "what to review",
    },
    "failure_handling": {
        "troubleshooting",
        "failure modes",
        "common failures",
        "common signals",
        "interpreting results",
        "follow-up",
        "what to look for",
    },
    "safety": {"safety", "safety notes", "risk", "risk and safety"},
    "resource_impact": {
        "resource impact",
        "resource and cost",
        "cost and resources",
        "cost and resource impact",
    },
    "cleanup": {"cleanup", "cleanup planning", "rollback", "recovery"},
    "site_boundary": {
        "adaptation points",
        "site adaptation",
        "site notes",
        "local policy",
    },
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_heading(value: str) -> str:
    value = re.sub(r"[`*_]", "", value).strip().lower()
    return re.sub(r"\s+", " ", value)


def headings(text: str) -> Set[str]:
    return {normalize_heading(value) for value in HEADING_RE.findall(text)}


def intro_text(text: str) -> str:
    body = re.sub(r"^#[ \t]+.*$", "", text, count=1, flags=re.MULTILINE).strip()
    return re.split(r"^##[ \t]+", body, maxsplit=1, flags=re.MULTILINE)[0].strip()


def section_text(text: str, aliases: Set[str]) -> str:
    matches = list(HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        if normalize_heading(match.group(1)) not in aliases:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[match.end() : end].strip()
    return ""


def has_heading(found: Set[str], dimension: str) -> bool:
    return bool(found & HEADING_ALIASES[dimension])


def coverage_by_skill(directory: Path) -> Dict[str, int]:
    coverage: Dict[str, int] = defaultdict(int)
    for path in sorted(directory.glob("*.json")):
        payload = load_json(path)
        for skill_id in set(payload.get("skill_ids", [])):
            coverage[skill_id] += 1
    return dict(coverage)


def dimension(
    dimension_id: str, label: str, passed: bool, evidence: str
) -> Dict[str, Any]:
    return {
        "id": dimension_id,
        "label": label,
        "status": "present" if passed else "missing",
        "points": DIMENSION_POINTS if passed else 0,
        "evidence": evidence,
    }


def quality_band(score: int) -> str:
    if score >= STRONG_SCORE:
        return "strong"
    if score >= DEVELOPING_SCORE:
        return "developing"
    return "needs-depth"


def priority_tier(benchmark_count: int, agent_task_count: int) -> str:
    if agent_task_count:
        return "tier-1-agent-evidence"
    if benchmark_count:
        return "tier-2-benchmark"
    return "tier-3-registry"


def assess_skill(
    manifest_path: Path,
    benchmark_coverage: Dict[str, int],
    agent_coverage: Dict[str, int],
) -> Dict[str, Any]:
    manifest = load_json(manifest_path)
    skill_id = manifest["id"]
    readme_path = manifest_path.parent / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    found_headings = headings(text)
    words = len(WORD_RE.findall(text))
    safety_text = section_text(text, HEADING_ALIASES["safety"])
    lower_text = text.lower()

    scope_present = len(WORD_RE.findall(intro_text(text))) >= 20
    prerequisites_present = has_heading(found_headings, "prerequisites")
    workflow_present = has_heading(found_headings, "workflow")
    io_present = bool(manifest.get("inputs")) and bool(manifest.get("outputs"))
    validation_present = has_heading(found_headings, "validation")
    failure_present = has_heading(found_headings, "failure_handling")
    safety_present = has_heading(found_headings, "safety") and len(safety_text) >= 40

    resource_terms = re.search(
        r"\b(cpu|gpu|memory|storage|network|filesystem|allocation|quota|wall ?time|shared)\b",
        safety_text.lower(),
    )
    impact_terms = re.search(
        r"\b(cost|expensive|consume|resource|load|write|move|delete|request|impact)\w*\b",
        safety_text.lower(),
    )
    resource_present = has_heading(found_headings, "resource_impact") or bool(
        resource_terms and impact_terms
    )

    no_cleanup_needed = bool(
        re.search(
            r"\b(read-only|plan-only|does not (?:write|create|modify)|no files? (?:are|is) written)\b",
            lower_text,
        )
    )
    cleanup_present = has_heading(found_headings, "cleanup") or no_cleanup_needed
    site_present = has_heading(found_headings, "site_boundary") or bool(
        PLACEHOLDER_RE.search(text)
        and re.search(r"\b(site|local|cluster|partition|account|queue|module)\b", lower_text)
    )

    dimensions = [
        dimension("scope", "Scope and intended use", scope_present, "README introduction"),
        dimension(
            "prerequisites",
            "Prerequisites and assumptions",
            prerequisites_present,
            "explicit prerequisites/assumptions section",
        ),
        dimension("workflow", "Step-by-step workflow", workflow_present, "workflow/example section"),
        dimension("inputs_outputs", "Inputs and outputs", io_present, "manifest inputs and outputs"),
        dimension("validation", "Validation and success criteria", validation_present, "validation section"),
        dimension("failure_handling", "Failure handling", failure_present, "troubleshooting/failure section"),
        dimension("safety", "Safety and side effects", safety_present, "substantive safety section"),
        dimension("resource_impact", "Resource and cost impact", resource_present, "resource impact evidence"),
        dimension("cleanup", "Cleanup or no-cleanup rationale", cleanup_present, "cleanup/rollback or read-only rationale"),
        dimension("site_boundary", "Site and privacy boundary", site_present, "site placeholders or adaptation section"),
    ]

    example_count = len(manifest.get("examples", []))
    reference_count = len(manifest.get("references", []))
    benchmark_count = benchmark_coverage.get(skill_id, 0)
    agent_task_count = agent_coverage.get(skill_id, 0)
    bonus = 0
    bonus_evidence = []
    if words >= 300:
        bonus += 6
        bonus_evidence.append("README >=300 words (+6)")
    elif words >= 200:
        bonus += 3
        bonus_evidence.append("README >=200 words (+3)")
    if example_count >= 3:
        bonus += 4
        bonus_evidence.append("3+ examples (+4)")
    elif example_count >= 2:
        bonus += 2
        bonus_evidence.append("2 examples (+2)")
    if reference_count >= 3:
        bonus += 4
        bonus_evidence.append("3+ references (+4)")
    elif reference_count >= 2:
        bonus += 2
        bonus_evidence.append("2 references (+2)")
    if benchmark_count:
        bonus += 3
        bonus_evidence.append("static/fixture benchmark (+3)")
    if agent_task_count:
        bonus += 3
        bonus_evidence.append("agent benchmark task (+3)")

    score = min(100, sum(item["points"] for item in dimensions) + bonus)
    gaps = [item["id"] for item in dimensions if item["status"] == "missing"]
    if words < 200:
        gaps.append("documentation_depth")
    if example_count < 2:
        gaps.append("example_depth")
    if reference_count < 2:
        gaps.append("reference_depth")

    return {
        "id": skill_id,
        "name": manifest["name"],
        "version": manifest["version"],
        "status": manifest["status"],
        "risk_level": manifest["risk_level"],
        "maturity": manifest["maturity"],
        "categories": manifest["categories"],
        "score": score,
        "band": quality_band(score),
        "release_priority": priority_tier(benchmark_count, agent_task_count),
        "word_count": words,
        "example_count": example_count,
        "reference_count": reference_count,
        "benchmark_case_count": benchmark_count,
        "agent_task_count": agent_task_count,
        "dimensions": dimensions,
        "bonus_points": bonus,
        "bonus_evidence": bonus_evidence,
        "gaps": gaps,
        "readme": str(readme_path.relative_to(ROOT)),
    }


def quality_payload() -> Dict[str, Any]:
    benchmark_coverage = coverage_by_skill(BENCHMARK_CASE_DIR)
    agent_coverage = coverage_by_skill(AGENT_TASK_DIR)
    skills = [
        assess_skill(path, benchmark_coverage, agent_coverage)
        for path in sorted(SKILLS_DIR.glob("*/skill.json"))
    ]
    skills.sort(
        key=lambda item: (
            {"tier-1-agent-evidence": 0, "tier-2-benchmark": 1, "tier-3-registry": 2}[
                item["release_priority"]
            ],
            item["score"],
            item["id"],
        )
    )
    raw_band_counts = Counter(item["band"] for item in skills)
    raw_priority_counts = Counter(item["release_priority"] for item in skills)
    band_counts = {
        band: raw_band_counts.get(band, 0)
        for band in ("strong", "developing", "needs-depth")
    }
    priority_counts = {
        priority: raw_priority_counts.get(priority, 0)
        for priority in (
            "tier-1-agent-evidence",
            "tier-2-benchmark",
            "tier-3-registry",
        )
    }
    return {
        "$schema": "../schemas/skill-quality-report.schema.json",
        "schema_version": "0.1.0",
        "generated_by": "tools/build_skill_quality.py",
        "skill_count": len(skills),
        "average_score": round(statistics.mean(item["score"] for item in skills), 2),
        "median_score": round(statistics.median(item["score"] for item in skills), 2),
        "thresholds": {"strong": STRONG_SCORE, "developing": DEVELOPING_SCORE},
        "band_counts": band_counts,
        "priority_counts": priority_counts,
        "skills": skills,
    }


def markdown_table_rows(skills: Iterable[Dict[str, Any]]) -> List[str]:
    rows = []
    for skill in skills:
        gaps = ", ".join(f"`{gap}`" for gap in skill["gaps"]) or "None detected"
        rows.append(
            f"| [`{skill['id']}`](../{skill['readme']}) | {skill['score']} | "
            f"{skill['band']} | {skill['release_priority']} | {skill['word_count']} | "
            f"{skill['example_count']} | {skill['reference_count']} | {gaps} |"
        )
    return rows


def build_markdown(payload: Dict[str, Any]) -> str:
    priority_skills = [
        item for item in payload["skills"] if item["release_priority"] != "tier-3-registry"
    ]
    lines = [
        "# Skill Quality Baseline",
        "",
        "This report is generated by `tools/build_skill_quality.py`. It measures",
        "reviewable evidence and documentation coverage; it does not certify safety,",
        "correctness, maturity, or field use. Text length contributes at most six points.",
        "",
        "## Summary",
        "",
        f"- Skills: {payload['skill_count']}",
        f"- Average score: {payload['average_score']}",
        f"- Median score: {payload['median_score']}",
        f"- Strong (`>= {STRONG_SCORE}`): {payload['band_counts'].get('strong', 0)}",
        f"- Developing (`>= {DEVELOPING_SCORE}`): {payload['band_counts'].get('developing', 0)}",
        f"- Needs depth: {payload['band_counts'].get('needs-depth', 0)}",
        f"- Agent-evidence priority: {payload['priority_counts'].get('tier-1-agent-evidence', 0)}",
        f"- Static/fixture benchmark priority: {payload['priority_counts'].get('tier-2-benchmark', 0)}",
        "",
        "## Method",
        "",
        "Each skill receives eight points for each visible dimension: scope,",
        "prerequisites, workflow, inputs/outputs, validation, failure handling,",
        "safety, resource impact, cleanup or a no-cleanup rationale, and site",
        "boundary. Up to 20 bonus points come from bounded documentation depth,",
        "examples, references, and benchmark coverage. Missing dimensions are",
        "review prompts, not automatic proof that a skill is wrong.",
        "",
        "## Release Priority",
        "",
        "| Skill | Score | Band | Priority | Words | Examples | References | Gaps |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | --- |",
        *markdown_table_rows(priority_skills),
        "",
        "## Full Registry",
        "",
        "| Skill | Score | Band | Priority | Words | Examples | References | Gaps |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | --- |",
        *markdown_table_rows(payload["skills"]),
        "",
    ]
    return "\n".join(lines)


def check_outputs(payload: Dict[str, Any]) -> List[str]:
    errors = []
    expected_json = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    expected_markdown = build_markdown(payload)
    if not QUALITY_JSON.exists():
        errors.append(f"{QUALITY_JSON.relative_to(ROOT)} is missing")
    elif QUALITY_JSON.read_text(encoding="utf-8") != expected_json:
        errors.append(f"{QUALITY_JSON.relative_to(ROOT)} is stale; run tools/build_skill_quality.py")
    if not QUALITY_MD.exists():
        errors.append(f"{QUALITY_MD.relative_to(ROOT)} is missing")
    elif QUALITY_MD.read_text(encoding="utf-8") != expected_markdown:
        errors.append(f"{QUALITY_MD.relative_to(ROOT)} is stale; run tools/build_skill_quality.py")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the skill quality baseline")
    parser.add_argument("--check", action="store_true", help="Fail if generated outputs are stale")
    parser.add_argument("--json", action="store_true", help="Print the report as JSON")
    parser.add_argument("--skill", help="Print one skill assessment")
    args = parser.parse_args()

    payload = quality_payload()
    if args.skill:
        skill = next((item for item in payload["skills"] if item["id"] == args.skill), None)
        if skill is None:
            print(f"ERROR: unknown skill {args.skill}", file=sys.stderr)
            return 1
        print(json.dumps(skill, indent=2, sort_keys=True))
        return 0
    if args.check:
        errors = check_outputs(payload)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Skill quality baseline is current for {payload['skill_count']} skill(s).")
        return 0
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    write_json(QUALITY_JSON, payload)
    QUALITY_MD.write_text(build_markdown(payload), encoding="utf-8")
    print(f"Wrote {QUALITY_JSON.relative_to(ROOT)} and {QUALITY_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
