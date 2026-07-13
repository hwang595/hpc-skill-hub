#!/usr/bin/env python3
"""Validate and report reviewed agent benchmark tasks and results."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
AGENT_BENCH_DIR = ROOT / "agent-bench"
TASK_DIR = AGENT_BENCH_DIR / "tasks"
RESULT_DIR = AGENT_BENCH_DIR / "results"
INDEX_JSON = ROOT / "registry" / "index.json"
DEFAULT_REPORT = ROOT / "docs" / "AGENT_BENCHMARK_REPORT.md"
DEFAULT_DASHBOARD = ROOT / "docs" / "AGENT_BENCHMARK_DASHBOARD.html"
PUBLICATION_MIN_PAIRS = 3

TASK_SCHEMA = "../../schemas/agent-benchmark-task.schema.json"
RESULT_SCHEMA = "../../schemas/agent-benchmark-result.schema.json"

ALLOWED_STATUS = {"draft", "reviewed", "deprecated"}
ALLOWED_TASK_TYPES = {"skill-routing", "triage", "safety", "repo-edit", "site-policy"}
ALLOWED_RISK = {"low", "medium", "high"}
ALLOWED_CONDITIONS = {"baseline", "docs-only", "skill-enabled", "skill-site-adapter"}
ALLOWED_RESULT_STATUS = {"pending-review", "scored", "failed", "skipped"}
ALLOWED_WORKSPACE_MODES = {"read-only", "workspace-write"}
ALLOWED_INVOCATION_MODES = {"cli", "api", "manual", "import"}
ALLOWED_EVALUATOR_TYPES = {"human", "deterministic", "llm-assisted"}
ALLOWED_FAILURE_CATEGORIES = {
    "agent-error",
    "timeout",
    "harness-error",
    "policy-blocked",
    "invalid-output",
    "unknown",
}

TASK_REQUIRED_FIELDS = {
    "$schema",
    "id",
    "name",
    "version",
    "status",
    "task_type",
    "risk_level",
    "skill_ids",
    "conditions",
    "summary",
    "prompt",
    "fixtures",
    "execution",
    "rubric",
    "expected_artifacts",
    "expected_outcomes",
}
RESULT_REQUIRED_FIELDS = {
    "$schema",
    "run_id",
    "task_id",
    "task_version",
    "trial",
    "agent",
    "harness",
    "model",
    "condition",
    "started_at",
    "completed_at",
    "status",
    "provenance",
    "metrics",
    "criteria_scores",
    "evaluation",
    "failure",
    "artifacts",
    "notes",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_repo_path(value: str) -> Path:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        raise ValueError(f"path escapes repository: {value}")
    return path


def load_tasks(task_dir: Path = TASK_DIR) -> List[Dict[str, Any]]:
    tasks = []
    for path in sorted(task_dir.glob("*.json")):
        task = load_json(path)
        task["_path"] = path
        tasks.append(task)
    return tasks


def load_results(result_dir: Path = RESULT_DIR) -> List[Dict[str, Any]]:
    results = []
    for path in sorted(result_dir.glob("*.json")):
        result = load_json(path)
        result["_path"] = path
        results.append(result)
    return results


def parse_timestamp(value: Any, context: str, field: str, errors: List[str]) -> Optional[datetime]:
    if not isinstance(value, str):
        errors.append(f"{context}: {field} must be an ISO 8601 date-time string")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            errors.append(f"{context}: {field} must include a timezone")
            return None
        return parsed
    except ValueError:
        errors.append(f"{context}: {field} must be an ISO 8601 date-time string")
        return None


def validate_task(task: Dict[str, Any], known_skills: set[str]) -> List[str]:
    errors: List[str] = []
    context = rel(task["_path"])

    for field in sorted(TASK_REQUIRED_FIELDS - set(task)):
        errors.append(f"{context}: missing required field {field}")
    for field in sorted(set(task) - TASK_REQUIRED_FIELDS - {"_path"}):
        errors.append(f"{context}: unknown field {field}")

    if task.get("$schema") != TASK_SCHEMA:
        errors.append(f"{context}: expected $schema {TASK_SCHEMA}")

    task_id = task.get("id")
    if not isinstance(task_id, str) or not task_id:
        errors.append(f"{context}: id must be a non-empty string")
    elif task_id != task["_path"].stem:
        errors.append(f"{context}: id must match filename")

    if task.get("status") not in ALLOWED_STATUS:
        errors.append(f"{context}: status must be one of {sorted(ALLOWED_STATUS)}")
    if task.get("task_type") not in ALLOWED_TASK_TYPES:
        errors.append(f"{context}: task_type must be one of {sorted(ALLOWED_TASK_TYPES)}")
    if task.get("risk_level") not in ALLOWED_RISK:
        errors.append(f"{context}: risk_level must be one of {sorted(ALLOWED_RISK)}")

    skill_ids = task.get("skill_ids", [])
    if not isinstance(skill_ids, list) or not skill_ids:
        errors.append(f"{context}: skill_ids must be a non-empty list")
    else:
        for skill_id in skill_ids:
            if skill_id not in known_skills:
                errors.append(f"{context}: unknown skill id {skill_id}")

    conditions = task.get("conditions", [])
    if not isinstance(conditions, list) or not conditions:
        errors.append(f"{context}: conditions must be a non-empty list")
        conditions = []
    else:
        if len(conditions) != len(set(conditions)):
            errors.append(f"{context}: conditions must be unique")
        for condition in conditions:
            if condition not in ALLOWED_CONDITIONS:
                errors.append(f"{context}: unknown condition {condition}")

    fixtures = task.get("fixtures", [])
    if not isinstance(fixtures, list):
        errors.append(f"{context}: fixtures must be a list")
        fixtures = []
    for fixture in fixtures:
        path = fixture.get("path") if isinstance(fixture, dict) else None
        fixture_conditions = fixture.get("conditions") if isinstance(fixture, dict) else None
        if not isinstance(path, str):
            errors.append(f"{context}: fixture path must be a string")
            continue
        if not isinstance(fixture_conditions, list) or not fixture_conditions:
            errors.append(f"{context}: fixture {path} must declare conditions")
            fixture_conditions = []
        for condition in fixture_conditions:
            if condition not in conditions:
                errors.append(f"{context}: fixture {path} uses undeclared condition {condition}")
        if path.startswith(("skills/", ".agents/", ".claude/")):
            leaked = sorted(set(fixture_conditions) & {"baseline", "docs-only"})
            if leaked:
                errors.append(f"{context}: skill fixture {path} leaks into {leaked}")
        if path.startswith("site-adapters/") and set(fixture_conditions) != {"skill-site-adapter"}:
            errors.append(
                f"{context}: site adapter fixture {path} must be limited to skill-site-adapter"
            )
        try:
            resolved = resolve_repo_path(path)
        except ValueError as exc:
            errors.append(f"{context}: {exc}")
            continue
        if not resolved.exists():
            errors.append(f"{context}: fixture does not exist: {path}")

    execution = task.get("execution", {})
    if not isinstance(execution, dict):
        errors.append(f"{context}: execution must be an object")
    else:
        workspace_mode = execution.get("workspace_mode")
        if workspace_mode not in ALLOWED_WORKSPACE_MODES:
            errors.append(f"{context}: invalid execution workspace_mode {workspace_mode}")
        if execution.get("network_access") is not False:
            errors.append(f"{context}: agent benchmarks must disable network_access")
        timeout = execution.get("timeout_seconds")
        if not isinstance(timeout, int) or timeout <= 0 or timeout > 3600:
            errors.append(f"{context}: timeout_seconds must be between 1 and 3600")
        allowed_paths = execution.get("allowed_write_paths")
        if not isinstance(allowed_paths, list) or not all(isinstance(item, str) for item in allowed_paths):
            errors.append(f"{context}: allowed_write_paths must be a string list")
        elif workspace_mode == "read-only" and allowed_paths:
            errors.append(f"{context}: read-only tasks cannot declare allowed_write_paths")
        else:
            for path in allowed_paths or []:
                try:
                    resolve_repo_path(path)
                except ValueError as exc:
                    errors.append(f"{context}: {exc}")

    rubric = task.get("rubric", [])
    if not isinstance(rubric, list) or not rubric:
        errors.append(f"{context}: rubric must be a non-empty list")
    else:
        criterion_ids = []
        total_weight = 0.0
        for criterion in rubric:
            if not isinstance(criterion, dict):
                errors.append(f"{context}: rubric criterion must be an object")
                continue
            criterion_id = criterion.get("id")
            weight = criterion.get("weight")
            if not isinstance(criterion_id, str) or not criterion_id:
                errors.append(f"{context}: rubric criterion id must be a non-empty string")
            else:
                criterion_ids.append(criterion_id)
            if not isinstance(weight, (int, float)) or weight <= 0:
                errors.append(f"{context}: rubric weight must be positive")
            else:
                total_weight += float(weight)
        if len(criterion_ids) != len(set(criterion_ids)):
            errors.append(f"{context}: rubric criterion ids must be unique")
        if round(total_weight, 6) != 100.0:
            errors.append(f"{context}: rubric weights must sum to 100, got {total_weight:g}")

    for field in ["expected_artifacts", "expected_outcomes"]:
        if not isinstance(task.get(field), list) or not task.get(field):
            errors.append(f"{context}: {field} must be a non-empty list")

    return errors


def validate_result(result: Dict[str, Any], tasks_by_id: Dict[str, Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    context = rel(result["_path"])

    for field in sorted(RESULT_REQUIRED_FIELDS - set(result)):
        errors.append(f"{context}: missing required field {field}")
    for field in sorted(set(result) - RESULT_REQUIRED_FIELDS - {"_path"}):
        errors.append(f"{context}: unknown field {field}")

    if result.get("$schema") != RESULT_SCHEMA:
        errors.append(f"{context}: expected $schema {RESULT_SCHEMA}")

    run_id = result.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        errors.append(f"{context}: run_id must be a non-empty string")
    elif run_id != result["_path"].stem:
        errors.append(f"{context}: run_id must match filename")

    task = tasks_by_id.get(result.get("task_id"))
    if task is None:
        errors.append(f"{context}: unknown task id {result.get('task_id')}")
        return errors
    if result.get("task_version") != task.get("version"):
        errors.append(f"{context}: task_version does not match task {task['id']}")

    trial = result.get("trial")
    if not isinstance(trial, int) or isinstance(trial, bool) or trial < 1:
        errors.append(f"{context}: trial must be a positive integer")

    condition = result.get("condition")
    if condition not in ALLOWED_CONDITIONS:
        errors.append(f"{context}: unknown condition {condition}")
    elif condition not in task.get("conditions", []):
        errors.append(f"{context}: condition {condition} is not declared for task {task['id']}")

    status = result.get("status")
    if status not in ALLOWED_RESULT_STATUS:
        errors.append(f"{context}: status must be one of {sorted(ALLOWED_RESULT_STATUS)}")
    if status == "scored" and result.get("model") == "configured-default":
        errors.append(f"{context}: scored results require an exact model id")

    started = parse_timestamp(result.get("started_at"), context, "started_at", errors)
    completed = parse_timestamp(result.get("completed_at"), context, "completed_at", errors)
    if started is not None and completed is not None and completed < started:
        errors.append(f"{context}: completed_at cannot precede started_at")

    provenance = result.get("provenance", {})
    if not isinstance(provenance, dict):
        errors.append(f"{context}: provenance must be an object")
        provenance = {}
    required_provenance = {
        "repository_commit",
        "repository_dirty",
        "skill_snapshot",
        "task_sha256",
        "agent_version",
        "harness_version",
        "invocation_mode",
        "model_parameters",
        "network_access",
        "workspace_mode",
    }
    for field in sorted(required_provenance - set(provenance)):
        errors.append(f"{context}: provenance missing field {field}")
    if provenance.get("task_sha256") != sha256_path(task["_path"]):
        errors.append(f"{context}: task_sha256 does not match {rel(task['_path'])}")
    if status == "scored" and provenance.get("repository_dirty") is not False:
        errors.append(f"{context}: scored results require a clean repository snapshot")
    if provenance.get("invocation_mode") not in ALLOWED_INVOCATION_MODES:
        errors.append(f"{context}: invalid invocation_mode {provenance.get('invocation_mode')}")
    if provenance.get("workspace_mode") != task.get("execution", {}).get("workspace_mode"):
        errors.append(f"{context}: workspace_mode does not match task execution contract")
    if provenance.get("network_access") != task.get("execution", {}).get("network_access"):
        errors.append(f"{context}: network_access does not match task execution contract")

    criterion_ids = {criterion["id"] for criterion in task["rubric"]}
    scores = result.get("criteria_scores", [])
    if not isinstance(scores, list):
        errors.append(f"{context}: criteria_scores must be a list")
        scores = []
    seen = set()
    for item in scores:
        criterion_id = item.get("criterion_id") if isinstance(item, dict) else None
        score = item.get("score") if isinstance(item, dict) else None
        if criterion_id not in criterion_ids:
            errors.append(f"{context}: unknown criterion id {criterion_id}")
        elif criterion_id in seen:
            errors.append(f"{context}: duplicate criterion id {criterion_id}")
        else:
            seen.add(criterion_id)
        if not isinstance(score, (int, float)) or score < 0 or score > 1:
            errors.append(f"{context}: score must be between 0 and 1")
    if status == "scored" and seen != criterion_ids:
        errors.append(f"{context}: scored result must include every rubric criterion")
    if status != "scored" and scores:
        errors.append(f"{context}: only scored results may include criteria_scores")

    evaluation = result.get("evaluation")
    if status == "scored":
        if not isinstance(evaluation, dict):
            errors.append(f"{context}: scored result requires evaluation provenance")
        else:
            if evaluation.get("rubric_version") != task.get("version"):
                errors.append(f"{context}: evaluation rubric_version must match task version")
            if evaluation.get("evaluator_type") not in ALLOWED_EVALUATOR_TYPES:
                errors.append(f"{context}: invalid evaluator_type")
            evaluator_ids = evaluation.get("evaluator_ids")
            if not isinstance(evaluator_ids, list) or not evaluator_ids:
                errors.append(f"{context}: evaluation requires evaluator_ids")
            parse_timestamp(evaluation.get("scored_at"), context, "evaluation.scored_at", errors)
    elif evaluation is not None:
        errors.append(f"{context}: unscored result evaluation must be null")

    failure = result.get("failure")
    if status == "failed":
        if not isinstance(failure, dict):
            errors.append(f"{context}: failed result requires failure details")
        elif failure.get("category") not in ALLOWED_FAILURE_CATEGORIES:
            errors.append(f"{context}: invalid failure category")
    elif failure is not None:
        errors.append(f"{context}: non-failed result failure must be null")

    metrics = result.get("metrics", {})
    if not isinstance(metrics, dict):
        errors.append(f"{context}: metrics must be an object")
    else:
        for field in ["wall_time_seconds", "input_tokens", "output_tokens", "cost_usd"]:
            value = metrics.get(field)
            if value is not None and (
                not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0
            ):
                errors.append(f"{context}: metric {field} must be non-negative or null")

    artifacts = result.get("artifacts", [])
    if not isinstance(artifacts, list):
        errors.append(f"{context}: artifacts must be a list")
    else:
        for artifact in artifacts:
            path = artifact.get("path") if isinstance(artifact, dict) else None
            if not isinstance(path, str) or not path:
                errors.append(f"{context}: artifact path must be a non-empty string")
            elif Path(path).is_absolute() or ".." in Path(path).parts:
                errors.append(f"{context}: artifact path must be repository-relative")

    return errors


def result_score(task: Dict[str, Any], result: Dict[str, Any]) -> Optional[float]:
    if result["status"] != "scored":
        return None
    weights = {criterion["id"]: float(criterion["weight"]) for criterion in task["rubric"]}
    scores = {item["criterion_id"]: float(item["score"]) for item in result["criteria_scores"]}
    return round(sum(scores[criterion_id] * weight for criterion_id, weight in weights.items()), 2)


def agent_key(result: Dict[str, Any]) -> Tuple[str, str, str]:
    return (result["agent"], result["harness"], result["model"])


def average(values: Iterable[float]) -> Optional[float]:
    values = list(values)
    if not values:
        return None
    return round(statistics.mean(values), 2)


def ci95(values: Iterable[float]) -> Optional[float]:
    values = list(values)
    if len(values) < 2:
        return None
    return round(1.96 * statistics.stdev(values) / math.sqrt(len(values)), 2)


def percentage(numerator: int, denominator: int) -> Optional[float]:
    if denominator == 0:
        return None
    return round(100.0 * numerator / denominator, 2)


def build_variants(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    groups: Dict[Tuple[str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for result in results:
        groups[(*agent_key(result), result["condition"])].append(result)

    variants = []
    for key in sorted(groups):
        agent, harness, model, condition = key
        runs = groups[key]
        status_counts = Counter(run["status"] for run in runs)
        task_scores: Dict[str, List[float]] = defaultdict(list)
        for run in runs:
            if run["score"] is not None:
                task_scores[run["task_id"]].append(run["score"])
        macro_scores = [statistics.mean(values) for values in task_scores.values()]
        terminal_count = status_counts["scored"] + status_counts["failed"]

        metric_values: Dict[str, List[float]] = defaultdict(list)
        for run in runs:
            metrics = run["metrics"]
            for field in ["wall_time_seconds", "cost_usd"]:
                if metrics.get(field) is not None:
                    metric_values[field].append(float(metrics[field]))
            token_total = sum(
                int(metrics[field])
                for field in ["input_tokens", "output_tokens"]
                if metrics.get(field) is not None
            )
            if any(metrics.get(field) is not None for field in ["input_tokens", "output_tokens"]):
                metric_values["tokens"].append(float(token_total))

        variants.append(
            {
                "agent": agent,
                "harness": harness,
                "model": model,
                "condition": condition,
                "task_count": len({run["task_id"] for run in runs}),
                "run_count": len(runs),
                "scored_count": status_counts["scored"],
                "pending_review_count": status_counts["pending-review"],
                "failed_count": status_counts["failed"],
                "skipped_count": status_counts["skipped"],
                "failure_rate": percentage(status_counts["failed"], terminal_count),
                "score": average(macro_scores),
                "score_ci95": ci95(macro_scores),
                "wall_time_seconds": average(metric_values["wall_time_seconds"]),
                "cost_usd": average(metric_values["cost_usd"]),
                "tokens": average(metric_values["tokens"]),
            }
        )
    return variants


def build_skill_lifts(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    trial_conditions: Dict[Tuple[str, str, str, str, int], Dict[str, float]] = defaultdict(dict)
    for result in results:
        if result["score"] is None:
            continue
        key = (*agent_key(result), result["task_id"], result["trial"])
        trial_conditions[key][result["condition"]] = result["score"]

    grouped: Dict[
        Tuple[str, str, str, str, str, str], List[Tuple[float, float, float]]
    ] = defaultdict(list)
    for key, condition_scores in trial_conditions.items():
        agent, harness, model, task_id, _trial = key
        comparisons = [
            ("docs-only", "baseline"),
            ("skill-enabled", "baseline"),
            ("skill-site-adapter", "skill-enabled"),
        ]
        for condition, reference_condition in comparisons:
            score = condition_scores.get(condition)
            reference = condition_scores.get(reference_condition)
            if score is not None and reference is not None:
                grouped[
                    (agent, harness, model, task_id, condition, reference_condition)
                ].append(
                    (reference, score, score - reference)
                )

    lifts = []
    for key in sorted(grouped):
        agent, harness, model, task_id, condition, reference_condition = key
        pairs = grouped[key]
        lift_values = [pair[2] for pair in pairs]
        lifts.append(
            {
                "agent": agent,
                "harness": harness,
                "model": model,
                "task_id": task_id,
                "condition": condition,
                "reference_condition": reference_condition,
                "pair_count": len(pairs),
                "reference_score": average(pair[0] for pair in pairs),
                "condition_score": average(pair[1] for pair in pairs),
                "lift": average(lift_values),
                "lift_ci95": ci95(lift_values),
            }
        )
    return lifts


def publication_readiness(
    payload: Dict[str, Any], root: Path = ROOT
) -> Dict[str, Any]:
    results = payload.get("results", [])
    scored_results = [result for result in results if result.get("status") == "scored"]
    agents = {
        (result.get("agent"), result.get("harness"), result.get("model"))
        for result in scored_results
    }
    blockers: List[str] = []

    if not scored_results:
        blockers.append("No reviewed scored runs have been imported.")
    if len(agents) < 2:
        blockers.append("Fewer than two scored agent/model variants are available.")
    if payload.get("pending_review_count", 0):
        blockers.append(
            f"{payload['pending_review_count']} run(s) are still pending blinded review."
        )

    root = root.resolve()
    artifact_issue_runs = set()
    review_issue_runs = set()
    for result in scored_results:
        run_id = result["run_id"]
        evaluation = result.get("evaluation") or {}
        evaluator_ids = evaluation.get("evaluator_ids", [])
        if (
            evaluation.get("blinded") is not True
            or not isinstance(evaluator_ids, list)
            or len(evaluator_ids) != 2
            or len(set(evaluator_ids)) != 2
        ):
            review_issue_runs.add(run_id)

        artifacts = result.get("artifacts", [])
        if not artifacts:
            artifact_issue_runs.add(run_id)
            continue
        for artifact in artifacts:
            digest = artifact.get("sha256") if isinstance(artifact, dict) else None
            value = artifact.get("path") if isinstance(artifact, dict) else None
            if not isinstance(value, str) or not isinstance(digest, str):
                artifact_issue_runs.add(run_id)
                continue
            path = (root / value).resolve()
            try:
                path.relative_to(root)
            except ValueError:
                artifact_issue_runs.add(run_id)
                continue
            if not path.is_file() or sha256_path(path) != digest:
                artifact_issue_runs.add(run_id)

    if review_issue_runs:
        blockers.append(
            f"{len(review_issue_runs)} scored run(s) lack exactly two independent blinded reviewers."
        )
    if artifact_issue_runs:
        blockers.append(
            f"{len(artifact_issue_runs)} scored run(s) lack complete digest-verified public artifacts."
        )

    lifts = payload.get("skill_lifts", [])
    eligible_lifts = [
        lift for lift in lifts if lift.get("pair_count", 0) >= PUBLICATION_MIN_PAIRS
    ]
    if not lifts:
        blockers.append("No paired condition comparison is available.")
    elif len(eligible_lifts) != len(lifts):
        blockers.append(
            f"{len(lifts) - len(eligible_lifts)} paired comparison(s) have fewer than "
            f"{PUBLICATION_MIN_PAIRS} trials."
        )

    eligible_skill_variants = {
        (lift.get("agent"), lift.get("harness"), lift.get("model"))
        for lift in eligible_lifts
        if lift.get("condition") == "skill-enabled"
        and lift.get("reference_condition") == "baseline"
    }
    missing_skill_variants = agents - eligible_skill_variants
    if missing_skill_variants:
        blockers.append(
            f"{len(missing_skill_variants)} scored agent/model variant(s) lack a "
            f"{PUBLICATION_MIN_PAIRS}-pair baseline-to-skill comparison."
        )

    return {
        "leaderboard_ready": not blockers,
        "minimum_pairs": PUBLICATION_MIN_PAIRS,
        "scored_agent_variant_count": len(agents),
        "eligible_comparison_count": len(eligible_lifts),
        "blockers": blockers,
    }


def benchmark_payload(task_dir: Path = TASK_DIR, result_dir: Path = RESULT_DIR) -> Dict[str, Any]:
    index = load_json(INDEX_JSON)
    known_skills = {skill["id"] for skill in index["skills"]}
    tasks = load_tasks(task_dir)
    results = load_results(result_dir)
    validation_errors = []
    for task in tasks:
        validation_errors.extend(validate_task(task, known_skills))

    tasks_by_id = {task["id"]: task for task in tasks if isinstance(task.get("id"), str)}
    run_ids = Counter(result.get("run_id") for result in results)
    for run_id, count in sorted(run_ids.items(), key=lambda item: str(item[0])):
        if run_id is not None and count > 1:
            validation_errors.append(f"duplicate run_id {run_id}")
    trial_keys = Counter(
        (
            result.get("agent"),
            result.get("harness"),
            result.get("model"),
            result.get("task_id"),
            result.get("condition"),
            result.get("trial"),
        )
        for result in results
    )
    for key, count in sorted(trial_keys.items(), key=lambda item: str(item[0])):
        if count > 1:
            validation_errors.append(f"duplicate agent/task/condition/trial result {key}")
    for result in results:
        validation_errors.extend(validate_result(result, tasks_by_id))

    if validation_errors:
        return {
            "ok": False,
            "validation_errors": validation_errors,
            "task_count": len(tasks),
            "result_count": len(results),
            "tasks": [],
            "results": [],
            "variants": [],
            "skill_lifts": [],
        }

    enriched_results = []
    for result in results:
        task = tasks_by_id[result["task_id"]]
        enriched = dict(result)
        enriched.pop("_path", None)
        enriched["result_path"] = rel(result["_path"])
        enriched["score"] = result_score(task, result)
        enriched_results.append(enriched)

    task_counts = Counter(task["task_type"] for task in tasks)
    condition_counts = Counter(condition for task in tasks for condition in task["conditions"])
    status_counts = Counter(result["status"] for result in enriched_results)
    task_summaries = [
        {
            "id": task["id"],
            "name": task["name"],
            "version": task["version"],
            "task_type": task["task_type"],
            "risk_level": task["risk_level"],
            "skill_ids": task["skill_ids"],
            "conditions": task["conditions"],
            "workspace_mode": task["execution"]["workspace_mode"],
            "timeout_seconds": task["execution"]["timeout_seconds"],
            "rubric_weight": sum(float(criterion["weight"]) for criterion in task["rubric"]),
            "task_path": rel(task["_path"]),
        }
        for task in sorted(tasks, key=lambda item: item["id"])
    ]

    payload = {
        "ok": True,
        "validation_errors": [],
        "task_count": len(tasks),
        "result_count": len(enriched_results),
        "scored_result_count": status_counts["scored"],
        "pending_review_count": status_counts["pending-review"],
        "failed_result_count": status_counts["failed"],
        "task_type_counts": dict(sorted(task_counts.items())),
        "condition_counts": dict(sorted(condition_counts.items())),
        "result_status_counts": dict(sorted(status_counts.items())),
        "tasks": task_summaries,
        "results": enriched_results,
        "variants": build_variants(enriched_results),
        "skill_lifts": build_skill_lifts(enriched_results),
    }
    payload["publication"] = publication_readiness(payload)
    return payload


def format_optional(value: Optional[float], signed: bool = False) -> str:
    if value is None:
        return ""
    return f"{value:+.2f}" if signed else f"{value:.2f}"


def markdown_report(payload: Dict[str, Any]) -> str:
    lines = [
        "# Agent Benchmark Report",
        "",
        "This report is generated by `tools/run_agent_benchmarks.py`. Do not edit it by hand.",
        "",
        "The evidence-pilot importer validates reviewed result files and reports macro-averaged",
        "scores, repeated-trial confidence intervals, failure rates, cost, time, and paired lift.",
        "External agents are launched only by the opt-in execution harness, never by CI.",
        "",
        "## Summary",
        "",
        "| Signal | Count |",
        "| --- | ---: |",
        f"| Tasks | {payload['task_count']} |",
        f"| Results | {payload['result_count']} |",
        f"| Scored results | {payload.get('scored_result_count', 0)} |",
        f"| Pending review | {payload.get('pending_review_count', 0)} |",
        f"| Failed results | {payload.get('failed_result_count', 0)} |",
    ]
    for task_type, count in payload.get("task_type_counts", {}).items():
        lines.append(f"| Task type `{task_type}` | {count} |")
    for condition, count in payload.get("condition_counts", {}).items():
        lines.append(f"| Condition `{condition}` | {count} |")

    publication = payload.get("publication", {})
    lines.extend(
        [
            "",
            "## Publication Readiness",
            "",
            "Ready for comparative publication: "
            f"**{'yes' if publication.get('leaderboard_ready') else 'no'}**.",
            "",
        ]
    )
    blockers = publication.get("blockers", [])
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append(
            f"All comparisons have at least {publication.get('minimum_pairs')} paired trials, "
            "two independent blinded reviewers per scored run, and digest-verified artifacts."
        )

    lines.extend(
        [
            "",
            "## Tasks",
            "",
            "| Task | Type | Skills | Conditions | Workspace | Timeout |",
            "| --- | --- | --- | --- | --- | ---: |",
        ]
    )
    for task in payload.get("tasks", []):
        skills = ", ".join(f"`{skill_id}`" for skill_id in task["skill_ids"])
        conditions = ", ".join(f"`{condition}`" for condition in task["conditions"])
        lines.append(
            f"| [`{task['id']}`](../{task['task_path']}) | `{task['task_type']}` | "
            f"{skills} | {conditions} | `{task['workspace_mode']}` | {task['timeout_seconds']}s |"
        )

    lines.extend(["", "## Agent Results", ""])
    if payload.get("variants"):
        lines.extend(
            [
                "| Agent | Harness | Model | Condition | Tasks | Runs | Scored | Failed | Failure % | Score | CI95 | Time | Cost | Tokens |",
                "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in payload["variants"]:
            lines.append(
                f"| `{item['agent']}` | `{item['harness']}` | `{item['model']}` | "
                f"`{item['condition']}` | {item['task_count']} | {item['run_count']} | "
                f"{item['scored_count']} | {item['failed_count']} | "
                f"{format_optional(item['failure_rate'])} | {format_optional(item['score'])} | "
                f"{format_optional(item['score_ci95'])} | "
                f"{format_optional(item['wall_time_seconds'])} | "
                f"{format_optional(item['cost_usd'])} | {format_optional(item['tokens'])} |"
            )
    else:
        lines.append("No public-safe reviewed agent runs have been imported yet.")

    lines.extend(["", "## Skill Lift", ""])
    if payload.get("skill_lifts"):
        lines.extend(
            [
                "| Agent | Harness | Model | Task | Reference | Condition | Pairs | Reference score | Condition score | Lift | CI95 |",
                "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in payload["skill_lifts"]:
            lines.append(
                f"| `{item['agent']}` | `{item['harness']}` | `{item['model']}` | "
                f"`{item['task_id']}` | `{item['reference_condition']}` | "
                f"`{item['condition']}` | {item['pair_count']} | "
                f"{format_optional(item['reference_score'])} | "
                f"{format_optional(item['condition_score'])} | "
                f"{format_optional(item['lift'], signed=True)} | "
                f"{format_optional(item['lift_ci95'])} |"
            )
    else:
        lines.append("Skill lift will appear after matching baseline and enabled trial numbers are scored.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Scores are macro-averaged by task so extra trials cannot overweight one task. Failure",
            "rates include terminal scored and failed runs; pending-review and skipped runs remain",
            "visible but do not change the denominator. CI95 is blank until at least two values exist.",
        ]
    )
    return "\n".join(lines)


def dashboard_report(payload: Dict[str, Any]) -> str:
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    def display(value: Optional[float], prefix: str = "", suffix: str = "") -> str:
        if value is None:
            return "Pending"
        return f"{prefix}{value:.2f}{suffix}"

    publication = payload.get("publication", {})
    ready = bool(publication.get("leaderboard_ready"))
    blockers = publication.get("blockers", [])
    blocker_items = "".join(f"<li>{esc(blocker)}</li>" for blocker in blockers)
    if not blocker_items:
        blocker_items = (
            "<li>Repeated paired trials, blinded reviews, and public artifact digests "
            "satisfy the publication contract.</li>"
        )

    variant_rows = []
    for item in payload.get("variants", []):
        score = item.get("score")
        score_width = max(0.0, min(100.0, float(score or 0.0)))
        variant_rows.append(
            "<tr>"
            f"<td><strong>{esc(item['agent'])}</strong><span class=\"sub\">{esc(item['harness'])}</span></td>"
            f"<td><code>{esc(item['model'])}</code></td>"
            f"<td><span class=\"condition\">{esc(item['condition'])}</span></td>"
            f"<td>{item['run_count']}</td>"
            f"<td>{item['scored_count']}</td>"
            f"<td>{item['failed_count']}</td>"
            "<td><div class=\"score-cell\">"
            f"<span>{display(score)}</span><div class=\"meter\"><i style=\"width:{score_width:.2f}%\"></i></div>"
            "</div></td>"
            f"<td>{display(item.get('failure_rate'), suffix='%')}</td>"
            f"<td>{display(item.get('wall_time_seconds'), suffix='s')}</td>"
            f"<td>{display(item.get('cost_usd'), prefix='$')}</td>"
            "</tr>"
        )
    if not variant_rows:
        variant_rows.append(
            '<tr><td colspan="10" class="empty">No reviewed runs published.</td></tr>'
        )

    lift_rows = []
    for item in payload.get("skill_lifts", []):
        lift = item.get("lift")
        lift_class = "positive" if lift is not None and lift >= 0 else "negative"
        lift_rows.append(
            "<tr>"
            f"<td><strong>{esc(item['agent'])}</strong><span class=\"sub\">{esc(item['model'])}</span></td>"
            f"<td><code>{esc(item['task_id'])}</code></td>"
            f"<td>{esc(item['reference_condition'])}</td>"
            f"<td>{esc(item['condition'])}</td>"
            f"<td>{item['pair_count']}</td>"
            f"<td>{display(item.get('reference_score'))}</td>"
            f"<td>{display(item.get('condition_score'))}</td>"
            f"<td class=\"{lift_class}\">{display(lift, prefix='+' if lift is not None and lift >= 0 else '')}</td>"
            f"<td>{display(item.get('lift_ci95'), prefix='±')}</td>"
            "</tr>"
        )
    if not lift_rows:
        lift_rows.append(
            '<tr><td colspan="9" class="empty">No three-trial paired comparison is available.</td></tr>'
        )

    result_rows = []
    for item in payload.get("results", []):
        result_rows.append(
            "<tr>"
            f"<td><a href=\"../{esc(item['result_path'])}\"><code>{esc(item['run_id'])}</code></a></td>"
            f"<td>{esc(item['agent'])}<span class=\"sub\">{esc(item['model'])}</span></td>"
            f"<td>{esc(item['task_id'])}</td>"
            f"<td>{esc(item['condition'])}</td>"
            f"<td>{item['trial']}</td>"
            f"<td><span class=\"status status-{esc(item['status'])}\">{esc(item['status'])}</span></td>"
            f"<td>{display(item.get('score'))}</td>"
            f"<td>{display(item.get('metrics', {}).get('wall_time_seconds'), suffix='s')}</td>"
            f"<td>{display(item.get('metrics', {}).get('cost_usd'), prefix='$')}</td>"
            "</tr>"
        )
    if not result_rows:
        result_rows.append(
            '<tr><td colspan="9" class="empty">The public result ledger is empty.</td></tr>'
        )

    status_label = "Publication ready" if ready else "Evidence not ready"
    status_class = "ready" if ready else "blocked"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>HPC Skill Hub Agent Evidence</title>
  <style>
    :root {{
      --bg: #f5f7fa;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #667085;
      --line: #d8dee8;
      --teal: #0f766e;
      --blue: #2563eb;
      --green: #157347;
      --amber: #a16207;
      --red: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.45; }}
    a {{ color: #1d4ed8; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{ font-size: .88em; overflow-wrap: anywhere; }}
    header {{ background: var(--panel); border-bottom: 1px solid var(--line); }}
    .wrap {{ width: min(1240px, calc(100vw - 32px)); margin: 0 auto; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 20px; padding: 20px 0; }}
    h1 {{ margin: 0; font-size: 1.45rem; letter-spacing: 0; }}
    h2 {{ margin: 0; font-size: 1.05rem; letter-spacing: 0; }}
    .subtitle {{ margin: 3px 0 0; color: var(--muted); }}
    nav {{ display: flex; gap: 14px; flex-wrap: wrap; font-size: .92rem; }}
    main {{ padding: 24px 0 44px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .metric {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px; }}
    .metric strong {{ display: block; font-size: 1.55rem; }}
    .metric span {{ color: var(--muted); font-size: .86rem; }}
    .publication {{ border: 1px solid var(--line); border-left: 5px solid var(--amber); background: var(--panel); padding: 16px 18px; margin-bottom: 22px; }}
    .publication.ready {{ border-left-color: var(--green); }}
    .publication h2 {{ color: var(--amber); }}
    .publication.ready h2 {{ color: var(--green); }}
    .publication ul {{ margin: 8px 0 0; padding-left: 20px; color: var(--muted); }}
    section {{ margin-top: 24px; }}
    .section-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: baseline; margin-bottom: 9px; }}
    .section-head span {{ color: var(--muted); font-size: .86rem; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); background: var(--panel); }}
    table {{ width: 100%; border-collapse: collapse; min-width: 820px; font-size: .88rem; }}
    th, td {{ text-align: left; border-bottom: 1px solid var(--line); padding: 10px 11px; vertical-align: top; }}
    th {{ background: #eef2f7; color: #344054; font-weight: 650; white-space: nowrap; }}
    tr:last-child td {{ border-bottom: 0; }}
    .sub {{ display: block; color: var(--muted); font-size: .78rem; margin-top: 2px; }}
    .condition {{ border: 1px solid #b7c6db; border-radius: 6px; padding: 2px 6px; white-space: nowrap; }}
    .score-cell {{ min-width: 126px; }}
    .meter {{ width: 100%; height: 5px; background: #e5eaf1; margin-top: 5px; }}
    .meter i {{ display: block; height: 100%; background: var(--teal); }}
    .positive {{ color: var(--green); font-weight: 650; }}
    .negative {{ color: var(--red); font-weight: 650; }}
    .status {{ display: inline-block; border: 1px solid var(--line); border-radius: 6px; padding: 2px 6px; white-space: nowrap; }}
    .status-scored {{ color: var(--green); border-color: #86b79d; }}
    .status-failed {{ color: var(--red); border-color: #e3a29c; }}
    .status-pending-review {{ color: var(--amber); border-color: #ddc28a; }}
    .empty {{ color: var(--muted); text-align: center; padding: 28px; }}
    .method {{ color: var(--muted); max-width: 86ch; font-size: .9rem; }}
    footer {{ background: var(--panel); border-top: 1px solid var(--line); color: var(--muted); padding: 18px 0; font-size: .86rem; }}
    @media (max-width: 760px) {{
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .section-head {{ align-items: flex-start; flex-direction: column; }}
      h1 {{ font-size: 1.25rem; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <div>
        <h1>Agent Evidence Dashboard</h1>
        <p class="subtitle">Reviewed HPC task outcomes across baseline, documentation, and skill-enabled conditions.</p>
      </div>
      <nav aria-label="Evidence links">
        <a href="../index.html">Registry</a>
        <a href="AGENT_BENCHMARKS.md">Method</a>
        <a href="AGENT_BENCHMARK_REPORT.md">Report</a>
        <a href="V0_4_COMPLETION.md">v0.4 gates</a>
      </nav>
    </div>
  </header>
  <main class="wrap">
    <div class="metrics" aria-label="Evidence summary">
      <div class="metric"><strong>{payload.get('scored_result_count', 0)}</strong><span>Reviewed runs</span></div>
      <div class="metric"><strong>{publication.get('scored_agent_variant_count', 0)}</strong><span>Agent/model variants</span></div>
      <div class="metric"><strong>{payload.get('task_count', 0)}</strong><span>Public tasks</span></div>
      <div class="metric"><strong>{publication.get('eligible_comparison_count', 0)}</strong><span>Three-trial comparisons</span></div>
    </div>
    <div class="publication {status_class}">
      <h2>{status_label}</h2>
      <ul>{blocker_items}</ul>
    </div>
    <section aria-labelledby="conditions-heading">
      <div class="section-head"><h2 id="conditions-heading">Condition Results</h2><span>Macro score, failures, time, and reported cost</span></div>
      <div class="table-wrap"><table>
        <thead><tr><th>Agent</th><th>Model</th><th>Condition</th><th>Runs</th><th>Scored</th><th>Failed</th><th>Score</th><th>Failure</th><th>Time</th><th>Cost</th></tr></thead>
        <tbody>{''.join(variant_rows)}</tbody>
      </table></div>
    </section>
    <section aria-labelledby="lift-heading">
      <div class="section-head"><h2 id="lift-heading">Paired Skill Lift</h2><span>Same task and trial, compared by condition</span></div>
      <div class="table-wrap"><table>
        <thead><tr><th>Agent</th><th>Task</th><th>Reference</th><th>Condition</th><th>Pairs</th><th>Reference score</th><th>Condition score</th><th>Lift</th><th>CI95</th></tr></thead>
        <tbody>{''.join(lift_rows)}</tbody>
      </table></div>
    </section>
    <section aria-labelledby="ledger-heading">
      <div class="section-head"><h2 id="ledger-heading">Public Run Ledger</h2><span>Failures and pending reviews remain visible</span></div>
      <div class="table-wrap"><table>
        <thead><tr><th>Run</th><th>Agent</th><th>Task</th><th>Condition</th><th>Trial</th><th>Status</th><th>Score</th><th>Time</th><th>Cost</th></tr></thead>
        <tbody>{''.join(result_rows)}</tbody>
      </table></div>
    </section>
    <section aria-labelledby="method-heading">
      <div class="section-head"><h2 id="method-heading">Evidence Boundary</h2></div>
      <p class="method">Comparative publication requires at least {PUBLICATION_MIN_PAIRS} paired trials, two independent blinded reviewers for every scored run, exact agent and model versions, a clean repository commit, and digest-verified public artifacts. Scores are not maturity promotions and incomplete evidence does not produce a ranking.</p>
    </section>
  </main>
  <footer><div class="wrap">Generated by <code>tools/run_agent_benchmarks.py</code> from reviewed public results.</div></footer>
</body>
</html>
"""


def check_report(report_path: Path, expected: str) -> List[str]:
    if not report_path.exists():
        return [f"{rel(report_path)} is missing"]
    if report_path.read_text(encoding="utf-8") != expected:
        return [f"{rel(report_path)} is stale; run tools/run_agent_benchmarks.py"]
    return []


def emit_failures(payload: Dict[str, Any]) -> None:
    for error in payload.get("validation_errors", []):
        print(f"ERROR: {error}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and report HPC Skill Hub agent benchmark results"
    )
    parser.add_argument("--check", action="store_true", help="Fail if report is stale")
    parser.add_argument("--json", action="store_true", help="Emit JSON results")
    parser.add_argument("--tasks-dir", default=str(TASK_DIR), help="Task directory")
    parser.add_argument("--results-dir", default=str(RESULT_DIR), help="Result directory")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Report path")
    parser.add_argument(
        "--dashboard", default=str(DEFAULT_DASHBOARD), help="Dashboard HTML path"
    )
    args = parser.parse_args()

    payload = benchmark_payload(Path(args.tasks_dir), Path(args.results_dir))
    expected_report = markdown_report(payload) + "\n"
    expected_dashboard = dashboard_report(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.check:
        errors = check_report(Path(args.report), expected_report)
        errors.extend(check_report(Path(args.dashboard), expected_dashboard))
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(
            f"Agent benchmark report is current in {rel(Path(args.report))}; "
            f"dashboard is current in {rel(Path(args.dashboard))}."
        )
    else:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(expected_report, encoding="utf-8")
        dashboard_path = Path(args.dashboard)
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        dashboard_path.write_text(expected_dashboard, encoding="utf-8")
        print(f"Wrote {rel(report_path)} and {rel(dashboard_path)}.")

    if not payload["ok"]:
        emit_failures(payload)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
