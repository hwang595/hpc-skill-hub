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
HARNESS_VERSION = "0.2.0"
ALLOWED_CONDITIONS = {"baseline", "docs-only", "skill-enabled", "skill-site-adapter"}
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
        if budget is not None and (not isinstance(budget, (int, float)) or budget <= 0):
            errors.append("plan max_budget_usd_per_run must be positive or null")
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
                    runs.append(
                        {
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
                    )
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
            "The files present in this isolated workspace are the complete context available for",
            "this run. Do not infer that missing repository instructions, skills, or site policy",
            "exist elsewhere, and do not use the network.",
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
            "-",
        ]
        return command

    tools = "Read,Glob,Grep"
    permission_mode = "plan"
    if run["workspace_mode"] == "workspace-write":
        tools = "Read,Glob,Grep,Edit,Write"
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
        "--disallowedTools",
        "mcp__*",
        "--tools",
        tools,
        "--permission-mode",
        permission_mode,
        "--max-turns",
        str(plan["execution"]["max_turns"]),
        "--model",
        model,
    ]
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


def execute_run(
    payload: Dict[str, Any],
    run_id: str,
    model: str,
    output_root: Path,
    workspace_root: Path,
    force: bool,
) -> Path:
    if not model or model == "configured-default":
        raise ValueError("real execution requires an exact --model value")
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
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        status = "failed"
        failure = {
            "category": "timeout",
            "summary": f"Agent exceeded the {run['timeout_seconds']} second task timeout.",
        }
    completed_at = utc_now()
    wall_time = round(time.monotonic() - started, 3)
    raw_output.write_text(stdout, encoding="utf-8")
    stderr_output.write_text(stderr, encoding="utf-8")
    if not final_output.exists() and run["harness"] == "claude-code":
        try:
            final_output.write_text(json.loads(stdout).get("result", ""), encoding="utf-8")
        except (json.JSONDecodeError, AttributeError):
            final_output.write_text("", encoding="utf-8")

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
    parser.add_argument("--execute", metavar="RUN_ID", help="Execute one run")
    parser.add_argument("--model", help="Exact model id for a real run")
    parser.add_argument(
        "--workspace-root", default="/tmp/hpc-skill-hub-agent-bench-workspaces"
    )
    parser.add_argument("--output-root", default="/tmp/hpc-skill-hub-agent-bench-runs")
    parser.add_argument("--force", action="store_true", help="Replace an existing run workspace")
    parser.add_argument(
        "--allow-paid-run",
        action="store_true",
        help="Acknowledge that executing an external agent may consume paid quota",
    )
    args = parser.parse_args()

    payload = plan_payload(Path(args.plan))
    if not payload["ok"]:
        for error in payload["validation_errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    expected_report = plan_report(payload) + "\n"

    try:
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
