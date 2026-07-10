import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


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
        return {
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


class AgentBenchmarkHarnessTests(unittest.TestCase):
    def setUp(self):
        self.harness = load_tool("agent_benchmark_harness")
        self.payload = self.harness.plan_payload()

    def test_calibration_matrix_is_balanced(self):
        self.assertTrue(self.payload["ok"], self.payload["validation_errors"])
        self.assertEqual(self.payload["run_count"], 54)
        self.assertEqual(self.payload["agent_counts"], {"claude-code": 27, "codex": 27})
        self.assertEqual(
            self.payload["condition_counts"],
            {"baseline": 18, "docs-only": 18, "skill-enabled": 18},
        )
        self.assertEqual(len({run["run_id"] for run in self.payload["runs"]}), 54)

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
