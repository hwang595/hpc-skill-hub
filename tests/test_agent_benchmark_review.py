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


class BlindedReviewTests(unittest.TestCase):
    def setUp(self):
        self.review = load_tool("agent_benchmark_review")
        self.plan_path = ROOT / "agent-bench" / "plans" / "smoke-v0.3.json"
        self.plan = self.review.load_plan(self.plan_path)
        self.run = self.plan["runs"][0]
        self.task = self.review.harness.load_tasks()[self.run["task_id"]]
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.run_root = self.root / "private-run"
        self.packet_root = self.root / "packet"
        self.mapping_path = self.root / "private" / "mapping.json"
        self.salt_path = self.root / "private" / "salt.bin"
        self.reviews_dir = self.root / "reviews"
        self.reconciliations_dir = self.root / "reconciliations"
        self.output_root = self.root / "staged-public"
        self.salt_path.parent.mkdir(parents=True)
        self.salt_path.write_bytes(b"deterministic-test-salt-32-bytes")
        self.response = (
            "The synthetic record reports OUT_OF_MEMORY. Compare ReqMem and MaxRSS, "
            "inspect the batch and extern steps, and review the application log before "
            "changing resources. Source: slurm-oom-memory-triage v0.1.0.\n"
        )
        self._write_pending_result(self.response)

    def _write_pending_result(self, response):
        run_id = self.run["run_id"]
        output_path = self.run_root / "artifacts" / run_id / "final-output.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(response, encoding="utf-8")
        result = {
            "$schema": self.review.benchmark_runner.RESULT_SCHEMA,
            "run_id": run_id,
            "task_id": self.run["task_id"],
            "task_version": self.run["task_version"],
            "trial": self.run["trial"],
            "agent": self.run["agent"],
            "harness": self.run["harness"],
            "model": "codex-test-model-exact",
            "condition": self.run["condition"],
            "started_at": "2026-07-10T18:00:00Z",
            "completed_at": "2026-07-10T18:01:00Z",
            "status": "pending-review",
            "provenance": {
                "repository_commit": "a" * 40,
                "repository_dirty": False,
                "skill_snapshot": "a" * 40,
                "task_sha256": self.review.sha256_path(self.task["_path"]),
                "agent_version": "codex-cli 1.0.0",
                "harness_version": self.review.harness.HARNESS_VERSION,
                "invocation_mode": "cli",
                "model_parameters": {},
                "network_access": False,
                "workspace_mode": self.run["workspace_mode"],
            },
            "metrics": {
                "wall_time_seconds": 60,
                "input_tokens": 100,
                "output_tokens": 80,
                "cost_usd": 0.01,
            },
            "criteria_scores": [],
            "evaluation": None,
            "failure": None,
            "artifacts": [
                {
                    "path": f"agent-bench/artifacts/{run_id}/final-output.txt",
                    "description": "Final agent response.",
                    "sha256": self.review.sha256_path(output_path),
                }
            ],
            "notes": "Synthetic pending result for blinded review tests.",
        }
        result_path = self.run_root / "results" / f"{run_id}.json"
        self.review.write_json(result_path, result)
        return result_path

    def _prepare(self, packet_root=None, mapping_path=None):
        packet_root = packet_root or self.packet_root
        mapping_path = mapping_path or self.mapping_path
        return self.review.prepare_packet(
            self.plan_path,
            self.run_root,
            packet_root,
            mapping_path,
            self.salt_path,
            "redactor-a",
        )

    def _case(self):
        return self.review.load_json(self.packet_root / "manifest.json")["cases"][0]

    def _score_items(self, score):
        if isinstance(score, dict):
            values = score
        else:
            values = {item["id"]: score for item in self.task["rubric"]}
        return [
            {
                "criterion_id": item["id"],
                "score": values[item["id"]],
                "rationale": f"Evidence supports {item['id']}.",
            }
            for item in self.task["rubric"]
        ]

    def _write_review(self, reviewer_id, score, blind_id=None, submitted_at=None):
        case = self._case()
        payload = {
            "$schema": self.review.REVIEW_SCHEMA,
            "blind_id": blind_id or case["blind_id"],
            "task_id": case["task_id"],
            "task_version": case["task_version"],
            "reviewer_id": reviewer_id,
            "reviewer_type": "human",
            "submitted_at": submitted_at or "2026-07-10T19:00:00Z",
            "scores": self._score_items(score),
            "notes": "Independent synthetic review.",
        }
        path = self.reviews_dir / reviewer_id / f"{payload['blind_id']}.json"
        self.review.write_json(path, payload)
        return path

    def _write_reconciliation(self, score):
        case = self._case()
        payload = {
            "$schema": self.review.RECONCILIATION_SCHEMA,
            "blind_id": case["blind_id"],
            "task_id": case["task_id"],
            "task_version": case["task_version"],
            "reviewer_ids": ["reviewer-a", "reviewer-b"],
            "reconciled_by": "adjudicator-a",
            "reconciled_at": "2026-07-10T20:00:00Z",
            "scores": self._score_items(score),
            "notes": "Resolved criterion differences from the independent reviews.",
        }
        path = self.reconciliations_dir / f"{case['blind_id']}.json"
        self.review.write_json(path, payload)
        return path

    def test_prepare_blinds_private_run_identity_and_is_deterministic(self):
        self._prepare()
        case = self._case()
        packet_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(self.packet_root.rglob("*"))
            if path.is_file()
        )
        for private_value in (
            self.run["run_id"],
            self.run["agent"],
            self.run["harness"],
            self.run["condition"],
            "codex-test-model-exact",
        ):
            self.assertNotIn(private_value, packet_text)

        mapping = self.review.load_json(self.mapping_path)
        self.assertEqual(mapping["cases"][0]["run_id"], self.run["run_id"])
        second_packet = self.root / "packet-two"
        second_mapping = self.root / "private" / "mapping-two.json"
        self._prepare(second_packet, second_mapping)
        second_case = self.review.load_json(second_packet / "manifest.json")["cases"][0]
        self.assertEqual(case["blind_id"], second_case["blind_id"])

    def test_prepare_requires_private_mapping_outside_packet(self):
        with self.assertRaisesRegex(ValueError, "outside the blinded packet"):
            self._prepare(self.packet_root, self.packet_root / "mapping.json")
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            self._prepare(self.packet_root, ROOT / "private-mapping.json")

    def test_prepare_blocks_unredacted_private_network_data(self):
        unsafe_response = "Observed private endpoint " + ".".join(["10", "20", "30", "40"])
        self._write_pending_result(unsafe_response)
        with self.assertRaisesRegex(ValueError, "redaction gate blocked"):
            self._prepare()

    def test_status_requires_exactly_two_independent_reviews(self):
        self._prepare()
        missing, _ = self.review.review_status(
            self.packet_root, self.mapping_path, self.reviews_dir
        )
        self.assertEqual(missing["state_counts"], {"missing-reviews": 1})

        self._write_review("reviewer-a", 0.7)
        one_review, _ = self.review.review_status(
            self.packet_root, self.mapping_path, self.reviews_dir
        )
        self.assertEqual(one_review["state_counts"], {"missing-reviews": 1})

        self._write_review("reviewer-b", 0.8)
        ready, _ = self.review.review_status(
            self.packet_root, self.mapping_path, self.reviews_dir
        )
        self.assertTrue(ready["ready_to_finalize"])

        self._write_review("reviewer-c", 0.75)
        extra, _ = self.review.review_status(
            self.packet_root, self.mapping_path, self.reviews_dir
        )
        self.assertFalse(extra["ok"])
        self.assertEqual(extra["state_counts"], {"invalid": 1})

    def test_status_rejects_unknown_blind_id_and_naive_timestamp(self):
        self._prepare()
        self._write_review("reviewer-a", 0.7)
        self._write_review("reviewer-b", 0.8, submitted_at="2026-07-10T19:00:00")
        unknown_id = "case-" + "f" * 12
        self._write_review("reviewer-x", 0.7, blind_id=unknown_id)
        report, _ = self.review.review_status(
            self.packet_root, self.mapping_path, self.reviews_dir
        )
        self.assertFalse(report["ok"])
        self.assertIn("unknown blind ids", report["errors"][0])
        self.assertEqual(report["state_counts"], {"invalid": 1})

    def test_status_detects_packet_rubric_tampering(self):
        self._prepare()
        rubric_path = self.packet_root / self._case()["rubric_path"]
        rubric_path.write_text(rubric_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        report, _ = self.review.review_status(
            self.packet_root, self.mapping_path, self.reviews_dir
        )
        self.assertFalse(report["ok"])
        self.assertEqual(report["state_counts"], {"invalid": 1})
        self.assertIn("digest mismatch", report["cases"][0]["errors"][0])

    def test_disagreement_threshold_requires_reconciliation(self):
        self._prepare()
        self._write_review("reviewer-a", 0.5)
        self._write_review("reviewer-b", 0.75)
        report, _ = self.review.review_status(
            self.packet_root, self.mapping_path, self.reviews_dir, self.reconciliations_dir
        )
        self.assertEqual(report["state_counts"], {"needs-reconciliation": 1})
        self.assertEqual(len(report["cases"][0]["disagreements"]), len(self.task["rubric"]))

        self._write_reconciliation(0.65)
        reconciled, _ = self.review.review_status(
            self.packet_root, self.mapping_path, self.reviews_dir, self.reconciliations_dir
        )
        self.assertTrue(reconciled["ready_to_finalize"])

    def test_finalize_emits_public_safe_scored_result(self):
        self._prepare()
        self._write_review("reviewer-a", 0.7)
        self._write_review("reviewer-b", 0.8)
        finalized = self.review.finalize_packet(
            self.packet_root,
            self.mapping_path,
            self.reviews_dir,
            None,
            self.output_root,
        )
        self.assertEqual(finalized["finalized_count"], 1)
        result_path = self.output_root / "results" / f"{self.run['run_id']}.json"
        result = self.review.load_json(result_path)
        self.assertEqual(result["status"], "scored")
        self.assertTrue(result["evaluation"]["blinded"])
        self.assertEqual(result["evaluation"]["evaluator_ids"], ["reviewer-a", "reviewer-b"])
        self.assertTrue(all(item["score"] == 0.75 for item in result["criteria_scores"]))
        self.assertEqual(len(result["artifacts"]), 1)
        aggregate = self.review.benchmark_runner.benchmark_payload(
            ROOT / "agent-bench" / "tasks", self.output_root / "results"
        )
        self.assertTrue(aggregate["ok"], aggregate["validation_errors"])
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            self.review.finalize_packet(
                self.packet_root,
                self.mapping_path,
                self.reviews_dir,
                None,
                ROOT / "reviewed-staging",
            )

    def test_finalize_detects_source_and_packet_tampering(self):
        self._prepare()
        self._write_review("reviewer-a", 0.7)
        self._write_review("reviewer-b", 0.8)
        result_path = self.run_root / "results" / f"{self.run['run_id']}.json"
        result_path.write_text(result_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "source result changed"):
            self.review.finalize_packet(
                self.packet_root,
                self.mapping_path,
                self.reviews_dir,
                None,
                self.output_root,
            )

        self._write_pending_result(self.response)
        response_path = self.packet_root / self._case()["response_path"]
        response_path.write_text("Changed after review.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "packet file digest mismatch"):
            self.review.finalize_packet(
                self.packet_root,
                self.mapping_path,
                self.reviews_dir,
                None,
                self.output_root,
                force=True,
            )


if __name__ == "__main__":
    unittest.main()
