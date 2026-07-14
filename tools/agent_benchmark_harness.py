#!/usr/bin/env python3
"""Plan, isolate, and explicitly execute HPC Skill Hub agent benchmarks."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "agent-bench" / "tasks"
DEFAULT_PLAN = ROOT / "agent-bench" / "plans" / "calibration-v0.2.json"
DEFAULT_REPORT = ROOT / "docs" / "AGENT_BENCHMARK_PLAN.md"
PLAN_SCHEMA = "../../schemas/agent-benchmark-plan.schema.json"
RESULT_SCHEMA = "../../schemas/agent-benchmark-result.schema.json"
HARNESS_VERSION = "0.5.0"
MCP_CONDITION = "mcp-enabled"
MCP_CONTRACT_PATH = ROOT / "integrations" / "mcp-client.json"
ALLOWED_CONDITIONS = {
    "baseline",
    "docs-only",
    "skill-enabled",
    MCP_CONDITION,
    "skill-site-adapter",
}
ALLOWED_HARNESSES = {"codex-cli", "claude-code"}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mcp_contract() -> Dict[str, Any]:
    contract = load_json(MCP_CONTRACT_PATH)
    server = contract.get("server")
    if not isinstance(server, dict):
        raise ValueError("MCP client contract must contain a server object")
    if server.get("transport") != "stdio":
        raise ValueError("benchmark MCP server must use stdio transport")
    if server.get("read_only") is not True:
        raise ValueError("benchmark MCP server must be read-only")
    if not isinstance(server.get("id"), str) or not server["id"]:
        raise ValueError("benchmark MCP server must declare an id")
    if not isinstance(server.get("command"), str) or not server["command"]:
        raise ValueError("benchmark MCP server must declare a command")
    if not isinstance(server.get("args"), list):
        raise ValueError("benchmark MCP server args must be a list")
    if not isinstance(server.get("env"), dict):
        raise ValueError("benchmark MCP server env must be an object")
    return contract


def mcp_condition_context(package_version: Optional[str] = None) -> Dict[str, Any]:
    server = mcp_contract()["server"]
    context = {
        "mcp_server_id": server["id"],
        "mcp_contract_path": rel(MCP_CONTRACT_PATH),
        "mcp_contract_sha256": sha256_path(MCP_CONTRACT_PATH),
        "mcp_read_only": True,
    }
    if package_version is not None:
        context["mcp_package_version"] = package_version
    return context


def decoded_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_tasks() -> Dict[str, Dict[str, Any]]:
    tasks = {}
    for path in sorted(TASK_DIR.glob("*.json")):
        task = load_json(path)
        task["_path"] = path
        tasks[task["id"]] = task
    return tasks


def validate_plan(plan: Dict[str, Any], tasks: Dict[str, Dict[str, Any]]) -> List[str]:
    errors = []
    required = {
        "$schema",
        "id",
        "name",
        "version",
        "status",
        "description",
        "repository_ref",
        "task_ids",
        "conditions",
        "trials_per_condition",
        "variants",
        "execution",
    }
    for field in sorted(required - set(plan)):
        errors.append(f"plan missing field {field}")
    for field in sorted(set(plan) - required):
        errors.append(f"plan has unknown field {field}")
    if plan.get("$schema") != PLAN_SCHEMA:
        errors.append(f"plan expected $schema {PLAN_SCHEMA}")

    task_ids = plan.get("task_ids", [])
    if not isinstance(task_ids, list) or not task_ids:
        errors.append("plan task_ids must be a non-empty list")
        task_ids = []
    if len(task_ids) != len(set(task_ids)):
        errors.append("plan task_ids must be unique")
    for task_id in task_ids:
        if task_id not in tasks:
            errors.append(f"plan references unknown task {task_id}")

    conditions = plan.get("conditions", [])
    if not isinstance(conditions, list) or not conditions:
        errors.append("plan conditions must be a non-empty list")
        conditions = []
    if len(conditions) != len(set(conditions)):
        errors.append("plan conditions must be unique")
    for condition in conditions:
        if condition not in ALLOWED_CONDITIONS:
            errors.append(f"plan uses unknown condition {condition}")
    if MCP_CONDITION in conditions:
        try:
            mcp_contract()
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"plan MCP condition contract is invalid: {exc}")
    for task_id in task_ids:
        if task_id in tasks:
            missing = sorted(set(conditions) - set(tasks[task_id].get("conditions", [])))
            if missing:
                errors.append(f"task {task_id} does not declare plan conditions {missing}")

    trials = plan.get("trials_per_condition")
    if not isinstance(trials, int) or isinstance(trials, bool) or trials < 1 or trials > 20:
        errors.append("plan trials_per_condition must be between 1 and 20")

    variants = plan.get("variants", [])
    if not isinstance(variants, list) or not variants:
        errors.append("plan variants must be a non-empty list")
        variants = []
    variant_ids = []
    for variant in variants:
        if not isinstance(variant, dict):
            errors.append("plan variant must be an object")
            continue
        variant_ids.append(variant.get("id"))
        if variant.get("harness") not in ALLOWED_HARNESSES:
            errors.append(f"variant {variant.get('id')} uses unsupported harness")
        if not isinstance(variant.get("model_parameters"), dict):
            errors.append(f"variant {variant.get('id')} model_parameters must be an object")
    if len(variant_ids) != len(set(variant_ids)):
        errors.append("plan variant ids must be unique")

    execution = plan.get("execution", {})
    if not isinstance(execution, dict):
        errors.append("plan execution must be an object")
    else:
        max_turns = execution.get("max_turns")
        if not isinstance(max_turns, int) or max_turns < 1:
            errors.append("plan execution max_turns must be positive")
        budget = execution.get("max_budget_usd_per_run")
        if budget is not None and (
            not isinstance(budget, (int, float))
            or isinstance(budget, bool)
            or budget <= 0
        ):
            errors.append("plan max_budget_usd_per_run must be positive or null")
        total_budget = execution.get("max_total_budget_usd")
        if total_budget is not None and (
            not isinstance(total_budget, (int, float))
            or isinstance(total_budget, bool)
            or total_budget <= 0
        ):
            errors.append("plan max_total_budget_usd must be positive when set")
        elif total_budget is not None and budget is None:
            errors.append("plan with max_total_budget_usd must set max_budget_usd_per_run")
        elif (
            total_budget is not None
            and isinstance(budget, (int, float))
            and not isinstance(budget, bool)
            and total_budget < budget
        ):
            errors.append("plan max_total_budget_usd cannot be below the per-run budget")
        acknowledgement = execution.get("require_paid_run_acknowledgement")
        if total_budget is not None and acknowledgement is not True:
            errors.append(
                "plan with max_total_budget_usd must require paid-run acknowledgement"
            )
        elif acknowledgement is not None and acknowledgement is not True:
            errors.append("plan require_paid_run_acknowledgement must be true when set")
        if not isinstance(execution.get("retain_workspaces"), bool):
            errors.append("plan retain_workspaces must be boolean")
    return errors


def build_matrix(plan: Dict[str, Any], tasks: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    runs = []
    for variant in plan["variants"]:
        for task_id in plan["task_ids"]:
            task = tasks[task_id]
            for condition in plan["conditions"]:
                for trial in range(1, plan["trials_per_condition"] + 1):
                    run_id = (
                        f"{plan['id']}-{variant['id']}-{task_id}-{condition}-t{trial:02d}"
                    )
                    run = {
                        "run_id": run_id,
                        "plan_id": plan["id"],
                        "plan_version": plan["version"],
                        "variant_id": variant["id"],
                        "agent": variant["agent"],
                        "harness": variant["harness"],
                        "model": variant["model"],
                        "model_parameters": variant["model_parameters"],
                        "task_id": task_id,
                        "task_version": task["version"],
                        "condition": condition,
                        "trial": trial,
                        "workspace_mode": task["execution"]["workspace_mode"],
                        "network_access": task["execution"]["network_access"],
                        "timeout_seconds": task["execution"]["timeout_seconds"],
                    }
                    if condition == MCP_CONDITION:
                        run["condition_context"] = mcp_condition_context()
                    runs.append(run)
    return runs


def plan_payload(plan_path: Path = DEFAULT_PLAN) -> Dict[str, Any]:
    plan = load_json(plan_path)
    tasks = load_tasks()
    errors = validate_plan(plan, tasks)
    if errors:
        return {"ok": False, "validation_errors": errors, "run_count": 0, "runs": []}
    runs = build_matrix(plan, tasks)
    run_ids = [run["run_id"] for run in runs]
    if len(run_ids) != len(set(run_ids)):
        errors.append("plan generated duplicate run ids")
    return {
        "ok": not errors,
        "validation_errors": errors,
        "plan": {key: value for key, value in plan.items() if key != "$schema"},
        "plan_path": rel(plan_path),
        "run_count": len(runs),
        "agent_counts": dict(sorted(Counter(run["agent"] for run in runs).items())),
        "condition_counts": dict(sorted(Counter(run["condition"] for run in runs).items())),
        "task_counts": dict(sorted(Counter(run["task_id"] for run in runs).items())),
        "runs": runs,
    }


def plan_report(payload: Dict[str, Any]) -> str:
    plan = payload["plan"]
    lines = [
        "# Agent Benchmark Calibration Plan",
        "",
        "This report is generated by `tools/agent_benchmark_harness.py`. Do not edit it by hand.",
        "",
        f"Plan: `{plan['id']}` v{plan['version']} (`{plan['status']}`)",
        "",
        plan["description"],
        "",
        "## Matrix",
        "",
        "| Signal | Value |",
        "| --- | ---: |",
        f"| Planned runs | {payload['run_count']} |",
        f"| Tasks | {len(plan['task_ids'])} |",
        f"| Conditions | {len(plan['conditions'])} |",
        f"| Agent variants | {len(plan['variants'])} |",
        f"| Trials per task and condition | {plan['trials_per_condition']} |",
        f"| Max budget per run (USD) | {plan['execution']['max_budget_usd_per_run'] if plan['execution']['max_budget_usd_per_run'] is not None else 'not set'} |",
        f"| Max campaign budget (USD) | {plan['execution'].get('max_total_budget_usd', 'not set')} |",
        f"| Paid-run acknowledgement | {str(plan['execution'].get('require_paid_run_acknowledgement', False)).lower()} |",
    ]
    for agent, count in payload["agent_counts"].items():
        lines.append(f"| Agent `{agent}` | {count} |")
    for condition, count in payload["condition_counts"].items():
        lines.append(f"| Condition `{condition}` | {count} |")

    lines.extend(
        [
            "",
            "## Variants",
            "",
            "| Variant | Agent | Harness | Model |",
            "| --- | --- | --- | --- |",
        ]
    )
    for variant in plan["variants"]:
        lines.append(
            f"| `{variant['id']}` | `{variant['agent']}` | `{variant['harness']}` | "
            f"`{variant['model']}` |"
        )

    lines.extend(
        [
            "",
            "## Calibration Tasks",
            "",
            "| Task | Planned runs |",
            "| --- | ---: |",
        ]
    )
    for task_id, count in payload["task_counts"].items():
        lines.append(f"| [`{task_id}`](../agent-bench/tasks/{task_id}.json) | {count} |")

    lines.extend(
        [
            "",
            "## Execution Gate",
            "",
            "The harness is dry-run by default. A real run requires one explicit run id, an exact",
            "model id, and `--allow-paid-run`. Each run uses an isolated context packet, disables",
            "network use in the task contract, captures output and changed files outside the",
            "repository, and produces a `pending-review` result. No result becomes scored until",
            "a reviewer records rubric and evaluator provenance.",
            "",
            "Use `--preflight` with exact per-variant model overrides before execution. Use",
            "`--status` to find the next planned run and detect duplicate or mismatched results.",
            "Preflight labels Claude Code's provider CLI budget as a hard limit and Codex's",
            "allowance as requiring external quota monitoring.",
        ]
    )
    return "\n".join(lines)


def support_paths(task: Dict[str, Any], run: Dict[str, Any]) -> List[Path]:
    paths = []
    condition = run["condition"]
    for fixture in task["fixtures"]:
        if condition in fixture["conditions"]:
            paths.append(ROOT / fixture["path"])

    if condition in {"docs-only", "skill-enabled", "skill-site-adapter"}:
        paths.append(ROOT / "AGENTS.md")
        if run["harness"] == "claude-code":
            paths.append(ROOT / "CLAUDE.md")

    if condition in {"skill-enabled", "skill-site-adapter"}:
        paths.extend(
            [
                ROOT / "registry" / "index.json",
                ROOT / "tools" / "hpc_skill.py",
                ROOT / "src" / "hpc_skill_hub",
            ]
        )
        if run["harness"] == "codex-cli":
            paths.append(ROOT / ".agents" / "skills" / "hpc-skill-hub")
        else:
            paths.append(ROOT / ".claude" / "skills" / "hpc-skill-hub")
        for skill_id in task["skill_ids"]:
            paths.append(ROOT / "skills" / skill_id)
    return paths


def copy_repo_path(source: Path, workspace: Path) -> None:
    relative = source.relative_to(ROOT)
    target = workspace / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
    else:
        shutil.copy2(source, target)


def write_mcp_client_config(workspace: Path) -> Path:
    server = mcp_contract()["server"]
    path = workspace / ".mcp.json"
    write_json(
        path,
        {
            "mcpServers": {
                server["id"]: {
                    "type": server["transport"],
                    "command": server["command"],
                    "args": server["args"],
                    "env": server["env"],
                }
            }
        },
    )
    return path


def prompt_text(task: Dict[str, Any], condition: str) -> str:
    fixture_lines = [
        f"- `{fixture['path']}`: {fixture['description']}"
        for fixture in task["fixtures"]
        if condition in fixture["conditions"]
    ]
    if not fixture_lines:
        fixture_lines = ["- No task-specific fixture files are required."]
    allowed_paths = task["execution"]["allowed_write_paths"]
    if allowed_paths:
        write_rule = "You may edit only: " + ", ".join(f"`{path}`" for path in allowed_paths) + "."
    else:
        write_rule = "Treat the workspace as read-only."
    if condition == MCP_CONDITION:
        context_boundary = (
            "The files present in this isolated workspace and the explicitly configured "
            "read-only HPC Skill Hub MCP server are the complete context available for this "
            "run. Use only that server for registry discovery and skill context; do not infer "
            "other repository instructions or site policy, and do not use the network."
        )
    else:
        context_boundary = (
            "The files present in this isolated workspace are the complete context available "
            "for this run. Do not infer that missing repository instructions, skills, or site "
            "policy exist elsewhere, and do not use the network."
        )
    return "\n".join(
        [
            f"# {task['name']}",
            "",
            task["prompt"],
            "",
            "## Available Inputs",
            "",
            *fixture_lines,
            "",
            context_boundary,
            "",
            "## Execution Constraints",
            "",
            f"- {write_rule}",
            "- Do not submit jobs, move data, install software, open tunnels, or consume allocations.",
            "- Keep private hostnames, users, accounts, allocations, tokens, and paths out of output.",
            "- Return a concise final answer and identify any assumptions that remain unresolved.",
            "",
        ]
    )


def materialize_run(
    payload: Dict[str, Any], run_id: str, workspace_root: Path, force: bool = False
) -> Tuple[Dict[str, Any], Path]:
    run = next((item for item in payload["runs"] if item["run_id"] == run_id), None)
    if run is None:
        raise ValueError(f"unknown run id {run_id}")
    workspace = workspace_root / run_id
    if workspace.exists():
        if not force:
            raise ValueError(f"workspace already exists: {workspace}")
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)
    task = load_tasks()[run["task_id"]]
    for path in support_paths(task, run):
        copy_repo_path(path, workspace)
    if run["condition"] == MCP_CONDITION and run["harness"] == "claude-code":
        write_mcp_client_config(workspace)
    (workspace / "BENCHMARK_TASK.md").write_text(
        prompt_text(task, run["condition"]), encoding="utf-8"
    )
    return run, workspace


def file_snapshot(workspace: Path) -> Dict[str, str]:
    snapshot = {}
    for path in sorted(workspace.rglob("*")):
        if path.is_file():
            snapshot[str(path.relative_to(workspace))] = sha256_path(path)
    return snapshot


def capture_changes(
    workspace: Path, before: Dict[str, str], artifact_dir: Path
) -> Optional[Path]:
    after = file_snapshot(workspace)
    changed = sorted(path for path, digest in after.items() if before.get(path) != digest)
    deleted = sorted(path for path in before if path not in after)
    if not changed and not deleted:
        return None
    changed_root = artifact_dir / "changed-files"
    for relative in changed:
        source = workspace / relative
        target = changed_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    manifest = artifact_dir / "workspace-changes.json"
    write_json(manifest, {"changed": changed, "deleted": deleted})
    return manifest


def command_version(executable: str) -> str:
    result = subprocess.run(
        [executable, "--version"],
        text=True,
        capture_output=True,
        timeout=15,
        check=False,
    )
    output = (result.stdout or result.stderr).strip().splitlines()
    if result.returncode != 0 or not output:
        raise ValueError(f"could not read {executable} version")
    return output[-1]


def parse_model_overrides(values: Iterable[str]) -> Dict[str, str]:
    overrides: Dict[str, str] = {}
    for value in values:
        variant_id, separator, model = value.partition("=")
        if not separator or not variant_id or not model:
            raise ValueError(
                f"invalid model override {value!r}; expected <variant-id>=<exact-model-id>"
            )
        if variant_id in overrides:
            raise ValueError(f"duplicate model override for {variant_id}")
        overrides[variant_id] = model
    return overrides


def mcp_runtime_preflight() -> Dict[str, Any]:
    server = mcp_contract()["server"]
    server_path = shutil.which(server["command"])
    doctor_path = shutil.which("hpc-skill")
    issues = []
    package_version = None
    server_version = None
    doctor_status = None
    if server_path is None:
        issues.append(f"required MCP executable is not installed: {server['command']}")
    else:
        try:
            version_result = subprocess.run(
                [server_path, "--version"],
                text=True,
                capture_output=True,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            issues.append(f"MCP server version could not be evaluated: {exc}")
        else:
            version_output = (version_result.stdout or version_result.stderr).strip()
            if version_result.returncode != 0 or not version_output:
                issues.append("MCP server did not report a version")
            else:
                server_version = version_output.splitlines()[-1]
    if doctor_path is None:
        issues.append("required MCP doctor executable is not installed: hpc-skill")
    else:
        try:
            completed = subprocess.run(
                [doctor_path, "doctor", "--require-mcp", "--json"],
                text=True,
                capture_output=True,
                timeout=60,
                check=False,
            )
            report = json.loads(completed.stdout)
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
            issues.append(f"MCP doctor could not be evaluated: {exc}")
        else:
            doctor_status = report.get("status")
            checks = report.get("checks", [])
            package_check = next(
                (
                    item
                    for item in checks
                    if isinstance(item, dict) and item.get("id") == "package-version"
                ),
                None,
            )
            if isinstance(package_check, dict):
                details = package_check.get("details", {})
                if isinstance(details, dict):
                    value = details.get("distribution_version")
                    if isinstance(value, str) and value:
                        package_version = value
            if completed.returncode != 0 or report.get("ok") is not True:
                issues.append("hpc-skill doctor --require-mcp did not pass")
            if package_version is None:
                issues.append("MCP doctor did not report an installed package version")
    if server_path and doctor_path:
        if Path(server_path).resolve().parent != Path(doctor_path).resolve().parent:
            issues.append("MCP server and doctor must come from the same environment")
    if server_version and package_version and server_version != package_version:
        issues.append("MCP server version does not match the doctor package version")

    context = mcp_condition_context(package_version)
    return {
        **context,
        "server_command": server["command"],
        "server_executable_path": server_path,
        "server_version": server_version,
        "doctor_executable_path": doctor_path,
        "doctor_status": doctor_status,
        "ready": not issues,
        "issues": issues,
    }


def preflight_payload(
    payload: Dict[str, Any], model_overrides: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    model_overrides = model_overrides or {}
    try:
        repository_commit, repository_dirty = repository_state()
    except (OSError, subprocess.SubprocessError) as exc:
        repository_commit = None
        repository_dirty = None
        blockers = [f"could not read repository state: {exc}"]
    else:
        blockers = []
        if repository_dirty:
            blockers.append("repository worktree is dirty; public evidence requires a clean commit")
    known_variants = {variant["id"] for variant in payload["plan"]["variants"]}
    blockers.extend(
        f"model override references unknown variant {variant_id}"
        for variant_id in sorted(set(model_overrides) - known_variants)
    )
    if any(run["network_access"] for run in payload["runs"]):
        blockers.append("benchmark plan contains a run with network access enabled")
    variants = []
    per_run_budget = payload["plan"]["execution"].get("max_budget_usd_per_run")
    for variant in payload["plan"]["variants"]:
        executable = "codex" if variant["harness"] == "codex-cli" else "claude"
        executable_path = shutil.which(executable)
        version = None
        issues = []
        if executable_path is None:
            issues.append(f"required executable is not installed: {executable}")
        else:
            try:
                version = command_version(executable)
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                issues.append(str(exc))
        model = model_overrides.get(variant["id"], variant["model"])
        exact_model = bool(model and model != "configured-default")
        if not exact_model:
            issues.append("exact model id is required")
        if per_run_budget is None:
            budget_enforcement = "not-configured"
        elif variant["harness"] == "claude-code":
            budget_enforcement = "provider-cli-hard-limit"
        else:
            budget_enforcement = "external-monitoring-required"
        blockers.extend(f"variant {variant['id']}: {issue}" for issue in issues)
        variants.append(
            {
                "id": variant["id"],
                "agent": variant["agent"],
                "harness": variant["harness"],
                "executable": executable,
                "executable_path": executable_path,
                "agent_version": version,
                "model": model,
                "exact_model": exact_model,
                "budget_enforcement": budget_enforcement,
                "ready": not issues,
                "issues": issues,
            }
        )
    mcp = None
    if MCP_CONDITION in payload["plan"]["conditions"]:
        try:
            mcp = dict(mcp_runtime_preflight())
            mcp["issues"] = list(mcp.get("issues", []))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            mcp = {"ready": False, "issues": [str(exc)]}
        expected_package_version = payload["plan"]["version"]
        if mcp.get("mcp_package_version") != expected_package_version:
            mcp["issues"].append(
                "installed MCP package version must match plan version "
                f"{expected_package_version}"
            )
            mcp["ready"] = False
        blockers.extend(f"mcp-enabled: {issue}" for issue in mcp["issues"])
    return {
        "ok": not blockers,
        "plan_id": payload["plan"]["id"],
        "run_count": payload["run_count"],
        "repository_commit": repository_commit,
        "repository_dirty": repository_dirty,
        "max_budget_usd_per_run": per_run_budget,
        "max_total_budget_usd": payload["plan"]["execution"].get(
            "max_total_budget_usd"
        ),
        "variants": variants,
        "mcp": mcp,
        "blockers": blockers,
    }


def preflight_text(preflight: Dict[str, Any]) -> str:
    lines = [
        f"Agent benchmark preflight: {'READY' if preflight['ok'] else 'BLOCKED'}",
        f"Plan: {preflight['plan_id']} ({preflight['run_count']} runs)",
        f"Per-run budget (USD): {preflight['max_budget_usd_per_run'] or 'not set'}",
        f"Campaign budget (USD): {preflight['max_total_budget_usd'] or 'not set'}",
    ]
    for variant in preflight["variants"]:
        state = "READY" if variant["ready"] else "BLOCKED"
        version = variant["agent_version"] or "unavailable"
        lines.append(
            f"{state}: {variant['id']}: {variant['executable']} {version}; "
            f"model={variant['model']}; budget={variant['budget_enforcement']}"
        )
        for issue in variant["issues"]:
            lines.append(f"  - {issue}")
    if preflight.get("mcp") is not None:
        mcp = preflight["mcp"]
        state = "READY" if mcp.get("ready") else "BLOCKED"
        lines.append(
            f"{state}: mcp-enabled: server={mcp.get('mcp_server_id', 'unknown')}; "
            f"package={mcp.get('mcp_package_version', 'unavailable')}; "
            f"doctor={mcp.get('doctor_status', 'unavailable')}"
        )
        for issue in mcp.get("issues", []):
            lines.append(f"  - {issue}")
    if preflight["blockers"]:
        lines.append("Blockers:")
        lines.extend(f"- {blocker}" for blocker in preflight["blockers"])
    return "\n".join(lines)


def result_identity_errors(run: Dict[str, Any], result: Dict[str, Any]) -> List[str]:
    errors = []
    expected = {
        "run_id": run["run_id"],
        "task_id": run["task_id"],
        "task_version": run["task_version"],
        "trial": run["trial"],
        "agent": run["agent"],
        "harness": run["harness"],
        "condition": run["condition"],
    }
    for field, value in expected.items():
        if result.get(field) != value:
            errors.append(f"{field} expected {value!r}, found {result.get(field)!r}")
    if run["model"] != "configured-default" and result.get("model") != run["model"]:
        errors.append(f"model expected {run['model']!r}, found {result.get('model')!r}")
    if not result.get("model") or result.get("model") == "configured-default":
        errors.append("result must record an exact model id")
    if result.get("status") not in {"pending-review", "scored", "failed", "skipped"}:
        errors.append(f"invalid result status {result.get('status')!r}")
    return errors


def campaign_status(payload: Dict[str, Any], result_dirs: Iterable[Path]) -> Dict[str, Any]:
    result_dirs = list(result_dirs)
    runs = []
    counts = Counter()
    recorded_cost_usd = 0.0
    for run in payload["runs"]:
        candidates = [directory / f"{run['run_id']}.json" for directory in result_dirs]
        existing = [path for path in candidates if path.exists()]
        errors = []
        result_path = None
        result_model = None
        result_cost_usd = None
        if len(existing) > 1:
            state = "invalid"
            errors.append("result exists in more than one result directory")
        elif not existing:
            state = "planned"
        else:
            result_path = existing[0]
            try:
                result = load_json(result_path)
            except (OSError, json.JSONDecodeError) as exc:
                state = "invalid"
                errors.append(f"could not load result: {exc}")
            else:
                errors.extend(result_identity_errors(run, result))
                state = "invalid" if errors else result["status"]
                result_model = result.get("model")
                metrics = result.get("metrics", {})
                if (
                    isinstance(metrics, dict)
                    and isinstance(metrics.get("cost_usd"), (int, float))
                    and not isinstance(metrics.get("cost_usd"), bool)
                ):
                    result_cost_usd = float(metrics["cost_usd"])
                    recorded_cost_usd += result_cost_usd
        counts[state] += 1
        runs.append(
            {
                "run_id": run["run_id"],
                "variant_id": run["variant_id"],
                "agent": run["agent"],
                "task_id": run["task_id"],
                "condition": run["condition"],
                "trial": run["trial"],
                "state": state,
                "model": result_model,
                "cost_usd": result_cost_usd,
                "result_path": str(result_path) if result_path else None,
                "errors": errors,
            }
        )
    next_run = next((run["run_id"] for run in runs if run["state"] == "planned"), None)
    execution_complete = not any(run["state"] in {"planned", "invalid"} for run in runs)
    scoring_complete = execution_complete and all(
        run["state"] in {"scored", "skipped"} for run in runs
    )
    total_budget_usd = payload["plan"]["execution"].get("max_total_budget_usd")
    remaining_budget_usd = (
        round(max(0.0, float(total_budget_usd) - recorded_cost_usd), 4)
        if isinstance(total_budget_usd, (int, float))
        else None
    )
    return {
        "ok": counts["invalid"] == 0,
        "plan_id": payload["plan"]["id"],
        "run_count": len(runs),
        "state_counts": dict(sorted(counts.items())),
        "next_run_id": next_run,
        "execution_complete": execution_complete,
        "scoring_complete": scoring_complete,
        "recorded_cost_usd": round(recorded_cost_usd, 4),
        "max_total_budget_usd": total_budget_usd,
        "remaining_budget_usd": remaining_budget_usd,
        "runs": runs,
    }


def status_text(status: Dict[str, Any]) -> str:
    lines = [
        f"Agent benchmark campaign: {status['plan_id']}",
        f"Runs: {status['run_count']}",
    ]
    for state, count in status["state_counts"].items():
        lines.append(f"- {state}: {count}")
    lines.append(f"Next run: {status['next_run_id'] or 'none'}")
    lines.append(f"Execution complete: {str(status['execution_complete']).lower()}")
    lines.append(f"Scoring complete: {str(status['scoring_complete']).lower()}")
    lines.append(f"Recorded cost (USD): {status['recorded_cost_usd']:.4f}")
    if status["max_total_budget_usd"] is not None:
        lines.append(f"Campaign budget (USD): {status['max_total_budget_usd']}")
        lines.append(f"Remaining budget (USD): {status['remaining_budget_usd']:.4f}")
    for run in status["runs"]:
        if run["errors"]:
            lines.append(f"INVALID: {run['run_id']}: {'; '.join(run['errors'])}")
    return "\n".join(lines)


def materialize_all_runs(
    payload: Dict[str, Any], workspace_root: Path, force: bool = False
) -> List[Dict[str, str]]:
    workspaces = []
    for item in payload["runs"]:
        run, workspace = materialize_run(payload, item["run_id"], workspace_root, force=force)
        workspaces.append({"run_id": run["run_id"], "workspace": str(workspace)})
    return workspaces


def build_command(
    run: Dict[str, Any], workspace: Path, model: str, output_file: Path, plan: Dict[str, Any]
) -> List[str]:
    if run["harness"] == "codex-cli":
        command = [
            "codex",
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "--sandbox",
            run["workspace_mode"],
            "--cd",
            str(workspace),
            "--color",
            "never",
            "--json",
            "--output-last-message",
            str(output_file),
            "--model",
            model,
        ]
        if run["condition"] == MCP_CONDITION:
            server = mcp_contract()["server"]
            prefix = f"mcp_servers.{server['id']}"
            command.extend(
                [
                    "--config",
                    f"{prefix}.command={json.dumps(server['command'])}",
                    "--config",
                    f"{prefix}.args={json.dumps(server['args'])}",
                    "--config",
                    f"{prefix}.enabled=true",
                    "--config",
                    f"{prefix}.required=true",
                    "--config",
                    f"{prefix}.startup_timeout_sec=15",
                    "--config",
                    f"{prefix}.tool_timeout_sec=60",
                ]
            )
        command.append("-")
        return command

    tool_names = ["Read", "Glob", "Grep"]
    permission_mode = "plan"
    if run["workspace_mode"] == "workspace-write":
        tool_names.extend(["Edit", "Write"])
        permission_mode = "acceptEdits"
    command = [
        "claude",
        "-p",
        "--output-format",
        "json",
        "--no-session-persistence",
        "--setting-sources",
        "project",
        "--strict-mcp-config",
    ]
    if run["condition"] == MCP_CONDITION:
        server_id = mcp_contract()["server"]["id"]
        mcp_pattern = f"mcp__{server_id}__*"
        command.extend(
            [
                "--mcp-config",
                str(workspace / ".mcp.json"),
                "--allowedTools",
                mcp_pattern,
            ]
        )
    else:
        command.extend(["--disallowedTools", "mcp__*"])
    command.extend(
        [
            "--tools",
            ",".join(tool_names),
            "--permission-mode",
            permission_mode,
            "--max-turns",
            str(plan["execution"]["max_turns"]),
            "--model",
            model,
        ]
    )
    budget = plan["execution"].get("max_budget_usd_per_run")
    if budget is not None:
        command.extend(["--max-budget-usd", str(budget)])
    if run["condition"] == "baseline":
        command.append("--bare")
    command.append(prompt_text(load_tasks()[run["task_id"]], run["condition"]))
    return command


def usage_from_output(harness: str, stdout: str) -> Tuple[Optional[int], Optional[int], Optional[float]]:
    payloads = []
    try:
        if harness == "claude-code":
            payloads = [json.loads(stdout)]
        else:
            payloads = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    except json.JSONDecodeError:
        return None, None, None

    input_tokens = None
    output_tokens = None
    cost = None
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        usage = payload.get("usage")
        if isinstance(usage, dict):
            if isinstance(usage.get("input_tokens"), int):
                input_tokens = usage["input_tokens"]
            if isinstance(usage.get("output_tokens"), int):
                output_tokens = usage["output_tokens"]
        if isinstance(payload.get("total_cost_usd"), (int, float)):
            cost = float(payload["total_cost_usd"])
    return input_tokens, output_tokens, cost


def repository_state() -> Tuple[str, bool]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.strip()
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    )
    return commit, dirty


def artifact_entry(path: Path, description: str, run_id: str) -> Dict[str, Any]:
    return {
        "path": f"agent-bench/artifacts/{run_id}/{path.name}",
        "description": description,
        "sha256": sha256_path(path),
    }


def recorded_campaign_cost(output_root: Path) -> float:
    total = 0.0
    result_dir = output_root / "results"
    if not result_dir.exists():
        return total
    for path in sorted(result_dir.glob("*.json")):
        try:
            result = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        metrics = result.get("metrics", {})
        cost = metrics.get("cost_usd") if isinstance(metrics, dict) else None
        if isinstance(cost, (int, float)) and not isinstance(cost, bool):
            total += float(cost)
    return round(total, 4)


def enforce_campaign_budget(plan: Dict[str, Any], output_root: Path) -> None:
    execution = plan["execution"]
    total_budget = execution.get("max_total_budget_usd")
    if total_budget is None:
        return
    per_run_budget = execution.get("max_budget_usd_per_run")
    if per_run_budget is None:
        raise ValueError("campaign total budget requires a per-run budget")
    recorded = recorded_campaign_cost(output_root)
    if recorded + float(per_run_budget) > float(total_budget) + 1e-9:
        raise ValueError(
            "campaign budget exhausted: "
            f"recorded ${recorded:.4f}, next-run cap ${float(per_run_budget):.4f}, "
            f"total cap ${float(total_budget):.4f}"
        )


def execute_run(
    payload: Dict[str, Any],
    run_id: str,
    model: str,
    output_root: Path,
    workspace_root: Path,
    force: bool,
    allow_dirty_run: bool = False,
) -> Path:
    if not model or model == "configured-default":
        raise ValueError("real execution requires an exact --model value")
    _commit, dirty = repository_state()
    if dirty and not allow_dirty_run:
        raise ValueError(
            "real execution requires a clean repository; commit the benchmark contract "
            "or pass --allow-dirty-run for non-public debugging"
        )
    planned_run = next(
        (item for item in payload["runs"] if item["run_id"] == run_id), None
    )
    if planned_run is None:
        raise ValueError(f"unknown run id {run_id}")
    mcp_runtime = None
    if planned_run["condition"] == MCP_CONDITION:
        mcp_runtime = mcp_runtime_preflight()
        if not mcp_runtime["ready"]:
            raise ValueError(
                "mcp-enabled execution preflight failed: "
                + "; ".join(mcp_runtime["issues"])
            )
        if mcp_runtime.get("mcp_package_version") != payload["plan"]["version"]:
            raise ValueError(
                "mcp-enabled execution requires installed package version "
                f"{payload['plan']['version']}"
            )
    enforce_campaign_budget(payload["plan"], output_root)
    run, workspace = materialize_run(payload, run_id, workspace_root, force=force)
    before = file_snapshot(workspace)
    task = load_tasks()[run["task_id"]]
    artifact_dir = output_root / "artifacts" / run_id
    result_dir = output_root / "results"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    final_output = artifact_dir / "final-output.txt"
    raw_output = artifact_dir / "raw-output.jsonl"
    stderr_output = artifact_dir / "stderr.txt"

    executable = "codex" if run["harness"] == "codex-cli" else "claude"
    if shutil.which(executable) is None:
        raise ValueError(f"required executable is not installed: {executable}")
    agent_version = command_version(executable)
    command = build_command(run, workspace, model, final_output, payload["plan"])
    started_at = utc_now()
    started = time.monotonic()
    failure = None
    try:
        completed = subprocess.run(
            command,
            cwd=workspace,
            input=prompt_text(task, run["condition"])
            if run["harness"] == "codex-cli"
            else None,
            text=True,
            capture_output=True,
            timeout=run["timeout_seconds"],
            check=False,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        status = "pending-review" if completed.returncode == 0 else "failed"
        if completed.returncode != 0:
            failure = {
                "category": "agent-error",
                "summary": f"Agent CLI exited with status {completed.returncode}.",
            }
    except subprocess.TimeoutExpired as exc:
        stdout = decoded_text(exc.stdout)
        stderr = decoded_text(exc.stderr)
        status = "failed"
        failure = {
            "category": "timeout",
            "summary": f"Agent exceeded the {run['timeout_seconds']} second task timeout.",
        }
    completed_at = utc_now()
    wall_time = round(time.monotonic() - started, 3)
    raw_output.write_text(stdout, encoding="utf-8")
    stderr_output.write_text(stderr, encoding="utf-8")
    if not final_output.exists():
        final_text = ""
        if run["harness"] == "claude-code":
            try:
                final_text = json.loads(stdout).get("result", "")
            except (json.JSONDecodeError, AttributeError):
                pass
        final_output.write_text(decoded_text(final_text), encoding="utf-8")

    change_manifest = capture_changes(workspace, before, artifact_dir)
    input_tokens, output_tokens, cost = usage_from_output(run["harness"], stdout)
    commit, dirty = repository_state()
    artifacts = [
        artifact_entry(final_output, "Final agent response.", run_id),
        artifact_entry(raw_output, "Raw structured agent output for private review.", run_id),
        artifact_entry(stderr_output, "Agent CLI stderr for private review.", run_id),
    ]
    if change_manifest is not None:
        artifacts.append(artifact_entry(change_manifest, "Changed-file manifest.", run_id))

    result = {
        "$schema": RESULT_SCHEMA,
        "run_id": run_id,
        "task_id": run["task_id"],
        "task_version": run["task_version"],
        "trial": run["trial"],
        "agent": run["agent"],
        "harness": run["harness"],
        "model": model,
        "condition": run["condition"],
        "started_at": started_at,
        "completed_at": completed_at,
        "status": status,
        "provenance": {
            "repository_commit": commit,
            "repository_dirty": dirty,
            "skill_snapshot": f"working-tree@{commit}" if dirty else commit,
            "task_sha256": sha256_path(task["_path"]),
            "agent_version": agent_version,
            "harness_version": HARNESS_VERSION,
            "invocation_mode": "cli",
            "model_parameters": run["model_parameters"],
            "network_access": run["network_access"],
            "workspace_mode": run["workspace_mode"],
        },
        "metrics": {
            "wall_time_seconds": wall_time,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
        },
        "criteria_scores": [],
        "evaluation": None,
        "failure": failure,
        "artifacts": artifacts,
        "notes": "Pending redaction review and blinded rubric scoring before public import.",
    }
    if mcp_runtime is not None:
        result["provenance"]["condition_context"] = {
            key: mcp_runtime[key]
            for key in [
                "mcp_server_id",
                "mcp_contract_path",
                "mcp_contract_sha256",
                "mcp_read_only",
                "mcp_package_version",
            ]
        }
    result_path = result_dir / f"{run_id}.json"
    write_json(result_path, result)
    if not payload["plan"]["execution"]["retain_workspaces"]:
        shutil.rmtree(workspace)
    return result_path


def check_report(report_path: Path, expected: str) -> List[str]:
    if not report_path.exists():
        return [f"{rel(report_path)} is missing"]
    if report_path.read_text(encoding="utf-8") != expected:
        return [f"{rel(report_path)} is stale; run tools/agent_benchmark_harness.py"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Plan and explicitly execute isolated agent benchmark runs"
    )
    parser.add_argument("--plan", default=str(DEFAULT_PLAN), help="Benchmark plan JSON")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Generated plan report")
    parser.add_argument("--check", action="store_true", help="Validate plan and report freshness")
    parser.add_argument("--json", action="store_true", help="Emit the expanded run matrix")
    parser.add_argument("--materialize", metavar="RUN_ID", help="Create one isolated context packet")
    parser.add_argument(
        "--materialize-all",
        action="store_true",
        help="Create isolated context packets for every planned run without executing agents",
    )
    parser.add_argument("--execute", metavar="RUN_ID", help="Execute one run")
    parser.add_argument("--model", help="Exact model id for a real run")
    parser.add_argument(
        "--workspace-root", default="/tmp/hpc-skill-hub-agent-bench-workspaces"
    )
    parser.add_argument("--output-root", default="/tmp/hpc-skill-hub-agent-bench-runs")
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Check agent executables and exact model ids without running agents",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Report resumable run state from private and imported result directories",
    )
    parser.add_argument(
        "--model-override",
        action="append",
        default=[],
        metavar="VARIANT_ID=MODEL",
        help="Use an exact model id for preflight; repeat for multiple variants",
    )
    parser.add_argument("--force", action="store_true", help="Replace an existing run workspace")
    parser.add_argument(
        "--allow-paid-run",
        action="store_true",
        help="Acknowledge that executing an external agent may consume paid quota",
    )
    parser.add_argument(
        "--allow-dirty-run",
        action="store_true",
        help="Allow a non-public debugging run from a dirty worktree",
    )
    args = parser.parse_args()

    selected_actions = sum(
        bool(value)
        for value in [
            args.preflight,
            args.status,
            args.materialize_all,
            args.materialize,
            args.execute,
        ]
    )
    if selected_actions > 1:
        print(
            "ERROR: choose only one of --preflight, --status, --materialize-all, "
            "--materialize, or --execute",
            file=sys.stderr,
        )
        return 2
    if args.model_override and not args.preflight:
        print("ERROR: --model-override is only valid with --preflight", file=sys.stderr)
        return 2

    payload = plan_payload(Path(args.plan))
    if not payload["ok"]:
        for error in payload["validation_errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    expected_report = plan_report(payload) + "\n"

    try:
        if args.preflight:
            preflight = preflight_payload(payload, parse_model_overrides(args.model_override))
            if args.json:
                print(json.dumps(preflight, indent=2, sort_keys=True))
            else:
                print(preflight_text(preflight))
            return 0 if preflight["ok"] else 1
        if args.status:
            status = campaign_status(
                payload,
                [Path(args.output_root) / "results", ROOT / "agent-bench" / "results"],
            )
            if args.json:
                print(json.dumps(status, indent=2, sort_keys=True))
            else:
                print(status_text(status))
            return 0 if status["ok"] else 1
        if args.materialize_all:
            workspaces = materialize_all_runs(payload, Path(args.workspace_root), force=args.force)
            print(json.dumps({"run_count": len(workspaces), "workspaces": workspaces}, indent=2, sort_keys=True))
            return 0
        if args.materialize:
            run, workspace = materialize_run(
                payload, args.materialize, Path(args.workspace_root), force=args.force
            )
            print(json.dumps({"run": run, "workspace": str(workspace)}, indent=2, sort_keys=True))
            return 0
        if args.execute:
            if not args.allow_paid_run:
                print("ERROR: --execute requires --allow-paid-run", file=sys.stderr)
                return 2
            result_path = execute_run(
                payload,
                args.execute,
                args.model or "",
                Path(args.output_root),
                Path(args.workspace_root),
                args.force,
                args.allow_dirty_run,
            )
            print(f"Wrote pending benchmark result to {result_path}.")
            return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.check:
        errors = check_report(Path(args.report), expected_report)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Agent benchmark plan is current in {rel(Path(args.report))}.")
    else:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(expected_report, encoding="utf-8")
        print(f"Wrote {rel(report_path)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
