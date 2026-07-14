import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AgentBenchmarkAggregationTests(unittest.TestCase):
    def setUp(self):
        self.runner = load_tool("run_agent_benchmarks")
        self.task = json.loads(
            (ROOT / "agent-bench" / "tasks" / "skill-routing-oom-triage.json").read_text(
                encoding="utf-8"
            )
        )
        self.task_path = ROOT / "agent-bench" / "tasks" / "skill-routing-oom-triage.json"

    def result(self, condition, trial, status, score=None):
        run_id = f"fixture-agent-oom-{condition}-t{trial:02d}"
        criteria_scores = []
        evaluation = None
        failure = None
        if status == "scored":
            criteria_scores = [
                {"criterion_id": criterion["id"], "score": score}
                for criterion in self.task["rubric"]
            ]
            evaluation = {
                "rubric_version": self.task["version"],
                "evaluator_type": "human",
                "evaluator_ids": ["reviewer-a", "reviewer-b"],
                "blinded": True,
                "scored_at": "2026-07-10T18:30:00Z",
            }
        elif status == "failed":
            failure = {"category": "agent-error", "summary": "Synthetic fixture failure."}
        result = {
            "$schema": "../../schemas/agent-benchmark-result.schema.json",
            "run_id": run_id,
            "task_id": self.task["id"],
            "task_version": self.task["version"],
            "trial": trial,
            "agent": "fixture-agent",
            "harness": "fixture-harness",
            "model": "fixture-model-v1",
            "condition": condition,
            "started_at": "2026-07-10T18:00:00Z",
            "completed_at": "2026-07-10T18:01:00Z",
            "status": status,
            "provenance": {
                "repository_commit": "a" * 40,
                "repository_dirty": False,
                "skill_snapshot": "fixture-snapshot-v1",
                "task_sha256": self.runner.sha256_path(self.task_path),
                "agent_version": "fixture-agent 1.0.0",
                "harness_version": "0.2.0",
                "invocation_mode": "import",
                "model_parameters": {},
                "network_access": False,
                "workspace_mode": "read-only",
            },
            "metrics": {
                "wall_time_seconds": 60,
                "input_tokens": 100,
                "output_tokens": 50,
                "cost_usd": 0.01,
            },
            "criteria_scores": criteria_scores,
            "evaluation": evaluation,
            "failure": failure,
            "artifacts": [],
            "notes": "Synthetic public-safe aggregation fixture.",
        }
        if condition == "mcp-enabled":
            result["provenance"]["condition_context"] = {
                "mcp_server_id": "hpc-skill-hub",
                "mcp_contract_path": "integrations/mcp-client.json",
                "mcp_contract_sha256": self.runner.sha256_path(
                    ROOT / "integrations" / "mcp-client.json"
                ),
                "mcp_read_only": True,
                "mcp_package_version": "0.5.0",
            }
        return result

    def test_repeated_trials_failure_rate_and_paired_lift(self):
        results = [
            self.result("baseline", 1, "scored", 0.5),
            self.result("baseline", 2, "scored", 0.7),
            self.result("baseline", 3, "failed"),
            self.result("skill-enabled", 1, "scored", 0.8),
            self.result("skill-enabled", 2, "scored", 0.9),
            self.result("skill-enabled", 3, "pending-review"),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            result_dir = Path(tmpdir)
            for result in results:
                (result_dir / f"{result['run_id']}.json").write_text(
                    json.dumps(result), encoding="utf-8"
                )
            payload = self.runner.benchmark_payload(
                ROOT / "agent-bench" / "tasks", result_dir
            )

        self.assertTrue(payload["ok"], payload["validation_errors"])
        self.assertEqual(payload["result_count"], 6)
        self.assertEqual(payload["scored_result_count"], 4)
        self.assertEqual(payload["failed_result_count"], 1)
        self.assertEqual(payload["pending_review_count"], 1)

        variants = {variant["condition"]: variant for variant in payload["variants"]}
        self.assertEqual(variants["baseline"]["score"], 60.0)
        self.assertEqual(variants["baseline"]["failure_rate"], 33.33)
        self.assertEqual(variants["skill-enabled"]["score"], 85.0)
        self.assertEqual(variants["skill-enabled"]["pending_review_count"], 1)

        self.assertEqual(len(payload["skill_lifts"]), 1)
        lift = payload["skill_lifts"][0]
        self.assertEqual(lift["pair_count"], 2)
        self.assertEqual(lift["reference_condition"], "baseline")
        self.assertEqual(lift["lift"], 25.0)
        self.assertEqual(lift["lift_ci95"], 9.8)
        self.assertFalse(payload["publication"]["leaderboard_ready"])
        self.assertTrue(
            any("pending blinded review" in item for item in payload["publication"]["blockers"])
        )
        self.assertTrue(
            any("digest-verified" in item for item in payload["publication"]["blockers"])
        )

        dashboard = self.runner.dashboard_report(payload)
        self.assertIn("Evidence not ready", dashboard)
        self.assertIn("Public Run Ledger", dashboard)
        self.assertIn("fixture-agent-oom-baseline-t01", dashboard)

    def test_publication_gate_accepts_complete_paired_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            artifact_path = root / "agent-bench" / "artifacts" / "public" / "response.txt"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("Public-safe reviewed response.\n", encoding="utf-8")
            artifact = {
                "path": str(artifact_path.relative_to(root)),
                "description": "Public-safe reviewed response.",
                "sha256": self.runner.sha256_path(artifact_path),
            }
            results = []
            lifts = []
            for agent in ("codex", "claude-code"):
                for condition in ("baseline", "skill-enabled"):
                    for trial in range(1, 4):
                        results.append(
                            {
                                "run_id": f"{agent}-{condition}-t{trial:02d}",
                                "status": "scored",
                                "agent": agent,
                                "harness": f"{agent}-cli",
                                "model": f"{agent}-exact-v1",
                                "evaluation": {
                                    "blinded": True,
                                    "evaluator_ids": ["reviewer-a", "reviewer-b"],
                                },
                                "artifacts": [artifact],
                            }
                        )
                lifts.append(
                    {
                        "agent": agent,
                        "harness": f"{agent}-cli",
                        "model": f"{agent}-exact-v1",
                        "task_id": "public-fixture",
                        "condition": "skill-enabled",
                        "reference_condition": "baseline",
                        "pair_count": 3,
                    }
                )

            readiness = self.runner.publication_readiness(
                {
                    "results": results,
                    "pending_review_count": 0,
                    "skill_lifts": lifts,
                },
                root,
            )
            incomplete_readiness = self.runner.publication_readiness(
                {
                    "results": results,
                    "pending_review_count": 0,
                    "skill_lifts": lifts[:1],
                },
                root,
            )

        self.assertTrue(readiness["leaderboard_ready"], readiness["blockers"])
        self.assertEqual(readiness["scored_agent_variant_count"], 2)
        self.assertEqual(readiness["eligible_comparison_count"], 2)
        self.assertFalse(incomplete_readiness["leaderboard_ready"])
        self.assertTrue(
            any("lack a 3-pair" in item for item in incomplete_readiness["blockers"])
        )

    def test_site_adapter_lift_uses_skill_enabled_reference(self):
        base = {
            "agent": "fixture-agent",
            "harness": "fixture-harness",
            "model": "fixture-model-v1",
            "task_id": "site-adapter-policy-mapping",
            "trial": 1,
        }
        results = [
            {**base, "condition": "baseline", "score": 20.0},
            {**base, "condition": "skill-enabled", "score": 55.0},
            {**base, "condition": "skill-site-adapter", "score": 75.0},
        ]
        lifts = self.runner.build_skill_lifts(results)
        site_lift = next(item for item in lifts if item["condition"] == "skill-site-adapter")
        self.assertEqual(site_lift["reference_condition"], "skill-enabled")
        self.assertEqual(site_lift["reference_score"], 55.0)
        self.assertEqual(site_lift["lift"], 20.0)

    def test_mcp_lift_compares_baseline_and_direct_skill_delivery(self):
        base = {
            "agent": "fixture-agent",
            "harness": "fixture-harness",
            "model": "fixture-model-v1",
            "task_id": "skill-routing-oom-triage",
            "trial": 1,
        }
        results = [
            {**base, "condition": "baseline", "score": 20.0},
            {**base, "condition": "skill-enabled", "score": 70.0},
            {**base, "condition": "mcp-enabled", "score": 75.0},
        ]

        lifts = self.runner.build_skill_lifts(results)
        mcp_lifts = {
            item["reference_condition"]: item
            for item in lifts
            if item["condition"] == "mcp-enabled"
        }

        self.assertEqual(set(mcp_lifts), {"baseline", "skill-enabled"})
        self.assertEqual(mcp_lifts["baseline"]["lift"], 55.0)
        self.assertEqual(mcp_lifts["skill-enabled"]["lift"], 5.0)

    def test_mcp_result_requires_current_contract_provenance(self):
        result = self.result("mcp-enabled", 1, "scored", 0.8)
        result["_path"] = Path(f"{result['run_id']}.json")
        tasks = {self.task["id"]: {**self.task, "_path": self.task_path}}

        valid = self.runner.validate_result(result, tasks)
        result["provenance"]["condition_context"]["mcp_contract_sha256"] = "0" * 64
        tampered = self.runner.validate_result(result, tasks)

        self.assertEqual(valid, [])
        self.assertTrue(any("MCP contract" in error for error in tampered))

    def test_mcp_comparison_gates_remain_closed_until_every_pair_is_complete(self):
        agents = [
            ("codex", "codex-cli", "codex-exact-v1"),
            ("claude-code", "claude-code", "claude-exact-v1"),
        ]
        results = [
            {
                "status": "scored",
                "agent": agent,
                "harness": harness,
                "model": model,
            }
            for agent, harness, model in agents
        ]
        lifts = []
        for agent, harness, model in agents:
            for reference in ("baseline", "skill-enabled"):
                lifts.append(
                    {
                        "agent": agent,
                        "harness": harness,
                        "model": model,
                        "task_id": "skill-routing-oom-triage",
                        "condition": "mcp-enabled",
                        "reference_condition": reference,
                        "pair_count": 3,
                    }
                )
        payload = {
            "tasks": [
                {
                    "id": "skill-routing-oom-triage",
                    "conditions": ["baseline", "skill-enabled", "mcp-enabled"],
                }
            ],
            "results": results,
            "skill_lifts": lifts,
        }

        ready = self.runner.mcp_comparison_gates(payload)
        payload["skill_lifts"] = lifts[:-1]
        incomplete = self.runner.mcp_comparison_gates(payload)

        self.assertTrue(all(gate["ready"] for gate in ready))
        self.assertTrue(any(not gate["ready"] for gate in incomplete))


class AgentBenchmarkHarnessTests(unittest.TestCase):
    def setUp(self):
        self.harness = load_tool("agent_benchmark_harness")
        self.payload = self.harness.plan_payload()
        self.smoke_payload = self.harness.plan_payload(
            ROOT / "agent-bench" / "plans" / "smoke-v0.3.json"
        )
        self.v0_4_payload = self.harness.plan_payload(
            ROOT / "agent-bench" / "plans" / "evidence-v0.4.json"
        )
        self.v0_5_payload = self.harness.plan_payload(
            ROOT / "agent-bench" / "plans" / "evidence-v0.5.json"
        )

    def test_calibration_matrix_is_balanced(self):
        self.assertTrue(self.payload["ok"], self.payload["validation_errors"])
        self.assertEqual(self.payload["run_count"], 54)
        self.assertEqual(self.payload["agent_counts"], {"claude-code": 27, "codex": 27})
        self.assertEqual(
            self.payload["condition_counts"],
            {"baseline": 18, "docs-only": 18, "skill-enabled": 18},
        )
        self.assertEqual(len({run["run_id"] for run in self.payload["runs"]}), 54)

    def test_smoke_matrix_is_balanced_and_bounded(self):
        self.assertTrue(
            self.smoke_payload["ok"], self.smoke_payload["validation_errors"]
        )
        self.assertEqual(self.smoke_payload["run_count"], 6)
        self.assertEqual(
            self.smoke_payload["agent_counts"], {"claude-code": 3, "codex": 3}
        )
        self.assertEqual(
            self.smoke_payload["condition_counts"],
            {"baseline": 2, "docs-only": 2, "skill-enabled": 2},
        )
        self.assertEqual(self.smoke_payload["task_counts"], {"skill-routing-oom-triage": 6})
        self.assertEqual(
            self.smoke_payload["plan"]["execution"]["max_budget_usd_per_run"], 0.5
        )

    def test_v0_4_evidence_matrix_is_balanced_and_budgeted(self):
        self.assertTrue(
            self.v0_4_payload["ok"], self.v0_4_payload["validation_errors"]
        )
        self.assertEqual(self.v0_4_payload["run_count"], 54)
        self.assertEqual(
            self.v0_4_payload["agent_counts"], {"claude-code": 27, "codex": 27}
        )
        self.assertEqual(
            self.v0_4_payload["condition_counts"],
            {"baseline": 18, "docs-only": 18, "skill-enabled": 18},
        )
        execution = self.v0_4_payload["plan"]["execution"]
        self.assertEqual(execution["max_budget_usd_per_run"], 0.75)
        self.assertEqual(execution["max_total_budget_usd"], 40.5)
        self.assertTrue(execution["require_paid_run_acknowledgement"])

    def test_v0_5_evidence_matrix_adds_balanced_mcp_condition(self):
        self.assertTrue(
            self.v0_5_payload["ok"], self.v0_5_payload["validation_errors"]
        )
        self.assertEqual(self.v0_5_payload["run_count"], 72)
        self.assertEqual(
            self.v0_5_payload["agent_counts"], {"claude-code": 36, "codex": 36}
        )
        self.assertEqual(
            self.v0_5_payload["condition_counts"],
            {
                "baseline": 18,
                "docs-only": 18,
                "mcp-enabled": 18,
                "skill-enabled": 18,
            },
        )
        self.assertEqual(
            self.v0_5_payload["plan"]["execution"]["max_total_budget_usd"], 54.0
        )
        mcp_runs = [
            run for run in self.v0_5_payload["runs"] if run["condition"] == "mcp-enabled"
        ]
        self.assertEqual(len(mcp_runs), 18)
        self.assertTrue(all("condition_context" in run for run in mcp_runs))

    def test_total_budget_requires_paid_run_acknowledgement(self):
        plan_path = ROOT / "agent-bench" / "plans" / "evidence-v0.4.json"
        plan = self.harness.load_json(plan_path)
        plan["execution"].pop("require_paid_run_acknowledgement")

        errors = self.harness.validate_plan(plan, self.harness.load_tasks())

        self.assertIn(
            "plan with max_total_budget_usd must require paid-run acknowledgement",
            errors,
        )

    def test_campaign_budget_blocks_a_run_above_total_ceiling(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_root = Path(tmpdir)
            result_dir = output_root / "results"
            result_dir.mkdir()
            (result_dir / "spent.json").write_text(
                json.dumps({"metrics": {"cost_usd": 40.0}}), encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "campaign budget exhausted"):
                self.harness.enforce_campaign_budget(
                    self.v0_4_payload["plan"], output_root
                )

            (result_dir / "spent.json").write_text(
                json.dumps({"metrics": {"cost_usd": 39.75}}), encoding="utf-8"
            )
            self.harness.enforce_campaign_budget(self.v0_4_payload["plan"], output_root)

    def test_preflight_requires_installed_agents_and_exact_models(self):
        with mock.patch.object(self.harness.shutil, "which", return_value=None):
            preflight = self.harness.preflight_payload(self.smoke_payload)

        self.assertFalse(preflight["ok"])
        self.assertEqual(len(preflight["variants"]), 2)
        self.assertTrue(any("exact model id" in item for item in preflight["blockers"]))
        self.assertTrue(any("not installed" in item for item in preflight["blockers"]))

    def test_preflight_accepts_variant_model_overrides(self):
        overrides = {
            "codex-smoke": "codex-exact-model",
            "claude-smoke": "claude-exact-model",
        }
        with mock.patch.object(
            self.harness.shutil, "which", side_effect=lambda executable: f"/bin/{executable}"
        ), mock.patch.object(
            self.harness, "command_version", side_effect=lambda executable: f"{executable} 1.0"
        ), mock.patch.object(
            self.harness, "repository_state", return_value=("a" * 40, False)
        ):
            preflight = self.harness.preflight_payload(self.smoke_payload, overrides)

        self.assertTrue(preflight["ok"], preflight["blockers"])
        self.assertTrue(all(item["ready"] for item in preflight["variants"]))
        budget_modes = {
            item["harness"]: item["budget_enforcement"]
            for item in preflight["variants"]
        }
        self.assertEqual(budget_modes["claude-code"], "provider-cli-hard-limit")
        self.assertEqual(budget_modes["codex-cli"], "external-monitoring-required")

    def test_v0_5_preflight_requires_passing_mcp_runtime(self):
        overrides = {
            "codex-v0-5": "codex-exact-model",
            "claude-v0-5": "claude-exact-model",
        }
        blocked_mcp = {"ready": False, "issues": ["MCP doctor did not pass"]}
        ready_mcp = {
            **self.harness.mcp_condition_context("0.5.0"),
            "ready": True,
            "issues": [],
            "doctor_status": "pass",
        }
        version_mismatch_mcp = {
            **self.harness.mcp_condition_context("0.4.0"),
            "ready": True,
            "issues": [],
            "doctor_status": "pass",
        }
        with mock.patch.object(
            self.harness.shutil,
            "which",
            side_effect=lambda executable: f"/bin/{executable}",
        ), mock.patch.object(
            self.harness, "command_version", return_value="agent 1.0"
        ), mock.patch.object(
            self.harness, "repository_state", return_value=("a" * 40, False)
        ), mock.patch.object(
            self.harness, "mcp_runtime_preflight", return_value=blocked_mcp
        ) as mcp_probe:
            blocked = self.harness.preflight_payload(self.v0_5_payload, overrides)
            mcp_probe.return_value = version_mismatch_mcp
            version_mismatch = self.harness.preflight_payload(
                self.v0_5_payload, overrides
            )
            mcp_probe.return_value = ready_mcp
            ready = self.harness.preflight_payload(self.v0_5_payload, overrides)

        self.assertFalse(blocked["ok"])
        self.assertTrue(any("mcp-enabled" in item for item in blocked["blockers"]))
        self.assertFalse(version_mismatch["ok"])
        self.assertTrue(
            any("plan version 0.5.0" in item for item in version_mismatch["blockers"])
        )
        self.assertTrue(ready["ok"], ready["blockers"])
        self.assertEqual(ready["mcp"]["mcp_package_version"], "0.5.0")

    def test_preflight_blocks_dirty_repository_evidence(self):
        overrides = {
            "codex-smoke": "codex-exact-model",
            "claude-smoke": "claude-exact-model",
        }
        with mock.patch.object(
            self.harness.shutil, "which", side_effect=lambda executable: f"/bin/{executable}"
        ), mock.patch.object(
            self.harness, "command_version", return_value="agent 1.0"
        ), mock.patch.object(
            self.harness, "repository_state", return_value=("a" * 40, True)
        ):
            preflight = self.harness.preflight_payload(self.smoke_payload, overrides)

        self.assertFalse(preflight["ok"])
        self.assertTrue(any("worktree is dirty" in item for item in preflight["blockers"]))

    def test_campaign_status_is_resumable_and_checks_result_identity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result_dir = Path(tmpdir) / "private-results"
            imported_dir = Path(tmpdir) / "imported-results"
            result_dir.mkdir()
            imported_dir.mkdir()
            initial = self.harness.campaign_status(
                self.smoke_payload, [result_dir, imported_dir]
            )
            first = self.smoke_payload["runs"][0]
            result = {
                "run_id": first["run_id"],
                "task_id": first["task_id"],
                "task_version": first["task_version"],
                "trial": first["trial"],
                "agent": first["agent"],
                "harness": first["harness"],
                "model": "exact-model-id",
                "condition": first["condition"],
                "status": "pending-review",
            }
            result_path = result_dir / f"{first['run_id']}.json"
            result_path.write_text(json.dumps(result), encoding="utf-8")
            resumed = self.harness.campaign_status(
                self.smoke_payload, [result_dir, imported_dir]
            )

            self.assertEqual(initial["state_counts"], {"planned": 6})
            self.assertEqual(initial["next_run_id"], first["run_id"])
            self.assertEqual(
                resumed["state_counts"], {"pending-review": 1, "planned": 5}
            )
            self.assertEqual(
                resumed["next_run_id"], self.smoke_payload["runs"][1]["run_id"]
            )
            self.assertEqual(resumed["recorded_cost_usd"], 0.0)
            self.assertIsNone(resumed["max_total_budget_usd"])

            duplicate = imported_dir / result_path.name
            duplicate.write_text(json.dumps(result), encoding="utf-8")
            invalid = self.harness.campaign_status(
                self.smoke_payload, [result_dir, imported_dir]
            )
            self.assertFalse(invalid["ok"])
            self.assertEqual(invalid["state_counts"]["invalid"], 1)

    def test_campaign_status_rejects_configured_default_result_model(self):
        run = self.smoke_payload["runs"][0]
        result = {
            "run_id": run["run_id"],
            "task_id": run["task_id"],
            "task_version": run["task_version"],
            "trial": run["trial"],
            "agent": run["agent"],
            "harness": run["harness"],
            "model": "configured-default",
            "condition": run["condition"],
            "status": "pending-review",
        }

        errors = self.harness.result_identity_errors(run, result)

        self.assertIn("result must record an exact model id", errors)

    def test_timeout_output_bytes_are_decoded_for_artifacts(self):
        self.assertEqual(self.harness.decoded_text(b"partial output\xff"), "partial output�")

    def test_materialize_all_smoke_contexts_preserves_condition_isolation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspaces = self.harness.materialize_all_runs(
                self.smoke_payload, Path(tmpdir)
            )

            self.assertEqual(len(workspaces), 6)
            for item in workspaces:
                workspace = Path(item["workspace"])
                run = next(
                    run
                    for run in self.smoke_payload["runs"]
                    if run["run_id"] == item["run_id"]
                )
                if run["condition"] == "baseline":
                    self.assertFalse((workspace / "AGENTS.md").exists())
                    self.assertFalse((workspace / "skills").exists())
                elif run["condition"] == "docs-only":
                    self.assertTrue((workspace / "AGENTS.md").exists())
                    self.assertFalse((workspace / "skills").exists())
                else:
                    self.assertTrue((workspace / "AGENTS.md").exists())
                    self.assertTrue(
                        (workspace / "skills" / "slurm-oom-memory-triage").exists()
                    )

    def test_materialized_contexts_do_not_leak_skills_into_baseline(self):
        baseline_id = (
            "calibration-v0-2-codex-current-skill-routing-oom-triage-baseline-t01"
        )
        skill_id = (
            "calibration-v0-2-codex-current-skill-routing-oom-triage-skill-enabled-t01"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _, baseline = self.harness.materialize_run(self.payload, baseline_id, root)
            self.assertTrue(
                (baseline / "benchmarks" / "fixtures" / "slurm" / "oom-sacct.txt").exists()
            )
            self.assertFalse((baseline / "AGENTS.md").exists())
            self.assertFalse((baseline / "skills").exists())
            self.assertFalse((baseline / ".agents").exists())

            _, enabled = self.harness.materialize_run(self.payload, skill_id, root)
            self.assertTrue((enabled / "AGENTS.md").exists())
            self.assertTrue((enabled / ".agents" / "skills" / "hpc-skill-hub").exists())
            self.assertTrue((enabled / "skills" / "slurm-oom-memory-triage").exists())
            self.assertTrue((enabled / "registry" / "index.json").exists())

    def test_mcp_contexts_use_only_fixtures_and_provider_config(self):
        codex_run = next(
            run
            for run in self.v0_5_payload["runs"]
            if run["condition"] == "mcp-enabled"
            and run["harness"] == "codex-cli"
            and run["task_id"] == "skill-routing-oom-triage"
        )
        claude_run = next(
            run
            for run in self.v0_5_payload["runs"]
            if run["condition"] == "mcp-enabled"
            and run["harness"] == "claude-code"
            and run["task_id"] == "skill-routing-oom-triage"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _, codex_workspace = self.harness.materialize_run(
                self.v0_5_payload, codex_run["run_id"], root
            )
            _, claude_workspace = self.harness.materialize_run(
                self.v0_5_payload, claude_run["run_id"], root
            )

            for workspace in (codex_workspace, claude_workspace):
                self.assertFalse((workspace / "AGENTS.md").exists())
                self.assertFalse((workspace / "skills").exists())
                self.assertFalse((workspace / "registry").exists())
                self.assertTrue(
                    (workspace / "benchmarks" / "fixtures" / "slurm" / "oom-sacct.txt").exists()
                )
                self.assertIn(
                    "read-only HPC Skill Hub MCP server",
                    (workspace / "BENCHMARK_TASK.md").read_text(encoding="utf-8"),
                )
            self.assertFalse((codex_workspace / ".mcp.json").exists())
            self.assertTrue((claude_workspace / ".mcp.json").exists())

            codex_command = self.harness.build_command(
                codex_run,
                codex_workspace,
                "codex-exact-v1",
                root / "codex-output.txt",
                self.v0_5_payload["plan"],
            )
            claude_command = self.harness.build_command(
                claude_run,
                claude_workspace,
                "claude-exact-v1",
                root / "claude-output.txt",
                self.v0_5_payload["plan"],
            )

        self.assertTrue(
            any("mcp_servers.hpc-skill-hub.required=true" in item for item in codex_command)
        )
        self.assertIn("--mcp-config", claude_command)
        self.assertIn("mcp__hpc-skill-hub__*", claude_command)
        self.assertNotIn("--disallowedTools", claude_command)

    def test_site_adapter_fixture_is_condition_scoped(self):
        task = self.harness.load_tasks()["site-adapter-policy-mapping"]
        baseline = {
            "condition": "baseline",
            "harness": "codex-cli",
        }
        site_enabled = {
            "condition": "skill-site-adapter",
            "harness": "codex-cli",
        }
        baseline_paths = {path.relative_to(ROOT) for path in self.harness.support_paths(task, baseline)}
        site_paths = {path.relative_to(ROOT) for path in self.harness.support_paths(task, site_enabled)}
        adapter_path = Path("site-adapters/example-campus-cluster/site.json")
        self.assertNotIn(adapter_path, baseline_paths)
        self.assertIn(adapter_path, site_paths)


if __name__ == "__main__":
    unittest.main()
