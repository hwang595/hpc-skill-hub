#!/usr/bin/env python3
"""Prepare, validate, reconcile, and finalize blinded agent benchmark reviews."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
SRC_DIR = ROOT / "src"
for import_path in (TOOLS_DIR, SRC_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

import agent_benchmark_harness as harness
import audit_safety
import run_agent_benchmarks as benchmark_runner
from hpc_skill_hub.security import scan_target


PACKET_SCHEMA = "https://hpc-skill-hub.org/schemas/agent-benchmark-review-packet.schema.json"
REVIEW_SCHEMA = "https://hpc-skill-hub.org/schemas/agent-benchmark-review.schema.json"
RECONCILIATION_SCHEMA = (
    "https://hpc-skill-hub.org/schemas/agent-benchmark-reconciliation.schema.json"
)
MAPPING_SCHEMA_VERSION = "0.1.0"
DISAGREEMENT_THRESHOLD = 0.25
PACKET_REQUIRED_FIELDS = {
    "$schema",
    "schema_version",
    "packet_id",
    "plan_id",
    "created_at",
    "redaction",
    "case_count",
    "cases",
}
PACKET_CASE_REQUIRED_FIELDS = {
    "blind_id",
    "task_id",
    "task_version",
    "response_path",
    "rubric_path",
    "score_template_path",
    "response_sha256",
    "rubric_sha256",
    "score_template_sha256",
}
REVIEW_REQUIRED_FIELDS = {
    "$schema",
    "blind_id",
    "task_id",
    "task_version",
    "reviewer_id",
    "reviewer_type",
    "submitted_at",
    "scores",
    "notes",
}
RECONCILIATION_REQUIRED_FIELDS = {
    "$schema",
    "blind_id",
    "task_id",
    "task_version",
    "reviewer_ids",
    "reconciled_by",
    "reconciled_at",
    "scores",
    "notes",
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


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_timestamp(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{context} must be a non-empty timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{context} is not a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{context} must include a timezone")
    return value


def path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def prepare_target(path: Path, force: bool) -> None:
    if path.exists():
        if not force:
            raise ValueError(f"output already exists: {path}; pass --force to replace it")
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    path.mkdir(parents=True, exist_ok=True)


def blind_id(salt: bytes, run_id: str) -> str:
    digest = hmac.new(salt, run_id.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"case-{digest[:12]}"


def load_plan(plan_path: Path) -> Dict[str, Any]:
    payload = harness.plan_payload(plan_path)
    if not payload["ok"]:
        raise ValueError("invalid benchmark plan: " + "; ".join(payload["validation_errors"]))
    return payload


def validate_pending_result(
    result_path: Path, result: Dict[str, Any], run: Dict[str, Any], tasks: Dict[str, Dict[str, Any]]
) -> None:
    candidate = dict(result)
    candidate["_path"] = result_path
    errors = harness.result_identity_errors(run, candidate)
    errors.extend(benchmark_runner.validate_result(candidate, tasks))
    if result.get("status") != "pending-review":
        errors.append("review preparation requires status pending-review")
    if result.get("model") in {None, "", "configured-default"}:
        errors.append("review preparation requires an exact model id")
    provenance = result.get("provenance", {})
    if provenance.get("repository_dirty") is not False:
        errors.append("review preparation requires a clean repository snapshot")
    if provenance.get("network_access") is not False:
        errors.append("review preparation requires network_access=false")
    if errors:
        raise ValueError(f"invalid pending result {result_path}: " + "; ".join(errors))


def source_final_output(run_root: Path, result: Dict[str, Any]) -> Path:
    run_id = result["run_id"]
    source = run_root / "artifacts" / run_id / "final-output.txt"
    if not source.is_file():
        raise ValueError(f"missing final output for {run_id}: {source}")
    entries = [
        entry
        for entry in result.get("artifacts", [])
        if isinstance(entry, dict) and str(entry.get("path", "")).endswith("/final-output.txt")
    ]
    if len(entries) != 1:
        raise ValueError(f"{run_id} must reference exactly one final-output.txt artifact")
    if entries[0].get("sha256") != sha256_path(source):
        raise ValueError(f"final output digest mismatch for {run_id}")
    return source


def redaction_findings(path: Path) -> Tuple[List[str], List[Dict[str, Any]]]:
    public_safety = audit_safety.audit_file(path)
    security_report = scan_target(path, fail_on="high")
    blocking_security = [
        finding
        for finding in security_report["findings"]
        if finding["severity"] in {"high", "critical"}
    ]
    return public_safety, blocking_security


def score_template(case_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "$schema": REVIEW_SCHEMA,
        "blind_id": case_id,
        "task_id": task["id"],
        "task_version": task["version"],
        "reviewer_id": "<reviewer-id>",
        "reviewer_type": "human",
        "submitted_at": "<ISO-8601 timestamp>",
        "scores": [
            {"criterion_id": item["id"], "score": None, "rationale": ""}
            for item in task["rubric"]
        ],
        "notes": "",
    }


def packet_readme() -> str:
    return """# Blinded Agent Benchmark Review Packet

This packet intentionally omits run ids, agents, harnesses, models, and benchmark
conditions. Review only the response and task rubric available for each blind id.

For each case, copy `score-template.json` to
`<reviews-dir>/<reviewer-id>/<blind-id>.json`, replace placeholders, and score every
criterion from 0 to 1. Do not attempt to identify the agent or condition. Reviewers
must work independently before reconciliation.
"""


def prepare_packet(
    plan_path: Path,
    run_root: Path,
    packet_root: Path,
    mapping_path: Path,
    salt_file: Path,
    redaction_reviewer: str,
    force: bool = False,
) -> Dict[str, Any]:
    if path_is_within(mapping_path, packet_root):
        raise ValueError("private mapping must be stored outside the blinded packet root")
    if path_is_within(mapping_path, ROOT) or path_is_within(salt_file, ROOT):
        raise ValueError("private mapping and salt must be stored outside the repository")
    salt = salt_file.read_bytes()
    if len(salt) < 16:
        raise ValueError("salt file must contain at least 16 bytes")
    if not redaction_reviewer.strip():
        raise ValueError("redaction reviewer id must not be empty")

    plan = load_plan(plan_path)
    tasks = harness.load_tasks()
    run_by_id = {run["run_id"]: run for run in plan["runs"]}
    prepared = []
    blind_ids = set()
    for run_id, run in sorted(run_by_id.items()):
        result_path = run_root / "results" / f"{run_id}.json"
        if not result_path.exists():
            continue
        result = load_json(result_path)
        validate_pending_result(result_path, result, run, tasks)
        source = source_final_output(run_root, result)
        safety_findings, security_findings = redaction_findings(source)
        if safety_findings or security_findings:
            details = safety_findings + [
                f"{item['path']}:{item['line']}: {item['rule_id']}: {item['message']}"
                for item in security_findings
            ]
            raise ValueError(f"redaction gate blocked {run_id}: " + "; ".join(details))
        case_id = blind_id(salt, run_id)
        if case_id in blind_ids:
            raise ValueError(f"blind id collision: {case_id}")
        blind_ids.add(case_id)
        prepared.append(
            {
                "blind_id": case_id,
                "run": run,
                "result": result,
                "result_path": result_path,
                "source": source,
                "task": tasks[run["task_id"]],
            }
        )
    if not prepared:
        raise ValueError(f"no pending-review results found for plan {plan['plan']['id']}")

    if mapping_path.exists() and not force:
        raise ValueError(f"private mapping already exists: {mapping_path}; pass --force to replace it")
    prepare_target(packet_root, force)
    packet_root.joinpath("README.md").write_text(packet_readme(), encoding="utf-8")

    packet_cases = []
    mapping_cases = []
    for item in sorted(prepared, key=lambda value: value["blind_id"]):
        case_id = item["blind_id"]
        task = item["task"]
        case_root = packet_root / "cases" / case_id
        case_root.mkdir(parents=True, exist_ok=True)
        response_path = case_root / "response.txt"
        shutil.copy2(item["source"], response_path)
        rubric_path = case_root / "rubric.json"
        write_json(
            rubric_path,
            {
                "blind_id": case_id,
                "task_id": task["id"],
                "task_version": task["version"],
                "name": task["name"],
                "prompt": task["prompt"],
                "rubric": task["rubric"],
                "expected_artifacts": task["expected_artifacts"],
                "expected_outcomes": task["expected_outcomes"],
            },
        )
        template_path = case_root / "score-template.json"
        write_json(template_path, score_template(case_id, task))
        response_digest = sha256_path(response_path)
        packet_cases.append(
            {
                "blind_id": case_id,
                "task_id": task["id"],
                "task_version": task["version"],
                "response_path": str(response_path.relative_to(packet_root)),
                "rubric_path": str(rubric_path.relative_to(packet_root)),
                "score_template_path": str(template_path.relative_to(packet_root)),
                "response_sha256": response_digest,
                "rubric_sha256": sha256_path(rubric_path),
                "score_template_sha256": sha256_path(template_path),
            }
        )
        mapping_cases.append(
            {
                "blind_id": case_id,
                "run_id": item["run"]["run_id"],
                "result_path": str(item["result_path"].resolve()),
                "result_sha256": sha256_path(item["result_path"]),
                "source_output_path": str(item["source"].resolve()),
                "source_output_sha256": sha256_path(item["source"]),
                "redacted_response_sha256": response_digest,
            }
        )

    created_at = harness.utc_now()
    manifest = {
        "$schema": PACKET_SCHEMA,
        "schema_version": "0.1.0",
        "packet_id": f"{plan['plan']['id']}-blinded",
        "plan_id": plan["plan"]["id"],
        "created_at": created_at,
        "redaction": {
            "reviewer_id": redaction_reviewer.strip(),
            "automated_checks": ["audit_safety", "hpc-skill-security-high"],
        },
        "case_count": len(packet_cases),
        "cases": packet_cases,
    }
    manifest_path = packet_root / "manifest.json"
    write_json(manifest_path, manifest)
    mapping = {
        "schema_version": MAPPING_SCHEMA_VERSION,
        "packet_id": manifest["packet_id"],
        "plan_id": manifest["plan_id"],
        "created_at": created_at,
        "salt_sha256": hashlib.sha256(salt).hexdigest(),
        "packet_manifest_sha256": sha256_path(manifest_path),
        "redaction_reviewer_id": redaction_reviewer.strip(),
        "cases": mapping_cases,
    }
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(mapping_path, mapping)
    return {
        "ok": True,
        "packet_id": manifest["packet_id"],
        "case_count": len(packet_cases),
        "packet_root": str(packet_root),
        "mapping_path": str(mapping_path),
    }


def validate_score_items(
    scores: Any, criterion_ids: List[str], context: str
) -> Tuple[List[str], Dict[str, float]]:
    errors = []
    values: Dict[str, float] = {}
    if not isinstance(scores, list):
        return [f"{context}: scores must be an array"], values
    for item in scores:
        if not isinstance(item, dict):
            errors.append(f"{context}: score entry must be an object")
            continue
        criterion_id = item.get("criterion_id")
        score = item.get("score")
        if criterion_id not in criterion_ids:
            errors.append(f"{context}: unknown criterion {criterion_id}")
        elif criterion_id in values:
            errors.append(f"{context}: duplicate criterion {criterion_id}")
        elif not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 1:
            errors.append(f"{context}: score for {criterion_id} must be between 0 and 1")
        else:
            values[criterion_id] = float(score)
        if not isinstance(item.get("rationale"), str) or not item.get("rationale", "").strip():
            errors.append(f"{context}: criterion {criterion_id} requires rationale")
    if set(values) != set(criterion_ids):
        missing = sorted(set(criterion_ids) - set(values))
        if missing:
            errors.append(f"{context}: missing criteria {missing}")
    return errors, values


def validate_review(
    path: Path, payload: Dict[str, Any], case: Dict[str, Any], criterion_ids: List[str]
) -> Tuple[List[str], Dict[str, float]]:
    context = str(path)
    errors = []
    if set(payload) != REVIEW_REQUIRED_FIELDS:
        errors.append(f"{context}: review fields do not match the public contract")
    if payload.get("$schema") != REVIEW_SCHEMA:
        errors.append(f"{context}: invalid review schema")
    for field in ("blind_id", "task_id", "task_version"):
        if payload.get(field) != case[field]:
            errors.append(f"{context}: {field} does not match packet case")
    if not isinstance(payload.get("reviewer_id"), str) or not payload.get("reviewer_id", "").strip():
        errors.append(f"{context}: reviewer_id is required")
    if payload.get("reviewer_type") not in {"human", "llm-assisted"}:
        errors.append(f"{context}: invalid reviewer_type")
    try:
        parse_timestamp(payload.get("submitted_at"), f"{context}: submitted_at")
    except ValueError as exc:
        errors.append(str(exc))
    score_errors, values = validate_score_items(payload.get("scores"), criterion_ids, context)
    errors.extend(score_errors)
    return errors, values


def validate_reconciliation(
    path: Path,
    payload: Dict[str, Any],
    case: Dict[str, Any],
    criterion_ids: List[str],
    reviewer_ids: List[str],
) -> Tuple[List[str], Dict[str, float]]:
    context = str(path)
    errors = []
    if set(payload) != RECONCILIATION_REQUIRED_FIELDS:
        errors.append(f"{context}: reconciliation fields do not match the public contract")
    if payload.get("$schema") != RECONCILIATION_SCHEMA:
        errors.append(f"{context}: invalid reconciliation schema")
    for field in ("blind_id", "task_id", "task_version"):
        if payload.get(field) != case[field]:
            errors.append(f"{context}: {field} does not match packet case")
    submitted_reviewer_ids = payload.get("reviewer_ids")
    if (
        not isinstance(submitted_reviewer_ids, list)
        or len(submitted_reviewer_ids) != 2
        or not all(isinstance(value, str) and value.strip() for value in submitted_reviewer_ids)
        or len(set(submitted_reviewer_ids)) != 2
    ):
        errors.append(f"{context}: reviewer_ids must contain two unique reviewer ids")
    elif sorted(submitted_reviewer_ids) != sorted(reviewer_ids):
        errors.append(f"{context}: reviewer_ids must match the two independent reviews")
    if not isinstance(payload.get("reconciled_by"), str) or not payload.get("reconciled_by", "").strip():
        errors.append(f"{context}: reconciled_by is required")
    try:
        parse_timestamp(payload.get("reconciled_at"), f"{context}: reconciled_at")
    except ValueError as exc:
        errors.append(str(exc))
    score_errors, values = validate_score_items(payload.get("scores"), criterion_ids, context)
    errors.extend(score_errors)
    return errors, values


def review_status(
    packet_root: Path,
    mapping_path: Path,
    reviews_dir: Path,
    reconciliations_dir: Optional[Path] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    manifest_path = packet_root / "manifest.json"
    manifest = load_json(manifest_path)
    mapping = load_json(mapping_path)
    if set(manifest) != PACKET_REQUIRED_FIELDS:
        raise ValueError("packet manifest fields do not match the public contract")
    if manifest.get("$schema") != PACKET_SCHEMA or manifest.get("schema_version") != "0.1.0":
        raise ValueError("packet manifest schema contract is invalid")
    if mapping.get("packet_manifest_sha256") != sha256_path(manifest_path):
        raise ValueError("packet manifest digest does not match private mapping")
    if mapping.get("packet_id") != manifest.get("packet_id"):
        raise ValueError("packet id does not match private mapping")
    manifest_cases = manifest.get("cases", [])
    if not isinstance(manifest_cases, list) or not manifest_cases:
        raise ValueError("packet manifest must contain at least one case")
    if manifest.get("case_count") != len(manifest_cases):
        raise ValueError("packet manifest case_count does not match cases")
    mapping_cases = mapping.get("cases", [])
    if not isinstance(mapping_cases, list):
        raise ValueError("private mapping cases must be an array")
    manifest_ids = [item.get("blind_id") for item in manifest_cases if isinstance(item, dict)]
    mapping_ids = [item.get("blind_id") for item in mapping_cases if isinstance(item, dict)]
    if len(manifest_ids) != len(manifest_cases) or len(set(manifest_ids)) != len(manifest_ids):
        raise ValueError("packet manifest contains invalid or duplicate blind ids")
    if len(mapping_ids) != len(mapping_cases) or len(set(mapping_ids)) != len(mapping_ids):
        raise ValueError("private mapping contains invalid or duplicate blind ids")
    if set(mapping_ids) != set(manifest_ids):
        raise ValueError("packet manifest and private mapping blind ids do not match")
    mapping_by_blind = {item["blind_id"]: item for item in mapping_cases}
    reviews_by_blind: Dict[str, List[Tuple[Path, Dict[str, Any]]]] = defaultdict(list)
    if reviews_dir.exists():
        for path in sorted(reviews_dir.rglob("*.json")):
            payload = load_json(path)
            reviews_by_blind[str(payload.get("blind_id"))].append((path, payload))

    global_errors = []
    unknown_review_ids = sorted(set(reviews_by_blind) - set(manifest_ids))
    if unknown_review_ids:
        global_errors.append(
            "review files reference unknown blind ids: " + ", ".join(unknown_review_ids)
        )
    reconciliation_by_blind: Dict[str, Tuple[Path, Dict[str, Any]]] = {}
    if reconciliations_dir is not None and reconciliations_dir.exists():
        for path in sorted(reconciliations_dir.rglob("*.json")):
            payload = load_json(path)
            case_id = str(payload.get("blind_id"))
            if case_id in reconciliation_by_blind:
                global_errors.append(f"multiple reconciliations found for {case_id}")
            else:
                reconciliation_by_blind[case_id] = (path, payload)
    unknown_reconciliation_ids = sorted(set(reconciliation_by_blind) - set(manifest_ids))
    if unknown_reconciliation_ids:
        global_errors.append(
            "reconciliation files reference unknown blind ids: "
            + ", ".join(unknown_reconciliation_ids)
        )

    task_map = harness.load_tasks()
    cases = []
    internal: Dict[str, Any] = {}
    counts: Dict[str, int] = defaultdict(int)
    for case in manifest_cases:
        case_id = case["blind_id"]
        errors = []
        if set(case) != PACKET_CASE_REQUIRED_FIELDS:
            errors.append("packet case fields do not match the public contract")
        if case_id not in mapping_by_blind:
            errors.append("blind id is missing from private mapping")
        case_mapping = mapping_by_blind.get(case_id)
        for path_field, digest_field in (
            ("response_path", "response_sha256"),
            ("rubric_path", "rubric_sha256"),
            ("score_template_path", "score_template_sha256"),
        ):
            relative_path = case.get(path_field)
            expected_digest = case.get(digest_field)
            if (
                not isinstance(relative_path, str)
                or not relative_path
                or Path(relative_path).is_absolute()
                or ".." in Path(relative_path).parts
            ):
                errors.append(f"{path_field} must be a packet-relative path")
                continue
            packet_path = packet_root / relative_path
            if not packet_path.is_file():
                errors.append(f"missing packet file: {relative_path}")
            elif sha256_path(packet_path) != expected_digest:
                errors.append(f"packet file digest mismatch: {relative_path}")
        if (
            case_mapping is not None
            and case_mapping.get("redacted_response_sha256") != case.get("response_sha256")
        ):
            errors.append("response digest does not match private mapping")
        task = task_map.get(case["task_id"])
        if task is None or task["version"] != case["task_version"]:
            errors.append("task contract is missing or version-mismatched")
            criterion_ids = []
        else:
            criterion_ids = [item["id"] for item in task["rubric"]]
        review_entries = reviews_by_blind.get(case_id, [])
        valid_reviews = []
        reviewer_ids = []
        for path, review in review_entries:
            review_errors, values = validate_review(path, review, case, criterion_ids)
            errors.extend(review_errors)
            valid_reviews.append((review, values))
            reviewer_ids.append(review.get("reviewer_id"))
        review_count_error = None
        if len(review_entries) != 2:
            review_count_error = f"expected exactly 2 reviews, found {len(review_entries)}"
            errors.append(review_count_error)
        valid_reviewer_ids = [value for value in reviewer_ids if isinstance(value, str)]
        if len(valid_reviewer_ids) != len(set(valid_reviewer_ids)):
            errors.append("reviewer ids must be unique")

        disagreements = []
        if len(valid_reviews) == 2 and not errors:
            for criterion_id in criterion_ids:
                delta = abs(valid_reviews[0][1][criterion_id] - valid_reviews[1][1][criterion_id])
                if delta + 1e-12 >= DISAGREEMENT_THRESHOLD:
                    disagreements.append({"criterion_id": criterion_id, "difference": round(delta, 4)})

        reconciliation = None
        final_scores = None
        reconciliation_entry = reconciliation_by_blind.get(case_id)
        if reconciliation_entry is not None:
            reconciliation_path, reconciliation = reconciliation_entry
            reconciliation_errors, values = validate_reconciliation(
                reconciliation_path,
                reconciliation,
                case,
                criterion_ids,
                [str(value) for value in reviewer_ids],
            )
            errors.extend(reconciliation_errors)
            if not reconciliation_errors:
                final_scores = values

        non_count_errors = [item for item in errors if item != review_count_error]
        if len(review_entries) < 2 and not non_count_errors:
            state = "missing-reviews"
        elif errors:
            state = "invalid"
        elif disagreements and reconciliation is None:
            state = "needs-reconciliation"
        else:
            state = "ready"
            if final_scores is None:
                final_scores = {
                    criterion_id: round(
                        (valid_reviews[0][1][criterion_id] + valid_reviews[1][1][criterion_id]) / 2,
                        4,
                    )
                    for criterion_id in criterion_ids
                }
        counts[state] += 1
        cases.append(
            {
                "blind_id": case_id,
                "task_id": case["task_id"],
                "review_count": len(review_entries),
                "reviewer_ids": sorted(str(value) for value in reviewer_ids if value),
                "state": state,
                "disagreements": disagreements,
                "errors": errors,
            }
        )
        internal[case_id] = {
            "case": case,
            "mapping": mapping_by_blind.get(case_id),
            "reviews": [item[0] for item in valid_reviews],
            "reconciliation": reconciliation,
            "final_scores": final_scores,
        }
    report = {
        "ok": counts.get("invalid", 0) == 0 and not global_errors,
        "packet_id": manifest["packet_id"],
        "case_count": len(cases),
        "state_counts": dict(sorted(counts.items())),
        "ready_to_finalize": (
            bool(cases)
            and not global_errors
            and all(item["state"] == "ready" for item in cases)
        ),
        "errors": global_errors,
        "cases": cases,
    }
    return report, internal


def finalize_packet(
    packet_root: Path,
    mapping_path: Path,
    reviews_dir: Path,
    reconciliations_dir: Optional[Path],
    output_root: Path,
    force: bool = False,
) -> Dict[str, Any]:
    if path_is_within(output_root, ROOT):
        raise ValueError("finalized staging output must be stored outside the repository")
    report, internal = review_status(
        packet_root, mapping_path, reviews_dir, reconciliations_dir
    )
    if not report["ready_to_finalize"]:
        details = list(report.get("errors", []))
        for case in report.get("cases", []):
            details.extend(case.get("errors", []))
        suffix = ": " + "; ".join(details) if details else ""
        raise ValueError("review packet is not ready to finalize" + suffix)
    prepare_target(output_root, force)
    tasks = harness.load_tasks()
    tasks_by_id = {task_id: task for task_id, task in tasks.items()}
    finalized = []
    for case_id in sorted(internal):
        item = internal[case_id]
        mapping = item["mapping"]
        if mapping is None:
            raise ValueError(f"missing private mapping for {case_id}")
        result_path = Path(mapping["result_path"])
        if sha256_path(result_path) != mapping["result_sha256"]:
            raise ValueError(f"source result changed after packet preparation: {case_id}")
        response_path = packet_root / item["case"]["response_path"]
        if sha256_path(response_path) != mapping["redacted_response_sha256"]:
            raise ValueError(f"redacted response changed after packet preparation: {case_id}")
        result = load_json(result_path)
        if result.get("status") != "pending-review":
            raise ValueError(f"source result is no longer pending-review: {case_id}")
        reviews = item["reviews"]
        evaluator_ids = sorted(review["reviewer_id"] for review in reviews)
        evaluator_type = (
            "llm-assisted"
            if any(review["reviewer_type"] == "llm-assisted" for review in reviews)
            else "human"
        )
        if item["reconciliation"] is not None:
            scored_at = item["reconciliation"]["reconciled_at"]
        else:
            scored_at = max(review["submitted_at"] for review in reviews)
        task = tasks[result["task_id"]]
        score_order = [criterion["id"] for criterion in task["rubric"]]
        result["status"] = "scored"
        result["criteria_scores"] = [
            {"criterion_id": criterion_id, "score": item["final_scores"][criterion_id]}
            for criterion_id in score_order
        ]
        result["evaluation"] = {
            "rubric_version": task["version"],
            "evaluator_type": evaluator_type,
            "evaluator_ids": evaluator_ids,
            "blinded": True,
            "scored_at": scored_at,
        }
        artifact_target = output_root / "artifacts" / result["run_id"] / "final-output.txt"
        artifact_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(response_path, artifact_target)
        result["artifacts"] = [
            {
                "path": f"agent-bench/artifacts/{result['run_id']}/final-output.txt",
                "description": "Redacted final response used for blinded scoring.",
                "sha256": sha256_path(artifact_target),
            }
        ]
        result["notes"] = (
            result.get("notes", "").rstrip()
            + " Finalized from two independent blinded reviews after redaction."
        ).strip()
        output_path = output_root / "results" / f"{result['run_id']}.json"
        candidate = dict(result)
        candidate["_path"] = output_path
        errors = benchmark_runner.validate_result(candidate, tasks_by_id)
        if errors:
            raise ValueError(f"finalized result is invalid for {case_id}: " + "; ".join(errors))
        write_json(output_path, result)
        finalized.append(result["run_id"])

    safety_findings = []
    for path in sorted(output_root.rglob("*")):
        if path.is_file():
            safety_findings.extend(audit_safety.audit_file(path))
    security = scan_target(output_root, fail_on="high")
    if safety_findings or security["summary"]["blocking_count"]:
        raise ValueError("finalized bundle failed public safety validation")
    benchmark_payload = benchmark_runner.benchmark_payload(
        ROOT / "agent-bench" / "tasks", output_root / "results"
    )
    if not benchmark_payload["ok"]:
        raise ValueError(
            "finalized result bundle failed benchmark validation: "
            + "; ".join(benchmark_payload["validation_errors"])
        )
    return {
        "ok": True,
        "packet_id": report["packet_id"],
        "finalized_count": len(finalized),
        "run_ids": finalized,
        "output_root": str(output_root),
    }


def print_payload(payload: Dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    for key, value in payload.items():
        if key == "cases":
            continue
        print(f"{key}: {value}")
    for case in payload.get("cases", []):
        print(f"- {case['blind_id']}: {case['state']} ({case['review_count']} reviews)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage blinded agent benchmark reviews")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Create a blinded packet from pending results")
    prepare.add_argument("--plan", required=True)
    prepare.add_argument("--run-root", required=True)
    prepare.add_argument("--packet-root", required=True)
    prepare.add_argument("--mapping", required=True)
    prepare.add_argument("--salt-file", required=True)
    prepare.add_argument("--redaction-reviewer", required=True)
    prepare.add_argument("--force", action="store_true")
    prepare.add_argument("--json", action="store_true")

    status = subparsers.add_parser("status", help="Validate reviews and reconciliation state")
    status.add_argument("--packet-root", required=True)
    status.add_argument("--mapping", required=True)
    status.add_argument("--reviews-dir", required=True)
    status.add_argument("--reconciliations-dir")
    status.add_argument("--json", action="store_true")

    finalize = subparsers.add_parser("finalize", help="Build staged scored results")
    finalize.add_argument("--packet-root", required=True)
    finalize.add_argument("--mapping", required=True)
    finalize.add_argument("--reviews-dir", required=True)
    finalize.add_argument("--reconciliations-dir")
    finalize.add_argument("--output-root", required=True)
    finalize.add_argument("--force", action="store_true")
    finalize.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "prepare":
            payload = prepare_packet(
                Path(args.plan),
                Path(args.run_root),
                Path(args.packet_root),
                Path(args.mapping),
                Path(args.salt_file),
                args.redaction_reviewer,
                args.force,
            )
        elif args.command == "status":
            payload, _internal = review_status(
                Path(args.packet_root),
                Path(args.mapping),
                Path(args.reviews_dir),
                Path(args.reconciliations_dir) if args.reconciliations_dir else None,
            )
        else:
            payload = finalize_packet(
                Path(args.packet_root),
                Path(args.mapping),
                Path(args.reviews_dir),
                Path(args.reconciliations_dir) if args.reconciliations_dir else None,
                Path(args.output_root),
                args.force,
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print_payload(payload, args.json)
    if args.command == "status" and not payload["ready_to_finalize"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
