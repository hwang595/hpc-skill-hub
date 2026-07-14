#!/usr/bin/env python3
"""Lock, schedule, and audit a real agent benchmark evidence campaign."""

from __future__ import annotations

import argparse
import json
import random
import re
import shlex
import subprocess
import sys
from collections import Counter, defaultdict
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


CAMPAIGN_SCHEMA = (
    "https://hpc-skill-hub.org/schemas/agent-benchmark-campaign.schema.json"
)
SCHEMA_VERSION = "0.2.0"
LEGACY_SCHEMA_VERSION = "0.1.0"
CAMPAIGN_REQUIRED_FIELDS = {
    "$schema",
    "schema_version",
    "campaign_id",
    "created_at",
    "plan",
    "repository",
    "task_sha256",
    "conditions",
    "mcp_contract",
    "variants",
    "budget",
    "schedule",
}
PRIVATE_PATH_MARKERS = {
    "blind-salt",
    "mapping",
    "raw-output",
    "reconciliation",
    "reviewer-a",
    "reviewer-b",
    "stderr",
    "transcript",
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


def path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def repo_path(value: Any, context: str) -> Optional[Path]:
    if not isinstance(value, str) or not value:
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (ROOT / candidate).resolve()
    if not path_is_within(resolved, ROOT):
        return None
    return resolved


def parse_timestamp(value: Any, context: str, errors: List[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{context} must be a non-empty timestamp")
        return
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{context} must be an ISO-8601 timestamp")
        return
    if parsed.tzinfo is None:
        errors.append(f"{context} must include a timezone")


def budget_mode(harness_id: str) -> str:
    if harness_id == "claude-code":
        return "provider-cli-hard-limit"
    return "external-monitoring-required"


def build_schedule(payload: Dict[str, Any], seed: int) -> Dict[str, Any]:
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("schedule seed must be a non-negative integer")
    grouped: Dict[Tuple[str, int], List[Dict[str, Any]]] = defaultdict(list)
    for run in payload["runs"]:
        grouped[(run["task_id"], run["trial"])].append(run)

    generator = random.Random(seed)
    wave_keys = sorted(grouped)
    generator.shuffle(wave_keys)
    waves = []
    for index, (task_id, trial) in enumerate(wave_keys, start=1):
        runs = sorted(grouped[(task_id, trial)], key=lambda item: item["run_id"])
        generator.shuffle(runs)
        waves.append(
            {
                "id": f"wave-{index:02d}",
                "task_id": task_id,
                "trial": trial,
                "run_ids": [run["run_id"] for run in runs],
            }
        )
    return {
        "seed": seed,
        "wave_count": len(waves),
        "run_count": payload["run_count"],
        "waves": waves,
    }


def build_manifest(
    payload: Dict[str, Any],
    plan_path: Path,
    preflight: Dict[str, Any],
    seed: int,
    created_at: Optional[str] = None,
) -> Dict[str, Any]:
    if not payload.get("ok"):
        raise ValueError("campaign plan is invalid")
    if not preflight.get("ok"):
        raise ValueError("campaign preflight is blocked: " + "; ".join(preflight["blockers"]))

    execution = payload["plan"]["execution"]
    per_run_budget = execution.get("max_budget_usd_per_run")
    total_budget = execution.get("max_total_budget_usd")
    if not isinstance(per_run_budget, (int, float)) or isinstance(per_run_budget, bool):
        raise ValueError("real evidence campaign requires a numeric per-run budget")
    if not isinstance(total_budget, (int, float)) or isinstance(total_budget, bool):
        raise ValueError("real evidence campaign requires a numeric total budget")
    if execution.get("require_paid_run_acknowledgement") is not True:
        raise ValueError("real evidence campaign requires paid-run acknowledgement")

    preflight_variants = {item["id"]: item for item in preflight["variants"]}
    variants = []
    for variant in payload["plan"]["variants"]:
        locked = preflight_variants.get(variant["id"])
        if locked is None or not locked.get("ready"):
            raise ValueError(f"variant {variant['id']} is not ready")
        variants.append(
            {
                "id": variant["id"],
                "agent": variant["agent"],
                "harness": variant["harness"],
                "model": locked["model"],
                "agent_version": locked["agent_version"],
                "budget_enforcement": locked["budget_enforcement"],
            }
        )

    tasks = harness.load_tasks()
    commit = preflight["repository_commit"]
    mcp_contract = None
    if harness.MCP_CONDITION in payload["plan"]["conditions"]:
        mcp = preflight.get("mcp")
        if not isinstance(mcp, dict) or not mcp.get("ready"):
            raise ValueError("mcp-enabled campaign requires a passing MCP preflight")
        if mcp.get("mcp_package_version") != payload["plan"]["version"]:
            raise ValueError("MCP package version must match the campaign plan version")
        mcp_contract = {
            key: mcp[key]
            for key in [
                "mcp_server_id",
                "mcp_contract_path",
                "mcp_contract_sha256",
                "mcp_read_only",
                "mcp_package_version",
            ]
        }
    manifest = {
        "$schema": CAMPAIGN_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "campaign_id": f"{payload['plan']['id']}-{commit[:12]}-s{seed}",
        "created_at": created_at or harness.utc_now(),
        "plan": {
            "id": payload["plan"]["id"],
            "version": payload["plan"]["version"],
            "path": harness.rel(plan_path),
            "sha256": harness.sha256_path(plan_path),
        },
        "repository": {"commit": commit, "dirty": False},
        "task_sha256": {
            task_id: harness.sha256_path(tasks[task_id]["_path"])
            for task_id in payload["plan"]["task_ids"]
        },
        "conditions": payload["plan"]["conditions"],
        "mcp_contract": mcp_contract,
        "variants": variants,
        "budget": {
            "max_usd_per_run": float(per_run_budget),
            "max_total_usd": float(total_budget),
            "paid_quota_acknowledged": True,
        },
        "schedule": build_schedule(payload, seed),
    }
    errors, _ = validate_campaign(manifest)
    if errors:
        raise ValueError("generated campaign lock is invalid: " + "; ".join(errors))
    return manifest


def validate_campaign(
    manifest: Dict[str, Any],
) -> Tuple[List[str], Optional[Dict[str, Any]]]:
    errors: List[str] = []
    schema_version = manifest.get("schema_version")
    required_fields = set(CAMPAIGN_REQUIRED_FIELDS)
    if schema_version == LEGACY_SCHEMA_VERSION:
        required_fields.remove("mcp_contract")
    for field in sorted(required_fields - set(manifest)):
        errors.append(f"campaign missing field {field}")
    for field in sorted(set(manifest) - required_fields):
        errors.append(f"campaign has unknown field {field}")
    if manifest.get("$schema") != CAMPAIGN_SCHEMA:
        errors.append(f"campaign expected $schema {CAMPAIGN_SCHEMA}")
    if schema_version not in {LEGACY_SCHEMA_VERSION, SCHEMA_VERSION}:
        errors.append(
            "campaign expected schema_version "
            f"{LEGACY_SCHEMA_VERSION} or {SCHEMA_VERSION}"
        )
    if not isinstance(manifest.get("campaign_id"), str) or not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest.get("campaign_id", "")
    ):
        errors.append("campaign id must use lowercase kebab-case")
    parse_timestamp(manifest.get("created_at"), "campaign created_at", errors)

    plan = manifest.get("plan")
    if not isinstance(plan, dict):
        errors.append("campaign plan must be an object")
        return errors, None
    plan_path = repo_path(plan.get("path"), "campaign plan path")
    if plan_path is None or not plan_path.is_file():
        errors.append("campaign plan path must name an existing repository file")
        return errors, None
    if plan.get("sha256") != harness.sha256_path(plan_path):
        errors.append("campaign plan digest does not match the repository plan")
    payload = harness.plan_payload(plan_path)
    if not payload.get("ok"):
        errors.append("campaign plan no longer validates")
        return errors, payload
    if plan.get("id") != payload["plan"]["id"]:
        errors.append("campaign plan id does not match the repository plan")
    if plan.get("version") != payload["plan"]["version"]:
        errors.append("campaign plan version does not match the repository plan")

    repository = manifest.get("repository")
    if not isinstance(repository, dict):
        errors.append("campaign repository must be an object")
    else:
        commit = repository.get("commit")
        if not isinstance(commit, str) or len(commit) != 40 or any(
            character not in "0123456789abcdef" for character in commit
        ):
            errors.append("campaign repository commit must be a full lowercase SHA")
        if repository.get("dirty") is not False:
            errors.append("campaign repository must record a clean commit")

    if manifest.get("conditions") != payload["plan"]["conditions"]:
        errors.append("campaign conditions do not match the repository plan")

    mcp_contract = manifest.get("mcp_contract")
    if harness.MCP_CONDITION in payload["plan"]["conditions"]:
        if schema_version != SCHEMA_VERSION:
            errors.append("mcp-enabled campaign requires schema_version 0.2.0")
        if not isinstance(mcp_contract, dict):
            errors.append("mcp-enabled campaign requires an MCP contract lock")
        else:
            expected_mcp = harness.mcp_condition_context()
            expected_fields = set(expected_mcp) | {"mcp_package_version"}
            if set(mcp_contract) != expected_fields:
                errors.append("campaign MCP contract fields do not match the lock schema")
            for field, expected in expected_mcp.items():
                if mcp_contract.get(field) != expected:
                    errors.append(f"campaign MCP contract changed for {field}")
            if not isinstance(mcp_contract.get("mcp_package_version"), str) or not mcp_contract.get(
                "mcp_package_version"
            ):
                errors.append("campaign MCP contract requires a package version")
    elif mcp_contract is not None:
        errors.append("campaign without mcp-enabled must not lock an MCP contract")

    tasks = harness.load_tasks()
    task_digests = manifest.get("task_sha256")
    if not isinstance(task_digests, dict):
        errors.append("campaign task_sha256 must be an object")
    else:
        if set(task_digests) != set(payload["plan"]["task_ids"]):
            errors.append("campaign task digests do not match the plan task set")
        for task_id in payload["plan"]["task_ids"]:
            if task_digests.get(task_id) != harness.sha256_path(tasks[task_id]["_path"]):
                errors.append(f"campaign task digest changed for {task_id}")

    expected_variants = {
        variant["id"]: variant for variant in payload["plan"]["variants"]
    }
    variants = manifest.get("variants")
    if not isinstance(variants, list):
        errors.append("campaign variants must be a list")
        variants = []
    variant_ids = [item.get("id") for item in variants if isinstance(item, dict)]
    if len(variant_ids) != len(set(variant_ids)):
        errors.append("campaign variant ids must be unique")
    if set(variant_ids) != set(expected_variants):
        errors.append("campaign variants do not match the plan variants")
    for item in variants:
        if not isinstance(item, dict) or item.get("id") not in expected_variants:
            continue
        expected = expected_variants[item["id"]]
        if item.get("agent") != expected["agent"] or item.get("harness") != expected["harness"]:
            errors.append(f"campaign variant identity changed for {item['id']}")
        if not item.get("model") or item.get("model") == "configured-default":
            errors.append(f"campaign variant {item['id']} requires an exact model")
        if not isinstance(item.get("agent_version"), str) or not item["agent_version"]:
            errors.append(f"campaign variant {item['id']} requires an agent version")
        if item.get("budget_enforcement") != budget_mode(expected["harness"]):
            errors.append(f"campaign variant {item['id']} has invalid budget enforcement")

    execution = payload["plan"]["execution"]
    budget = manifest.get("budget")
    if not isinstance(budget, dict):
        errors.append("campaign budget must be an object")
    else:
        plan_per_run = execution.get("max_budget_usd_per_run")
        plan_total = execution.get("max_total_budget_usd")
        if not isinstance(plan_per_run, (int, float)) or isinstance(plan_per_run, bool):
            errors.append("campaign plan must define a numeric per-run budget")
        elif budget.get("max_usd_per_run") != float(plan_per_run):
            errors.append("campaign per-run budget does not match the plan")
        if not isinstance(plan_total, (int, float)) or isinstance(plan_total, bool):
            errors.append("campaign plan must define a numeric total budget")
        elif budget.get("max_total_usd") != float(plan_total):
            errors.append("campaign total budget does not match the plan")
        if budget.get("paid_quota_acknowledged") is not True:
            errors.append("campaign must record paid quota acknowledgement")

    schedule = manifest.get("schedule")
    if not isinstance(schedule, dict):
        errors.append("campaign schedule must be an object")
        return errors, payload
    waves = schedule.get("waves")
    if not isinstance(waves, list):
        errors.append("campaign schedule waves must be a list")
        return errors, payload
    if schedule.get("wave_count") != len(waves):
        errors.append("campaign schedule wave_count is incorrect")
    if schedule.get("run_count") != payload["run_count"]:
        errors.append("campaign schedule run_count is incorrect")
    if (
        not isinstance(schedule.get("seed"), int)
        or isinstance(schedule.get("seed"), bool)
        or schedule.get("seed") < 0
    ):
        errors.append("campaign schedule seed must be a non-negative integer")

    expected_runs = {run["run_id"]: run for run in payload["runs"]}
    scheduled_ids: List[str] = []
    wave_ids = []
    for wave in waves:
        if not isinstance(wave, dict):
            errors.append("campaign schedule wave must be an object")
            continue
        wave_ids.append(wave.get("id"))
        run_ids = wave.get("run_ids")
        if not isinstance(run_ids, list):
            errors.append(f"campaign {wave.get('id')} run_ids must be a list")
            continue
        scheduled_ids.extend(run_ids)
        expected_wave = {
            run_id
            for run_id, run in expected_runs.items()
            if run["task_id"] == wave.get("task_id") and run["trial"] == wave.get("trial")
        }
        if set(run_ids) != expected_wave:
            errors.append(f"campaign {wave.get('id')} is not a complete task/trial wave")
    if len(wave_ids) != len(set(wave_ids)):
        errors.append("campaign schedule wave ids must be unique")
    if len(scheduled_ids) != len(set(scheduled_ids)):
        errors.append("campaign schedule contains duplicate run ids")
    if set(scheduled_ids) != set(expected_runs):
        errors.append("campaign schedule does not cover the exact plan run set")
    return errors, payload


def prepare_campaign(
    plan_path: Path,
    model_overrides: Dict[str, str],
    seed: int,
    output_path: Path,
    acknowledge_paid_quota: bool,
    force: bool = False,
) -> Dict[str, Any]:
    if not acknowledge_paid_quota:
        raise ValueError("prepare requires --acknowledge-paid-quota")
    if path_is_within(output_path, ROOT):
        raise ValueError("campaign lock must be stored outside the repository")
    if output_path.exists() and not force:
        raise ValueError(f"campaign lock already exists: {output_path}")
    payload = harness.plan_payload(plan_path)
    if not payload.get("ok"):
        raise ValueError("campaign plan is invalid: " + "; ".join(payload["validation_errors"]))
    preflight = harness.preflight_payload(payload, model_overrides)
    manifest = build_manifest(payload, plan_path, preflight, seed)
    write_json(output_path, manifest)
    return {
        "ok": True,
        "campaign_id": manifest["campaign_id"],
        "run_count": manifest["schedule"]["run_count"],
        "wave_count": manifest["schedule"]["wave_count"],
        "output_path": str(output_path),
    }


def variant_map(manifest: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in manifest["variants"]}


def runtime_environment_errors(manifest: Dict[str, Any]) -> List[str]:
    errors = []
    try:
        commit, dirty = harness.repository_state()
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return [f"could not read repository state: {exc}"]
    if dirty:
        errors.append("repository worktree is dirty; campaign execution requires a clean commit")
    if commit != manifest["repository"]["commit"]:
        errors.append("current repository commit does not match campaign lock")

    for variant in manifest["variants"]:
        executable = "codex" if variant["harness"] == "codex-cli" else "claude"
        if harness.shutil.which(executable) is None:
            errors.append(f"campaign executable is not installed: {executable}")
            continue
        try:
            version = harness.command_version(executable)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            errors.append(f"could not read {executable} version: {exc}")
            continue
        if version != variant["agent_version"]:
            errors.append(f"{executable} version does not match campaign lock")
    locked_mcp = manifest.get("mcp_contract")
    if isinstance(locked_mcp, dict):
        try:
            runtime_mcp = harness.mcp_runtime_preflight()
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"could not validate MCP runtime: {exc}")
        else:
            if not runtime_mcp.get("ready"):
                errors.extend(
                    f"MCP runtime: {issue}" for issue in runtime_mcp.get("issues", [])
                )
            for field, expected in locked_mcp.items():
                if runtime_mcp.get(field) != expected:
                    errors.append(f"MCP runtime {field} does not match campaign lock")
    return errors


def mcp_result_provenance_errors(
    manifest: Dict[str, Any], result: Dict[str, Any]
) -> List[str]:
    locked_mcp = manifest.get("mcp_contract")
    provenance = result.get("provenance")
    condition_context = (
        provenance.get("condition_context") if isinstance(provenance, dict) else None
    )
    if result.get("condition") == harness.MCP_CONDITION:
        if not isinstance(locked_mcp, dict):
            return ["MCP result has no campaign contract lock"]
        if not isinstance(condition_context, dict):
            return ["MCP result requires condition_context provenance"]
        return [
            f"MCP result {field} does not match campaign lock"
            for field, expected in locked_mcp.items()
            if condition_context.get(field) != expected
        ]
    if condition_context is not None:
        return ["non-MCP result must not declare MCP condition_context"]
    return []


def campaign_status(
    manifest: Dict[str, Any], run_root: Path, imported_results: Path
) -> Dict[str, Any]:
    errors, payload = validate_campaign(manifest)
    if errors or payload is None:
        return {"ok": False, "errors": errors, "campaign_id": manifest.get("campaign_id")}

    status = harness.campaign_status(
        payload, [run_root / "results", imported_results]
    )
    variants = variant_map(manifest)
    expected_runs = {run["run_id"]: run for run in payload["runs"]}
    for item in status["runs"]:
        if item["state"] in {"planned", "invalid"} or item["result_path"] is None:
            continue
        expected_run = expected_runs[item["run_id"]]
        expected_variant = variants[expected_run["variant_id"]]
        result = load_json(Path(item["result_path"]))
        if result.get("model") != expected_variant["model"]:
            item["errors"].append(
                f"model expected {expected_variant['model']!r}, found {result.get('model')!r}"
            )
        provenance = result.get("provenance", {})
        if isinstance(provenance, dict):
            if provenance.get("repository_commit") != manifest["repository"]["commit"]:
                item["errors"].append("repository commit does not match campaign lock")
            if provenance.get("agent_version") != expected_variant["agent_version"]:
                item["errors"].append("agent version does not match campaign lock")
        item["errors"].extend(mcp_result_provenance_errors(manifest, result))
        if item["errors"]:
            item["state"] = "invalid"

    counts = Counter(item["state"] for item in status["runs"])
    status["state_counts"] = dict(sorted(counts.items()))
    status["ok"] = counts["invalid"] == 0
    status["execution_complete"] = not any(
        item["state"] in {"planned", "invalid"} for item in status["runs"]
    )
    status["scoring_complete"] = status["execution_complete"] and all(
        item["state"] in {"scored", "skipped"} for item in status["runs"]
    )

    by_run = {item["run_id"]: item for item in status["runs"]}
    wave_reports = []
    next_wave = None
    for wave in manifest["schedule"]["waves"]:
        wave_counts = Counter(by_run[run_id]["state"] for run_id in wave["run_ids"])
        report = {
            "id": wave["id"],
            "task_id": wave["task_id"],
            "trial": wave["trial"],
            "state_counts": dict(sorted(wave_counts.items())),
        }
        wave_reports.append(report)
        if next_wave is None and wave_counts["planned"]:
            next_wave = wave

    campaign_errors = runtime_environment_errors(manifest)
    campaign_errors.extend(
        f"{item['run_id']}: {error}"
        for item in status["runs"]
        for error in item["errors"]
    )
    budget_can_run = (
        next_wave is None
        or status["remaining_budget_usd"] is None
        or status["remaining_budget_usd"] >= manifest["budget"]["max_usd_per_run"]
    )
    if not budget_can_run:
        campaign_errors.append("remaining campaign budget cannot authorize another run")

    status["ok"] = not campaign_errors
    commands = []
    if status["ok"] and next_wave is not None:
        for run_id in next_wave["run_ids"]:
            if by_run[run_id]["state"] != "planned":
                continue
            run = expected_runs[run_id]
            model = variants[run["variant_id"]]["model"]
            argv = [
                "python3",
                "tools/agent_benchmark_harness.py",
                "--plan",
                manifest["plan"]["path"],
                "--execute",
                run_id,
                "--model",
                model,
                "--allow-paid-run",
                "--output-root",
                str(run_root),
            ]
            commands.append({"run_id": run_id, "argv": argv, "shell": shlex.join(argv)})

    status.update(
        {
            "campaign_id": manifest["campaign_id"],
            "errors": campaign_errors,
            "budget_can_run": budget_can_run,
            "waves": wave_reports,
            "next_wave": next_wave["id"] if next_wave else None,
            "next_wave_commands": commands,
        }
    )
    return status


def staging_artifact_path(staging_root: Path, public_path: Any) -> Optional[Path]:
    if not isinstance(public_path, str) or not public_path:
        return None
    path = Path(public_path)
    if path.is_absolute() or ".." in path.parts:
        return None
    try:
        relative = path.relative_to("agent-bench")
    except ValueError:
        return None
    candidate = (staging_root / relative).resolve()
    if not path_is_within(candidate, staging_root):
        return None
    return candidate


def private_path_findings(staging_root: Path) -> List[str]:
    findings = []
    if not staging_root.exists():
        return findings
    for path in sorted(staging_root.rglob("*")):
        lowered = str(path.relative_to(staging_root)).lower()
        if any(marker in lowered for marker in PRIVATE_PATH_MARKERS):
            findings.append(f"private review artifact must not be imported: {lowered}")
    return findings


def audit_staging(
    manifest: Dict[str, Any],
    staging_root: Path,
    allow_partial: bool = False,
    security_reviewer: Optional[str] = None,
) -> Dict[str, Any]:
    errors, payload = validate_campaign(manifest)
    warnings = []
    if errors or payload is None:
        return {
            "ok": False,
            "ready_for_import": False,
            "campaign_id": manifest.get("campaign_id"),
            "errors": errors,
            "warnings": warnings,
        }

    errors.extend(private_path_findings(staging_root))
    symlink_findings = []
    if staging_root.exists():
        symlink_findings = [
            f"staging bundle must not contain symlinks: {path.relative_to(staging_root)}"
            for path in sorted(staging_root.rglob("*"))
            if path.is_symlink()
        ]
        errors.extend(symlink_findings)
    expected_runs = {run["run_id"]: run for run in payload["runs"]}
    variants = variant_map(manifest)
    tasks = harness.load_tasks()
    result_dir = staging_root / "results"
    result_paths = sorted(result_dir.glob("*.json")) if result_dir.is_dir() else []
    if not result_paths:
        errors.append("staging bundle contains no result records")

    audited_runs = []
    seen = set()
    for result_path in result_paths:
        try:
            result = load_json(result_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{result_path.name}: could not load result: {exc}")
            audited_runs.append(
                {
                    "run_id": None,
                    "task_id": None,
                    "agent": None,
                    "model": None,
                    "condition": None,
                    "trial": None,
                    "ok": False,
                    "errors": [f"could not load result: {exc}"],
                }
            )
            continue
        run_id = result.get("run_id")
        run_errors = []
        if run_id in seen:
            run_errors.append("duplicate staged run id")
        seen.add(run_id)
        expected_run = expected_runs.get(run_id)
        if expected_run is None:
            run_errors.append("run id is not part of the campaign")
        else:
            run_errors.extend(harness.result_identity_errors(expected_run, result))
            expected_variant = variants[expected_run["variant_id"]]
            if result.get("model") != expected_variant["model"]:
                run_errors.append("model does not match campaign lock")
            if result.get("status") != "scored":
                run_errors.append("public import requires a scored result")
            provenance = result.get("provenance", {})
            if not isinstance(provenance, dict):
                run_errors.append("result provenance must be an object")
            else:
                if provenance.get("repository_commit") != manifest["repository"]["commit"]:
                    run_errors.append("repository commit does not match campaign lock")
                if provenance.get("repository_dirty") is not False:
                    run_errors.append("public import requires a clean repository snapshot")
                if provenance.get("agent_version") != expected_variant["agent_version"]:
                    run_errors.append("agent version does not match campaign lock")
            run_errors.extend(mcp_result_provenance_errors(manifest, result))
            evaluation = result.get("evaluation")
            if not isinstance(evaluation, dict):
                run_errors.append("scored result requires evaluation provenance")
            else:
                reviewer_ids = evaluation.get("evaluator_ids")
                if (
                    evaluation.get("blinded") is not True
                    or not isinstance(reviewer_ids, list)
                    or len(reviewer_ids) != 2
                    or len(set(reviewer_ids)) != 2
                ):
                    run_errors.append("result requires exactly two independent blinded reviewers")

            candidate = dict(result)
            candidate["_path"] = result_path
            run_errors.extend(
                benchmark_runner.validate_result(
                    candidate, {task_id: task for task_id, task in tasks.items()}
                )
            )

        artifacts = result.get("artifacts", [])
        if not artifacts:
            run_errors.append("scored result requires a public artifact")
        for artifact in artifacts if isinstance(artifacts, list) else []:
            if not isinstance(artifact, dict):
                run_errors.append("artifact entry must be an object")
                continue
            artifact_path = staging_artifact_path(staging_root, artifact.get("path"))
            expected_prefix = Path("agent-bench") / "artifacts" / str(run_id)
            public_path = Path(str(artifact.get("path", "")))
            try:
                public_path.relative_to(expected_prefix)
            except ValueError:
                run_errors.append("public artifact path must be scoped to its run id")
            if artifact_path is None or not artifact_path.is_file():
                run_errors.append("public artifact is missing from staging")
            elif artifact.get("sha256") != harness.sha256_path(artifact_path):
                run_errors.append("public artifact digest does not match staging")

        if run_errors:
            errors.extend(f"{run_id or result_path.name}: {error}" for error in run_errors)
        audited_runs.append(
            {
                "run_id": run_id,
                "task_id": result.get("task_id"),
                "agent": result.get("agent"),
                "model": result.get("model"),
                "condition": result.get("condition"),
                "trial": result.get("trial"),
                "ok": not run_errors,
                "errors": run_errors,
            }
        )

    missing = sorted(set(expected_runs) - seen)
    unexpected = sorted(seen - set(expected_runs), key=str)
    if missing:
        message = f"staging bundle is missing {len(missing)} campaign run(s)"
        if allow_partial:
            warnings.append(message)
        else:
            errors.append(message)
    if unexpected:
        errors.append(f"staging bundle contains {len(unexpected)} unexpected run(s)")

    safety_findings = []
    if staging_root.exists():
        for path in sorted(staging_root.rglob("*")):
            if path.is_file() and not path.is_symlink():
                safety_findings.extend(audit_safety.audit_file(path))
    if safety_findings:
        errors.append(f"staging bundle has {len(safety_findings)} safety finding(s)")
    security = (
        scan_target(staging_root, fail_on="high")
        if staging_root.exists() and not symlink_findings
        else None
    )
    if security and security["summary"]["blocking_count"]:
        errors.append("staging bundle has blocking security findings")
    elif security and security["summary"]["finding_count"]:
        message = (
            f"staging bundle has {security['summary']['finding_count']} security "
            "finding(s) requiring human review"
        )
        if security_reviewer:
            warnings.append(message + f" (reviewed by {security_reviewer})")
        else:
            errors.append(message)

    complete = not missing and not unexpected and len(seen) == len(expected_runs)
    return {
        "ok": not errors,
        "ready_for_import": not errors,
        "campaign_id": manifest["campaign_id"],
        "complete_campaign": complete,
        "allow_partial": allow_partial,
        "security_reviewer": security_reviewer,
        "expected_run_count": len(expected_runs),
        "staged_run_count": len(result_paths),
        "missing_run_count": len(missing),
        "unexpected_run_count": len(unexpected),
        "safety_finding_count": len(safety_findings),
        "safety_findings": [
            finding.replace(str(staging_root.resolve()), ".")
            for finding in safety_findings
        ],
        "security_verdict": security["summary"]["verdict"] if security else None,
        "security_summary": security["summary"] if security else None,
        "security_findings": security.get("findings", []) if security else [],
        "errors": errors,
        "warnings": warnings,
        "runs": audited_runs,
    }


def print_status(payload: Dict[str, Any]) -> None:
    print(f"Agent benchmark campaign: {payload.get('campaign_id')}")
    if not payload.get("ok"):
        for error in payload.get("errors", []):
            print(f"ERROR: {error}")
        return
    print(f"Runs: {payload['run_count']}")
    for state, count in payload["state_counts"].items():
        print(f"- {state}: {count}")
    print(f"Recorded cost (USD): {payload['recorded_cost_usd']:.4f}")
    print(f"Remaining budget (USD): {payload['remaining_budget_usd']:.4f}")
    print(f"Next wave: {payload['next_wave'] or 'none'}")
    if payload["next_wave_commands"]:
        print("Review and run each command separately; none were executed:")
        for command in payload["next_wave_commands"]:
            print(command["shell"])


def print_audit(payload: Dict[str, Any]) -> None:
    state = "READY" if payload.get("ready_for_import") else "BLOCKED"
    print(f"Campaign staging audit: {state}")
    print(f"Campaign: {payload.get('campaign_id')}")
    if "staged_run_count" in payload:
        print(
            f"Runs: {payload['staged_run_count']}/{payload['expected_run_count']} "
            f"(complete={str(payload['complete_campaign']).lower()})"
        )
    for warning in payload.get("warnings", []):
        print(f"WARNING: {warning}")
    for error in payload.get("errors", []):
        print(f"ERROR: {error}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lock, schedule, and audit an agent benchmark evidence campaign"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Create a clean-commit campaign lock")
    prepare.add_argument("--plan", required=True)
    prepare.add_argument("--model-override", action="append", default=[])
    prepare.add_argument("--seed", type=int, required=True)
    prepare.add_argument("--output", required=True)
    prepare.add_argument("--acknowledge-paid-quota", action="store_true")
    prepare.add_argument("--force", action="store_true")
    prepare.add_argument("--json", action="store_true")

    status = subparsers.add_parser("status", help="Show the next balanced execution wave")
    status.add_argument("--campaign", required=True)
    status.add_argument("--run-root", required=True)
    status.add_argument(
        "--imported-results", default=str(ROOT / "agent-bench" / "results")
    )
    status.add_argument("--json", action="store_true")

    audit = subparsers.add_parser("audit", help="Audit a finalized public staging bundle")
    audit.add_argument("--campaign", required=True)
    audit.add_argument("--staging-root", required=True)
    audit.add_argument("--allow-partial", action="store_true")
    audit.add_argument("--security-reviewer")
    audit.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "prepare":
            payload = prepare_campaign(
                Path(args.plan),
                harness.parse_model_overrides(args.model_override),
                args.seed,
                Path(args.output),
                args.acknowledge_paid_quota,
                args.force,
            )
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(
                    f"Wrote campaign {payload['campaign_id']} with "
                    f"{payload['run_count']} runs in {payload['wave_count']} waves to "
                    f"{payload['output_path']}."
                )
            return 0

        manifest = load_json(Path(args.campaign))
        if args.command == "status":
            payload = campaign_status(
                manifest, Path(args.run_root), Path(args.imported_results)
            )
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print_status(payload)
            return 0 if payload.get("ok") else 1

        payload = audit_staging(
            manifest,
            Path(args.staging_root),
            args.allow_partial,
            args.security_reviewer,
        )
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print_audit(payload)
        return 0 if payload.get("ready_for_import") else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
