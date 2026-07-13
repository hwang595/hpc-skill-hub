"""Evidence-backed maturity review contracts and generated status helpers."""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REVIEW_SCHEMA_POINTER = "../../schemas/skill-review.schema.json"
STATUS_SCHEMA_POINTER = "../schemas/skill-review-status.schema.json"
SCHEMA_VERSION = "0.1.0"
RELEASE_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")
COMMIT_RE = re.compile(r"^[a-f0-9]{40}$")
STATUS_ORDER = ("blocked", "awaiting-review", "promotion-ready", "promoted")


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(root: Path, value: Any) -> Optional[Path]:
    if not isinstance(value, str) or not value:
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def quality_by_id(quality: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        item["id"]: item
        for item in quality.get("skills", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def skill_by_id(index: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        item["id"]: item
        for item in index.get("skills", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def approved_review(reviews: Any, review_commit: Any) -> bool:
    if not isinstance(reviews, list) or not isinstance(review_commit, str):
        return False
    return any(
        isinstance(review, dict)
        and review.get("decision") == "approved"
        and review.get("independence_attestation") is True
        and review.get("review_commit") == review_commit
        for review in reviews
    )


def validate_review_entries(
    reviews: Any, label: str, errors: List[str]
) -> None:
    if not isinstance(reviews, list):
        errors.append(f"{label} must be an array")
        return
    identities = set()
    for index, review in enumerate(reviews):
        context = f"{label}[{index}]"
        if not isinstance(review, dict):
            errors.append(f"{context} must be an object")
            continue
        for key in (
            "reviewer",
            "domain",
            "decision",
            "reviewed_at",
            "review_commit",
            "evidence_url",
            "independence_attestation",
        ):
            if key not in review:
                errors.append(f"{context} missing {key}")
        reviewer = review.get("reviewer")
        if not isinstance(reviewer, str) or not reviewer.strip():
            errors.append(f"{context}.reviewer must be non-empty")
        elif reviewer in identities:
            errors.append(f"{label} contains duplicate reviewer {reviewer}")
        else:
            identities.add(reviewer)
        if review.get("decision") not in {"approved", "changes-requested"}:
            errors.append(f"{context}.decision is invalid")
        if review.get("independence_attestation") is not True:
            errors.append(f"{context}.independence_attestation must be true")
        if not COMMIT_RE.fullmatch(str(review.get("review_commit", ""))):
            errors.append(f"{context}.review_commit must be a full Git commit")
        evidence_url = review.get("evidence_url")
        if not isinstance(evidence_url, str) or not evidence_url.startswith("https://"):
            errors.append(f"{context}.evidence_url must be a public HTTPS URL")


def evidence_paths(
    root: Path,
    values: Any,
    label: str,
    skill_id: str,
    errors: List[str],
    require_skill_reference: bool = False,
) -> List[str]:
    if not isinstance(values, list) or not values:
        errors.append(f"evidence.{label} must contain at least one path")
        return []
    paths: List[str] = []
    for value in values:
        path = repo_path(root, value)
        if path is None:
            errors.append(f"evidence.{label} contains unsafe path {value!r}")
            continue
        if not path.is_file():
            errors.append(f"evidence.{label} path does not exist: {value}")
            continue
        if require_skill_reference:
            try:
                payload = load_json(path)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append(f"evidence.{label} cannot load {value}: {exc}")
                continue
            if skill_id not in payload.get("skill_ids", []):
                errors.append(f"evidence.{label} {value} does not reference {skill_id}")
                continue
        paths.append(value)
    if paths != sorted(set(paths)):
        errors.append(f"evidence.{label} paths must be unique and sorted")
    return paths


def requirement(
    requirement_id: str, passed: bool, detail: str, category: str
) -> Dict[str, Any]:
    return {
        "id": requirement_id,
        "status": "passed" if passed else "pending",
        "category": category,
        "detail": detail,
    }


def assess_bundle(
    root: Path,
    bundle_path: Path,
    index: Dict[str, Any],
    quality: Dict[str, Any],
) -> Dict[str, Any]:
    errors: List[str] = []
    try:
        bundle = load_json(bundle_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "id": bundle_path.stem,
            "name": bundle_path.stem,
            "version": "unknown",
            "release": "unknown",
            "current_maturity": "unknown",
            "target_maturity": "reviewed",
            "risk_level": "high",
            "status": "blocked",
            "static_ready": False,
            "promotion_ready": False,
            "safety_review_required": False,
            "quality": {"score": 0, "band": "unknown", "gaps": []},
            "evidence": {"benchmark_case_count": 0, "agent_task_count": 0},
            "requirements": [],
            "blockers": [{"id": "invalid-bundle", "detail": str(exc)}],
            "validation_errors": [str(exc)],
            "bundle_path": str(bundle_path.relative_to(root)),
            "bundle_sha256": sha256(bundle_path) if bundle_path.is_file() else "0" * 64,
            "review_issue": None,
            "review_commit": None,
        }

    required = (
        "$schema",
        "schema_version",
        "review_id",
        "release",
        "target_maturity",
        "skill",
        "quality_snapshot",
        "evidence",
        "review_issue",
        "review_commit",
        "domain_reviews",
        "safety_reviews",
        "decision",
    )
    for key in required:
        if key not in bundle:
            errors.append(f"missing {key}")
    if bundle.get("$schema") != REVIEW_SCHEMA_POINTER:
        errors.append(f"expected $schema {REVIEW_SCHEMA_POINTER}")
    if bundle.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"expected schema_version {SCHEMA_VERSION}")
    release = bundle.get("release")
    if not isinstance(release, str) or not RELEASE_RE.fullmatch(release):
        errors.append("release must use vMAJOR.MINOR.PATCH")
        release = "unknown"

    skill_ref = bundle.get("skill")
    if not isinstance(skill_ref, dict):
        errors.append("skill must be an object")
        skill_ref = {}
    skill_id = str(skill_ref.get("id", bundle_path.stem))
    skills = skill_by_id(index)
    current = skills.get(skill_id)
    if current is None:
        errors.append(f"unknown skill {skill_id}")
        current = {
            "id": skill_id,
            "name": skill_id,
            "version": "unknown",
            "maturity": "unknown",
            "risk_level": "high",
            "categories": [],
            "readme": "",
            "examples": [],
        }
    if bundle.get("review_id") != f"{release}/{skill_id}":
        errors.append("review_id must equal <release>/<skill-id>")
    if bundle.get("target_maturity") != "reviewed":
        errors.append("P2A review bundles must target reviewed maturity")
    for key in ("version", "maturity", "risk_level"):
        if skill_ref.get(key) != current.get(key):
            errors.append(f"skill.{key} does not match registry index")

    quality_map = quality_by_id(quality)
    current_quality = quality_map.get(skill_id, {})
    snapshot = bundle.get("quality_snapshot")
    if not isinstance(snapshot, dict):
        errors.append("quality_snapshot must be an object")
        snapshot = {}
    for key in ("score", "band", "gaps"):
        if snapshot.get(key) != current_quality.get(key):
            errors.append(f"quality_snapshot.{key} is stale")

    evidence = bundle.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence must be an object")
        evidence = {}
    readme = evidence.get("readme")
    readme_path = repo_path(root, readme)
    if readme != current.get("readme") or readme_path is None or not readme_path.is_file():
        errors.append("evidence.readme must match the current registry README")
    examples = evidence_paths(root, evidence.get("examples"), "examples", skill_id, errors)
    current_examples = sorted(
        item.get("path") for item in current.get("examples", []) if item.get("path")
    )
    if examples and examples != current_examples:
        errors.append("evidence.examples must match current registry examples")
    benchmark_cases = evidence_paths(
        root,
        evidence.get("benchmark_cases"),
        "benchmark_cases",
        skill_id,
        errors,
        require_skill_reference=True,
    )
    agent_tasks = evidence_paths(
        root,
        evidence.get("agent_tasks"),
        "agent_tasks",
        skill_id,
        errors,
        require_skill_reference=True,
    )
    adoption_reports = evidence.get("adoption_reports", [])
    if not isinstance(adoption_reports, list):
        errors.append("evidence.adoption_reports must be an array")
        adoption_reports = []

    review_issue = bundle.get("review_issue")
    issue_valid = isinstance(review_issue, str) and review_issue.startswith("https://")
    if review_issue is not None and not issue_valid:
        errors.append("review_issue must be null or a public HTTPS URL")
    review_commit = bundle.get("review_commit")
    commit_valid = isinstance(review_commit, str) and bool(COMMIT_RE.fullmatch(review_commit))
    if review_commit is not None and not commit_valid:
        errors.append("review_commit must be null or a full Git commit")

    domain_reviews = bundle.get("domain_reviews", [])
    safety_reviews = bundle.get("safety_reviews", [])
    validate_review_entries(domain_reviews, "domain_reviews", errors)
    validate_review_entries(safety_reviews, "safety_reviews", errors)
    safety_required = current.get("risk_level") != "low" or "admin" in current.get(
        "categories", []
    )

    decision = bundle.get("decision")
    if not isinstance(decision, dict):
        errors.append("decision must be an object")
        decision = {}
    decision_status = decision.get("status")
    if decision_status not in {"pending", "approved", "rejected"}:
        errors.append("decision.status is invalid")
    if decision_status == "approved":
        if not isinstance(decision.get("decided_by"), str):
            errors.append("approved decision requires decided_by")
        if not isinstance(decision.get("decided_at"), str):
            errors.append("approved decision requires decided_at")

    quality_strong = current_quality.get("band") == "strong"
    quality_complete = current_quality.get("gaps") == []
    domain_approved = approved_review(domain_reviews, review_commit)
    safety_approved = not safety_required or approved_review(safety_reviews, review_commit)
    decision_approved = decision_status == "approved"
    requirements = [
        requirement("quality-strong", quality_strong, "Quality band is strong.", "static"),
        requirement("quality-gaps-closed", quality_complete, "Quality report has no gaps.", "static"),
        requirement("benchmark-evidence", bool(benchmark_cases), "At least one static or fixture benchmark references the skill.", "static"),
        requirement("agent-task-evidence", bool(agent_tasks), "At least one agent benchmark task references the skill.", "static"),
        requirement("public-review-issue", issue_valid, "A public maturity-review issue is linked.", "review"),
        requirement("review-commit", commit_valid, "Review is pinned to one full Git commit.", "review"),
        requirement("domain-review", domain_approved, "An independent domain reviewer approved the pinned commit.", "review"),
        requirement("safety-review", safety_approved, "Required safety review approved the pinned commit.", "review"),
        requirement("maintainer-decision", decision_approved, "A maintainer recorded the final promotion decision.", "review"),
    ]
    static_ready = not errors and all(
        item["status"] == "passed"
        for item in requirements
        if item["category"] == "static"
    )
    blockers = [
        {"id": item["id"], "detail": item["detail"]}
        for item in requirements
        if item["status"] != "passed"
    ]
    blockers.extend({"id": "invalid-bundle", "detail": error} for error in errors)
    promotion_ready = static_ready and not blockers
    if not static_ready:
        status = "blocked"
    elif promotion_ready and current.get("maturity") == "reviewed":
        status = "promoted"
    elif promotion_ready:
        status = "promotion-ready"
    else:
        status = "awaiting-review"

    return {
        "id": skill_id,
        "name": current.get("name", skill_id),
        "version": current.get("version", "unknown"),
        "release": release,
        "current_maturity": current.get("maturity", "unknown"),
        "target_maturity": "reviewed",
        "risk_level": current.get("risk_level", "high"),
        "status": status,
        "static_ready": static_ready,
        "promotion_ready": promotion_ready,
        "safety_review_required": safety_required,
        "quality": {
            "score": current_quality.get("score", 0),
            "band": current_quality.get("band", "unknown"),
            "gaps": current_quality.get("gaps", []),
        },
        "evidence": {
            "readme": current.get("readme", ""),
            "example_count": len(examples),
            "benchmark_case_count": len(benchmark_cases),
            "agent_task_count": len(agent_tasks),
            "adoption_report_count": len(adoption_reports),
        },
        "review_issue": review_issue,
        "review_commit": review_commit,
        "requirements": requirements,
        "blockers": blockers,
        "validation_errors": errors,
        "bundle_path": str(bundle_path.relative_to(root)),
        "bundle_sha256": sha256(bundle_path),
    }


def build_status(root: Path, release: str) -> Dict[str, Any]:
    if not RELEASE_RE.fullmatch(release):
        raise ValueError("release must use vMAJOR.MINOR.PATCH")
    index = load_json(root / "registry" / "index.json")
    quality = load_json(root / "registry" / "skill-quality.json")
    bundle_dir = root / "reviews" / release
    paths = sorted(bundle_dir.glob("*.json")) if bundle_dir.is_dir() else []
    skills = [assess_bundle(root, path, index, quality) for path in paths]
    counts = Counter(item["status"] for item in skills)
    return {
        "$schema": STATUS_SCHEMA_POINTER,
        "schema_version": SCHEMA_VERSION,
        "generated_by": "tools/build_skill_reviews.py",
        "release": release,
        "candidate_count": len(skills),
        "static_ready_count": sum(item["static_ready"] for item in skills),
        "promotion_ready_count": sum(item["promotion_ready"] for item in skills),
        "status_counts": {status: counts.get(status, 0) for status in STATUS_ORDER},
        "skills": skills,
    }


def markdown_report(payload: Dict[str, Any]) -> str:
    lines = [
        f"# {payload['release']} Skill Review Packet",
        "",
        "This generated packet tracks evidence-backed maturity review without",
        "promoting skills automatically. Static readiness is not domain approval.",
        "",
        "## Summary",
        "",
        f"- Candidates: {payload['candidate_count']}",
        f"- Static ready: {payload['static_ready_count']}",
        f"- Promotion ready: {payload['promotion_ready_count']}",
        f"- Status counts: `{json.dumps(payload['status_counts'], sort_keys=True)}`",
        "",
        "## Candidate Queue",
        "",
        "| Skill | Quality | Risk | Status | Safety review | Blockers |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for skill in payload["skills"]:
        blockers = ", ".join(item["id"] for item in skill["blockers"]) or "None"
        lines.append(
            f"| `{skill['id']}` | {skill['quality']['score']} | "
            f"`{skill['risk_level']}` | `{skill['status']}` | "
            f"{'required' if skill['safety_review_required'] else 'not required'} | "
            f"{blockers} |"
        )
    lines.extend(
        [
            "",
            "## Promotion Boundary",
            "",
            "- Open and link a public maturity-review issue.",
            "- Pin review to one full Git commit.",
            "- Record an independent domain approval for that commit.",
            "- Complete safety review when risk or admin scope requires it.",
            "- Record a maintainer decision before changing `skill.json` maturity.",
            "- Adoption evidence is optional for `reviewed` and required later for `field-tested`.",
            "",
        ]
    )
    return "\n".join(lines)


def dashboard(payload: Dict[str, Any]) -> str:
    rows = []
    for skill in payload["skills"]:
        blockers = "".join(
            f"<li><code>{html.escape(item['id'])}</code></li>"
            for item in skill["blockers"]
        ) or "<li>None</li>"
        rows.append(
            "<tr>"
            f"<td><strong>{html.escape(skill['name'])}</strong><br><code>{html.escape(skill['id'])}</code></td>"
            f"<td>{skill['quality']['score']}<br><span>{html.escape(skill['quality']['band'])}</span></td>"
            f"<td>{html.escape(skill['risk_level'])}</td>"
            f"<td><span class=\"status status-{html.escape(skill['status'])}\">{html.escape(skill['status'])}</span></td>"
            f"<td>{'Required' if skill['safety_review_required'] else 'Not required'}</td>"
            f"<td><ul>{blockers}</ul></td>"
            f"<td><a href=\"../{html.escape(skill['bundle_path'])}\">Bundle</a></td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(payload['release'])} Skill Review Dashboard</title>
  <style>
    :root {{ color-scheme: light; --ink:#18212b; --muted:#5c6875; --line:#d9dee3; --surface:#f5f7f8; --green:#176b4d; --amber:#8a5a00; --red:#9c2f2f; }}
    * {{ box-sizing:border-box; }} body {{ margin:0; color:var(--ink); background:white; font:15px/1.5 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; letter-spacing:0; }}
    header {{ border-bottom:1px solid var(--line); background:var(--surface); }} .wrap {{ width:min(1180px,calc(100% - 32px)); margin:auto; }}
    header .wrap {{ padding:28px 0 24px; }} h1 {{ margin:0 0 6px; font-size:26px; letter-spacing:0; }} p {{ margin:0; color:var(--muted); }}
    .stats {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1px; margin:24px 0; border:1px solid var(--line); background:var(--line); }}
    .stat {{ background:white; padding:18px; }} .stat strong {{ display:block; font-size:25px; }} .stat span {{ color:var(--muted); }}
    .table-wrap {{ overflow:auto; border:1px solid var(--line); margin-bottom:32px; }} table {{ width:100%; border-collapse:collapse; min-width:900px; }}
    th,td {{ padding:12px; text-align:left; vertical-align:top; border-bottom:1px solid var(--line); }} th {{ background:var(--surface); font-size:13px; }}
    td ul {{ margin:0; padding-left:18px; }} code {{ font-size:13px; }} a {{ color:#075b9a; }} .status {{ font-weight:700; }}
    .status-awaiting-review {{ color:var(--amber); }} .status-promotion-ready,.status-promoted {{ color:var(--green); }} .status-blocked {{ color:var(--red); }}
    .boundary {{ padding:0 0 40px; }} .boundary h2 {{ font-size:18px; }} .boundary ul {{ padding-left:20px; }}
    @media (max-width:700px) {{ .stats {{ grid-template-columns:1fr; }} h1 {{ font-size:22px; }} }}
  </style>
</head>
<body>
  <header><div class="wrap"><h1>{html.escape(payload['release'])} Skill Review Dashboard</h1><p>Static readiness, external review requirements, and maturity promotion blockers.</p></div></header>
  <main class="wrap">
    <section class="stats" aria-label="Review summary">
      <div class="stat"><strong>{payload['candidate_count']}</strong><span>Candidates</span></div>
      <div class="stat"><strong>{payload['static_ready_count']}</strong><span>Static ready</span></div>
      <div class="stat"><strong>{payload['promotion_ready_count']}</strong><span>Promotion ready</span></div>
    </section>
    <div class="table-wrap"><table><thead><tr><th>Skill</th><th>Quality</th><th>Risk</th><th>Status</th><th>Safety</th><th>Blockers</th><th>Evidence</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
    <section class="boundary"><h2>Promotion boundary</h2><p>Benchmark coverage and static quality can make a skill review-ready. Only public, commit-pinned independent review and a maintainer decision can make it promotion-ready.</p></section>
  </main>
</body>
</html>
"""


def candidates_text(payload: Dict[str, Any]) -> str:
    lines = [f"Review candidates for {payload['release']}"]
    for skill in payload["skills"]:
        lines.append(
            f"- {skill['id']}: {skill['status']}; quality={skill['quality']['score']}; "
            f"risk={skill['risk_level']}; blockers={len(skill['blockers'])}"
        )
    return "\n".join(lines)


def skill_status_text(skill: Dict[str, Any]) -> str:
    lines = [
        f"{skill['name']} ({skill['id']})",
        f"Release: {skill['release']}",
        f"Maturity: {skill['current_maturity']} -> {skill['target_maturity']}",
        f"Status: {skill['status']}",
        f"Static ready: {'yes' if skill['static_ready'] else 'no'}",
        f"Promotion ready: {'yes' if skill['promotion_ready'] else 'no'}",
        f"Bundle: {skill['bundle_path']}",
        "Blockers:",
    ]
    lines.extend(
        f"- {item['id']}: {item['detail']}" for item in skill["blockers"]
    )
    if not skill["blockers"]:
        lines.append("- None")
    return "\n".join(lines)
