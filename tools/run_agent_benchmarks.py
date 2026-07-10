#!/usr/bin/env python3
"""Validate and report reviewed agent benchmark tasks and results."""

from __future__ import annotations

import argparse
import hashlib
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

    return {
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
    args = parser.parse_args()

    payload = benchmark_payload(Path(args.tasks_dir), Path(args.results_dir))
    expected_report = markdown_report(payload) + "\n"

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.check:
        errors = check_report(Path(args.report), expected_report)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Agent benchmark report is current in {rel(Path(args.report))}.")
    else:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(expected_report, encoding="utf-8")
        print(f"Wrote {rel(report_path)}.")

    if not payload["ok"]:
        emit_failures(payload)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
