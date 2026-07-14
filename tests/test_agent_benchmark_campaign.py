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


class AgentBenchmarkCampaignTests(unittest.TestCase):
    def setUp(self):
        self.campaign = load_tool("agent_benchmark_campaign")
        self.plan_path = ROOT / "agent-bench" / "plans" / "evidence-v0.4.json"
        self.payload = self.campaign.harness.plan_payload(self.plan_path)
        variants = []
        for variant in self.payload["plan"]["variants"]:
            variants.append(
                {
                    "id": variant["id"],
                    "agent": variant["agent"],
                    "harness": variant["harness"],
                    "model": f"{variant['agent']}-exact-v1",
                    "agent_version": f"{variant['agent']} 1.0.0",
                    "budget_enforcement": self.campaign.budget_mode(
                        variant["harness"]
                    ),
                    "ready": True,
                    "issues": [],
                }
            )
        self.preflight = {
            "ok": True,
            "plan_id": self.payload["plan"]["id"],
            "run_count": self.payload["run_count"],
            "repository_commit": "b" * 40,
            "repository_dirty": False,
            "variants": variants,
            "blockers": [],
        }
        self.manifest = self.campaign.build_manifest(
            self.payload,
            self.plan_path,
            self.preflight,
            seed=20260713,
            created_at="2026-07-13T18:00:00Z",
        )

    def expected_variant(self, run, manifest=None):
        manifest = manifest or self.manifest
        return next(
            item
            for item in manifest["variants"]
            if item["id"] == run["variant_id"]
        )

    def write_scored_result(self, staging_root, run, manifest=None):
        manifest = manifest or self.manifest
        artifact_path = (
            staging_root / "artifacts" / run["run_id"] / "final-output.txt"
        )
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text("Public-safe reviewed response.\n", encoding="utf-8")
        task = self.campaign.harness.load_tasks()[run["task_id"]]
        variant = self.expected_variant(run, manifest)
        result = {
            "$schema": "../../schemas/agent-benchmark-result.schema.json",
            "run_id": run["run_id"],
            "task_id": run["task_id"],
            "task_version": run["task_version"],
            "trial": run["trial"],
            "agent": run["agent"],
            "harness": run["harness"],
            "model": variant["model"],
            "condition": run["condition"],
            "started_at": "2026-07-13T18:00:00Z",
            "completed_at": "2026-07-13T18:01:00Z",
            "status": "scored",
            "provenance": {
                "repository_commit": manifest["repository"]["commit"],
                "repository_dirty": False,
                "skill_snapshot": manifest["repository"]["commit"],
                "task_sha256": manifest["task_sha256"][run["task_id"]],
                "agent_version": variant["agent_version"],
                "harness_version": self.campaign.harness.HARNESS_VERSION,
                "invocation_mode": "cli",
                "model_parameters": run["model_parameters"],
                "network_access": run["network_access"],
                "workspace_mode": run["workspace_mode"],
            },
            "metrics": {
                "wall_time_seconds": 60.0,
                "input_tokens": 100,
                "output_tokens": 50,
                "cost_usd": 0.01,
            },
            "criteria_scores": [
                {"criterion_id": criterion["id"], "score": 0.8}
                for criterion in task["rubric"]
            ],
            "evaluation": {
                "rubric_version": task["version"],
                "evaluator_type": "human",
                "evaluator_ids": ["reviewer-a", "reviewer-b"],
                "blinded": True,
                "scored_at": "2026-07-13T19:00:00Z",
            },
            "failure": None,
            "artifacts": [
                {
                    "path": (
                        f"agent-bench/artifacts/{run['run_id']}/final-output.txt"
                    ),
                    "description": "Redacted final response used for scoring.",
                    "sha256": self.campaign.harness.sha256_path(artifact_path),
                }
            ],
            "notes": "Finalized from independent blinded review.",
        }
        if run["condition"] == self.campaign.harness.MCP_CONDITION:
            result["provenance"]["condition_context"] = dict(
                manifest["mcp_contract"]
            )
        result_path = staging_root / "results" / f"{run['run_id']}.json"
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return result_path, artifact_path

    def test_manifest_has_reproducible_balanced_waves(self):
        errors, payload = self.campaign.validate_campaign(self.manifest)

        self.assertEqual(errors, [])
        self.assertIsNotNone(payload)
        self.assertEqual(self.manifest["schedule"]["run_count"], 54)
        self.assertEqual(self.manifest["schedule"]["wave_count"], 9)
        self.assertTrue(
            all(len(wave["run_ids"]) == 6 for wave in self.manifest["schedule"]["waves"])
        )
        run_ids = [
            run_id
            for wave in self.manifest["schedule"]["waves"]
            for run_id in wave["run_ids"]
        ]
        self.assertEqual(len(run_ids), len(set(run_ids)))
        self.assertEqual(set(run_ids), {run["run_id"] for run in self.payload["runs"]})

        repeated = self.campaign.build_schedule(self.payload, 20260713)
        changed = self.campaign.build_schedule(self.payload, 20260714)
        self.assertEqual(repeated, self.manifest["schedule"])
        self.assertNotEqual(changed["waves"], repeated["waves"])

    def test_legacy_v0_4_campaign_lock_remains_readable(self):
        legacy = json.loads(json.dumps(self.manifest))
        legacy["schema_version"] = "0.1.0"
        legacy.pop("mcp_contract")

        errors, payload = self.campaign.validate_campaign(legacy)

        self.assertEqual(errors, [])
        self.assertIsNotNone(payload)

    def test_v0_5_manifest_locks_mcp_runtime_and_audit_rejects_tampering(self):
        plan_path = ROOT / "agent-bench" / "plans" / "evidence-v0.5.json"
        payload = self.campaign.harness.plan_payload(plan_path)
        variants = []
        for variant in payload["plan"]["variants"]:
            variants.append(
                {
                    "id": variant["id"],
                    "agent": variant["agent"],
                    "harness": variant["harness"],
                    "model": f"{variant['agent']}-exact-v1",
                    "agent_version": f"{variant['agent']} 1.0.0",
                    "budget_enforcement": self.campaign.budget_mode(
                        variant["harness"]
                    ),
                    "ready": True,
                    "issues": [],
                }
            )
        preflight = {
            "ok": True,
            "plan_id": payload["plan"]["id"],
            "run_count": payload["run_count"],
            "repository_commit": "c" * 40,
            "repository_dirty": False,
            "variants": variants,
            "mcp": {
                **self.campaign.harness.mcp_condition_context("0.5.0"),
                "ready": True,
                "issues": [],
            },
            "blockers": [],
        }
        manifest = self.campaign.build_manifest(
            payload,
            plan_path,
            preflight,
            seed=20260714,
            created_at="2026-07-14T18:00:00Z",
        )
        mcp_run = next(
            run
            for run in payload["runs"]
            if run["condition"] == self.campaign.harness.MCP_CONDITION
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            staging_root = Path(tmpdir)
            result_path, _ = self.write_scored_result(
                staging_root, mcp_run, manifest
            )
            ready = self.campaign.audit_staging(
                manifest, staging_root, allow_partial=True
            )
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["provenance"]["condition_context"]["mcp_contract_sha256"] = (
                "0" * 64
            )
            result_path.write_text(json.dumps(result), encoding="utf-8")
            tampered = self.campaign.audit_staging(
                manifest, staging_root, allow_partial=True
            )

        self.assertEqual(manifest["schema_version"], "0.2.0")
        self.assertEqual(manifest["schedule"]["run_count"], 72)
        self.assertEqual(manifest["schedule"]["wave_count"], 9)
        self.assertTrue(
            all(len(wave["run_ids"]) == 8 for wave in manifest["schedule"]["waves"])
        )
        self.assertEqual(manifest["mcp_contract"]["mcp_package_version"], "0.5.0")
        self.assertTrue(ready["ready_for_import"], ready["errors"])
        self.assertFalse(tampered["ready_for_import"])
        self.assertTrue(any("MCP result" in item for item in tampered["errors"]))

    def test_prepare_writes_lock_without_launching_agents(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "campaign.json"
            with mock.patch.object(
                self.campaign.harness,
                "preflight_payload",
                return_value=self.preflight,
            ):
                prepared = self.campaign.prepare_campaign(
                    self.plan_path,
                    {
                        "codex-v0-4": "codex-exact-v1",
                        "claude-v0-4": "claude-code-exact-v1",
                    },
                    20260713,
                    output_path,
                    acknowledge_paid_quota=True,
                )

            lock = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertTrue(prepared["ok"])
            self.assertEqual(lock["schedule"]["run_count"], 54)
            self.assertTrue(lock["budget"]["paid_quota_acknowledged"])

    def test_status_returns_only_the_next_balanced_wave(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            imported = root / "imported"
            imported.mkdir()
            with mock.patch.object(
                self.campaign, "runtime_environment_errors", return_value=[]
            ):
                status = self.campaign.campaign_status(self.manifest, root, imported)

        self.assertTrue(status["ok"], status.get("errors"))
        self.assertEqual(status["state_counts"], {"planned": 54})
        self.assertEqual(status["next_wave"], "wave-01")
        self.assertEqual(len(status["next_wave_commands"]), 6)
        for command in status["next_wave_commands"]:
            self.assertIn("--allow-paid-run", command["argv"])
            self.assertNotIn("configured-default", command["argv"])

    def test_status_blocks_result_that_does_not_match_campaign_lock(self):
        first_run_id = self.manifest["schedule"]["waves"][0]["run_ids"][0]
        run = next(run for run in self.payload["runs"] if run["run_id"] == first_run_id)
        variant = self.expected_variant(run)
        result = {
            "run_id": run["run_id"],
            "task_id": run["task_id"],
            "task_version": run["task_version"],
            "trial": run["trial"],
            "agent": run["agent"],
            "harness": run["harness"],
            "model": "wrong-exact-model",
            "condition": run["condition"],
            "status": "pending-review",
            "provenance": {
                "repository_commit": self.manifest["repository"]["commit"],
                "agent_version": variant["agent_version"],
            },
            "metrics": {"cost_usd": 0.01},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result_dir = root / "results"
            result_dir.mkdir()
            imported = root / "imported"
            imported.mkdir()
            (result_dir / f"{run['run_id']}.json").write_text(
                json.dumps(result), encoding="utf-8"
            )
            with mock.patch.object(
                self.campaign, "runtime_environment_errors", return_value=[]
            ):
                status = self.campaign.campaign_status(self.manifest, root, imported)

        self.assertFalse(status["ok"])
        self.assertEqual(status["state_counts"]["invalid"], 1)
        self.assertEqual(status["next_wave_commands"], [])

    def test_status_withholds_commands_when_budget_cannot_cover_next_run(self):
        first_run_id = self.manifest["schedule"]["waves"][0]["run_ids"][0]
        run = next(run for run in self.payload["runs"] if run["run_id"] == first_run_id)
        variant = self.expected_variant(run)
        result = {
            "run_id": run["run_id"],
            "task_id": run["task_id"],
            "task_version": run["task_version"],
            "trial": run["trial"],
            "agent": run["agent"],
            "harness": run["harness"],
            "model": variant["model"],
            "condition": run["condition"],
            "status": "pending-review",
            "provenance": {
                "repository_commit": self.manifest["repository"]["commit"],
                "agent_version": variant["agent_version"],
            },
            "metrics": {"cost_usd": 40.0},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            result_dir = root / "results"
            result_dir.mkdir()
            imported = root / "imported"
            imported.mkdir()
            (result_dir / f"{run['run_id']}.json").write_text(
                json.dumps(result), encoding="utf-8"
            )
            with mock.patch.object(
                self.campaign, "runtime_environment_errors", return_value=[]
            ):
                status = self.campaign.campaign_status(self.manifest, root, imported)

        self.assertFalse(status["ok"])
        self.assertFalse(status["budget_can_run"])
        self.assertEqual(status["remaining_budget_usd"], 0.5)
        self.assertEqual(status["next_wave_commands"], [])
        self.assertTrue(any("budget" in item for item in status["errors"]))

    def test_runtime_environment_must_still_match_campaign_lock(self):
        versions = {
            "codex": "codex 1.0.0",
            "claude": "claude-code 1.0.0",
        }
        with mock.patch.object(
            self.campaign.harness,
            "repository_state",
            return_value=(self.manifest["repository"]["commit"], False),
        ), mock.patch.object(
            self.campaign.harness.shutil,
            "which",
            side_effect=lambda executable: f"/bin/{executable}",
        ), mock.patch.object(
            self.campaign.harness,
            "command_version",
            side_effect=lambda executable: versions[executable],
        ):
            ready = self.campaign.runtime_environment_errors(self.manifest)
            versions["codex"] = "codex 2.0.0"
            changed = self.campaign.runtime_environment_errors(self.manifest)

        self.assertEqual(ready, [])
        self.assertTrue(any("codex version" in item for item in changed))

    def test_staging_audit_allows_reviewed_partial_bundle_only_when_explicit(self):
        run = self.payload["runs"][0]
        with tempfile.TemporaryDirectory() as tmpdir:
            staging_root = Path(tmpdir)
            _, artifact_path = self.write_scored_result(staging_root, run)

            blocked = self.campaign.audit_staging(self.manifest, staging_root)
            partial = self.campaign.audit_staging(
                self.manifest, staging_root, allow_partial=True
            )
            review_security = {
                "summary": {
                    "blocking_count": 0,
                    "finding_count": 1,
                    "verdict": "review",
                }
            }
            with mock.patch.object(
                self.campaign, "scan_target", return_value=review_security
            ):
                security_blocked = self.campaign.audit_staging(
                    self.manifest, staging_root, allow_partial=True
                )
                security_acknowledged = self.campaign.audit_staging(
                    self.manifest,
                    staging_root,
                    allow_partial=True,
                    security_reviewer="security-reviewer-a",
                )
            artifact_path.write_text("Tampered response.\n", encoding="utf-8")
            tampered = self.campaign.audit_staging(
                self.manifest, staging_root, allow_partial=True
            )

        self.assertFalse(blocked["ready_for_import"])
        self.assertTrue(any("missing 53" in item for item in blocked["errors"]))
        self.assertTrue(partial["ready_for_import"], partial["errors"])
        self.assertFalse(partial["complete_campaign"])
        self.assertTrue(any("missing 53" in item for item in partial["warnings"]))
        self.assertFalse(security_blocked["ready_for_import"])
        self.assertTrue(security_acknowledged["ready_for_import"])
        self.assertEqual(
            security_acknowledged["security_reviewer"], "security-reviewer-a"
        )
        self.assertFalse(tampered["ready_for_import"])
        self.assertTrue(any("digest" in item for item in tampered["errors"]))


if __name__ == "__main__":
    unittest.main()
