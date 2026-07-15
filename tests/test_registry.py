import importlib.util
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_registry_artifact_module():
    spec = importlib.util.spec_from_file_location(
        "validate_registry_artifacts", ROOT / "tools" / "validate_registry_artifacts.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_cmd(*args, cwd=ROOT):
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def run_cmd_no_check(*args, cwd=ROOT):
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_cmd_with_env(*args, cwd=ROOT, env=None):
    merged_env = None
    if env is not None:
        import os

        merged_env = os.environ.copy()
        merged_env.update(env)
    return subprocess.run(
        args,
        cwd=str(cwd),
        env=merged_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class RegistryTests(unittest.TestCase):
    def load_index(self):
        with (ROOT / "registry" / "index.json").open(encoding="utf-8") as handle:
            return json.load(handle)

    def test_validator_passes(self):
        result = run_cmd("python3", "tools/validate_skills.py")
        self.assertIn("Validated", result.stdout)
        self.assertIn("skill(s)", result.stdout)
        self.assertIn("site adapter(s)", result.stdout)
        self.assertIn("collection(s)", result.stdout)

    def test_generated_index_is_current(self):
        result = run_cmd("python3", "tools/build_index.py", "--check")
        self.assertIn("Registry index is current", result.stdout)

    def test_generated_health_is_current(self):
        result = run_cmd("python3", "tools/build_health.py", "--check")
        self.assertIn("Registry health is current", result.stdout)

    def test_generated_compatibility_is_current(self):
        result = run_cmd("python3", "tools/build_compatibility.py", "--check")
        self.assertIn("Compatibility tables are current", result.stdout)

    def test_generated_benchmark_report_is_current(self):
        result = run_cmd("python3", "tools/run_benchmarks.py", "--check")
        self.assertIn("Benchmark report is current", result.stdout)

        json_result = run_cmd("python3", "tools/run_benchmarks.py", "--json")
        payload = json.loads(json_result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["case_count"], 15)
        self.assertEqual(payload["counts"], {"passed": 14, "skipped": 1})
        self.assertEqual(
            payload["mode_counts"],
            {"fixture": 9, "site": 1, "static": 5},
        )

    def test_generated_agent_benchmark_report_is_current(self):
        plan_result = run_cmd("python3", "tools/agent_benchmark_harness.py", "--check")
        self.assertIn("Agent benchmark plan is current", plan_result.stdout)

        plan_json = run_cmd("python3", "tools/agent_benchmark_harness.py", "--json")
        plan_payload = json.loads(plan_json.stdout)
        self.assertTrue(plan_payload["ok"])
        self.assertEqual(plan_payload["run_count"], 54)
        self.assertEqual(plan_payload["agent_counts"], {"claude-code": 27, "codex": 27})

        smoke_result = run_cmd(
            "python3",
            "tools/agent_benchmark_harness.py",
            "--plan",
            "agent-bench/plans/smoke-v0.3.json",
            "--report",
            "docs/AGENT_BENCHMARK_SMOKE_PLAN.md",
            "--check",
        )
        self.assertIn("Agent benchmark plan is current", smoke_result.stdout)

        smoke_json = run_cmd(
            "python3",
            "tools/agent_benchmark_harness.py",
            "--plan",
            "agent-bench/plans/smoke-v0.3.json",
            "--json",
        )
        smoke_payload = json.loads(smoke_json.stdout)
        self.assertTrue(smoke_payload["ok"])
        self.assertEqual(smoke_payload["run_count"], 6)

        v0_5_json = run_cmd(
            "python3",
            "tools/agent_benchmark_harness.py",
            "--plan",
            "agent-bench/plans/evidence-v0.5.json",
            "--json",
        )
        v0_5_payload = json.loads(v0_5_json.stdout)
        self.assertTrue(v0_5_payload["ok"])
        self.assertEqual(v0_5_payload["run_count"], 72)
        self.assertEqual(
            v0_5_payload["condition_counts"],
            {
                "baseline": 18,
                "docs-only": 18,
                "mcp-enabled": 18,
                "skill-enabled": 18,
            },
        )

        result = run_cmd("python3", "tools/run_agent_benchmarks.py", "--check")
        self.assertIn("Agent benchmark report is current", result.stdout)

        json_result = run_cmd("python3", "tools/run_agent_benchmarks.py", "--json")
        payload = json.loads(json_result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["task_count"], 6)
        self.assertEqual(payload["result_count"], 0)
        self.assertEqual(payload["scored_result_count"], 0)
        self.assertEqual(payload["failed_result_count"], 0)
        self.assertEqual(payload["pending_review_count"], 0)
        self.assertEqual(
            payload["task_type_counts"],
            {
                "repo-edit": 1,
                "safety": 2,
                "site-policy": 1,
                "skill-routing": 1,
                "triage": 1,
            },
        )
        self.assertEqual(
            payload["condition_counts"],
            {
                "baseline": 6,
                "docs-only": 6,
                "mcp-enabled": 3,
                "skill-enabled": 6,
                "skill-site-adapter": 1,
            },
        )

    def test_generated_release_status_is_current_and_preserves_external_gates(self):
        result = run_cmd("python3", "tools/build_release_status.py", "--check")
        self.assertIn("Release status is current", result.stdout)

        status = json.loads(
            (ROOT / "registry" / "release-status.json").read_text(encoding="utf-8")
        )
        self.assertEqual(status["release"], "v0.6.0")
        self.assertTrue(status["repository_capability_ready"])
        self.assertFalse(status["external_evidence_ready"])
        self.assertEqual(status["capabilities"]["benchmark"]["planned_run_count"], 72)
        self.assertEqual(status["capabilities"]["benchmark"]["result_count"], 0)
        self.assertFalse(status["capabilities"]["benchmark"]["leaderboard_ready"])
        self.assertEqual(status["capabilities"]["community_pilot"]["case_count"], 9)
        self.assertEqual(status["capabilities"]["community_pilot"]["passed_count"], 9)
        self.assertFalse(
            status["capabilities"]["community_pilot"]["external_evidence_claimed"]
        )
        self.assertEqual(
            status["gates"]["community_intake_pilot"]["status"], "open"
        )
        self.assertEqual(
            status["gates"]["comparative_evidence"]["status"], "closed"
        )
        self.assertEqual(status["gates"]["maturity_promotion"]["status"], "closed")
        self.assertEqual(status["gates"]["release_provenance"]["status"], "pending")
        self.assertTrue(status["gates"]["release_provenance"]["blockers"])

    def test_release_provenance_receipt_is_bound_to_manifest(self):
        receipt = json.loads(
            (ROOT / "registry" / "provenance" / "v0.5.0.json").read_text(
                encoding="utf-8"
            )
        )
        manifest_path = ROOT / "registry" / "releases" / "v0.5.0.json"
        artifacts = {item["kind"]: item for item in receipt["artifacts"]}

        self.assertEqual(receipt["release"], "v0.5.0")
        self.assertEqual(receipt["tag"], "v0.5.0")
        self.assertEqual(
            receipt["commit"], "22be6aef66bd07182ce0d0dd67be72d1c2d21522"
        )
        self.assertEqual(receipt["workflow"]["conclusion"], "success")
        self.assertEqual(receipt["verification"]["status"], "verified")
        self.assertEqual(set(artifacts), {"manifest", "wheel", "sdist"})
        self.assertEqual(
            artifacts["manifest"]["sha256"],
            hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        )
        self.assertTrue(
            all(item["attestation"]["status"] == "verified" for item in artifacts.values())
        )

    def test_generated_package_data_is_current(self):
        result = run_cmd("python3", "tools/build_package_data.py", "--check")
        self.assertIn("Package registry data is current", result.stdout)

    def test_generated_mcp_client_configs_are_current(self):
        result = run_cmd("python3", "tools/build_mcp_client_configs.py", "--check")
        self.assertIn("MCP client configuration examples are current", result.stdout)

    def test_registry_artifact_contracts_pass(self):
        result = run_cmd("python3", "tools/validate_registry_artifacts.py")
        self.assertIn("Validated registry artifacts", result.stdout)

    def test_public_baseline_counts_are_checked(self):
        module = load_registry_artifact_module()
        index = self.load_index()
        errors = []
        module.validate_public_count_mentions(index, errors)
        self.assertEqual(errors, [])

        bad_index = dict(index)
        bad_index["collection_count"] = index["collection_count"] + 1
        bad_index["site_adapter_count"] = index["site_adapter_count"] + 1
        bad_errors = []
        module.PUBLIC_BASELINE_DOCS = [ROOT / "docs" / "PUBLIC_LAUNCH_PACKET.md"]
        module.validate_public_count_mentions(bad_index, bad_errors)
        self.assertTrue(
            any("Curated collections" in error for error in bad_errors),
            bad_errors,
        )
        self.assertTrue(
            any("Site adapters" in error for error in bad_errors),
            bad_errors,
        )

    def test_published_release_snapshots_are_valid(self):
        result = run_cmd(
            "python3",
            "tools/validate_registry_artifacts.py",
            "--release-only",
        )
        self.assertIn("versioned release snapshot", result.stdout)

    def test_review_packet_is_current(self):
        result = run_cmd("python3", "tools/review_packet.py", "--check")
        self.assertIn("Review packet is current", result.stdout)

        json_result = run_cmd(
            "python3",
            "tools/review_packet.py",
            "--json",
            "--limit",
            "5",
        )
        payload = json.loads(json_result.stdout)
        self.assertEqual(payload["target_version"], "v0.2.0")
        self.assertLessEqual(len(payload["candidates"]), 5)
        self.assertTrue(payload["focus_groups"])
        for candidate in payload["candidates"]:
            self.assertEqual(candidate["promotion_target"], "reviewed")
            self.assertIn("issue_title", candidate)
            self.assertIn("suggested_labels", candidate)

        bad_collection = run_cmd_no_check(
            "python3",
            "tools/review_packet.py",
            "--collection",
            "missing-collection",
            "--check",
        )
        self.assertNotEqual(bad_collection.returncode, 0)
        self.assertIn("unknown collection: missing-collection", bad_collection.stderr)

    def test_review_candidates_report(self):
        result = run_cmd("python3", "tools/review_candidates.py", "--limit", "5")
        self.assertIn("# HPC Skill Hub Review Candidates", result.stdout)
        self.assertIn(
            "| Skill | Risk | Categories | Collections | Score | Review Focus |",
            result.stdout,
        )

        json_result = run_cmd(
            "python3",
            "tools/review_candidates.py",
            "--json",
            "--limit",
            "5",
        )
        payload = json.loads(json_result.stdout)
        index = self.load_index()
        seed_count = sum(
            1 for skill in index["skills"] if skill["maturity"] == "seed"
        )

        self.assertEqual(payload["skill_count"], index["skill_count"])
        self.assertEqual(payload["seed_skill_count"], seed_count)
        self.assertLessEqual(len(payload["candidates"]), 5)
        self.assertTrue(payload["candidates"])
        for candidate in payload["candidates"]:
            self.assertEqual(candidate["maturity"], "seed")
            self.assertIn("review_focus", candidate)
            self.assertIn("evidence", candidate)

        collection_result = run_cmd(
            "python3",
            "tools/review_candidates.py",
            "--json",
            "--collection",
            "data-movement",
            "--limit",
            "3",
        )
        collection_payload = json.loads(collection_result.stdout)
        self.assertTrue(collection_payload["candidates"])
        for candidate in collection_payload["candidates"]:
            self.assertIn("data-movement", candidate["collections"])

    def test_v0_2_release_manifest_remains_immutable(self):
        manifest_path = ROOT / "registry" / "releases" / "v0.2.0.json"
        data = manifest_path.read_bytes()
        manifest = json.loads(data)

        self.assertEqual(manifest["version"], "v0.2.0")
        self.assertEqual(hashlib.sha256(data).hexdigest(), "f0569776a186da8b919ecd9df37cd765a1ddcc15f6dae977fbe62611d9656501")
        self.assertEqual(manifest["registry"]["skill_count"], 97)
        self.assertEqual(manifest["registry"]["collection_count"], 12)
        self.assertEqual(manifest["registry"]["site_adapter_count"], 2)
        paths = {entry["path"] for entry in manifest["files"]}
        self.assertIn("registry/index.json", paths)
        self.assertIn("docs/COMPATIBILITY.md", paths)
        self.assertIn("docs/AGENT_BENCHMARK_REPORT.md", paths)
        self.assertIn("docs/AGENT_BENCHMARK_PLAN.md", paths)
        self.assertIn("docs/BENCHMARK_REPORT.md", paths)
        self.assertIn("schemas/agent-benchmark-plan.schema.json", paths)
        self.assertIn("schemas/agent-benchmark-result.schema.json", paths)
        self.assertIn("schemas/agent-benchmark-task.schema.json", paths)
        self.assertIn("schemas/benchmark.schema.json", paths)
        self.assertIn("skills/slurm-submit-job/skill.json", paths)
        self.assertIn("schemas/registry-index.schema.json", paths)
        self.assertIn("schemas/registry-health.schema.json", paths)
        self.assertIn("schemas/release-manifest.schema.json", paths)

    def test_v0_3_release_manifest_remains_immutable(self):
        manifest_path = ROOT / "registry" / "releases" / "v0.3.0.json"
        data = manifest_path.read_bytes()
        manifest = json.loads(data)

        self.assertEqual(manifest["version"], "v0.3.0")
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "783988190fb695f6c8ca0066d129fd0f83d05fbb90bb1a6e89c6687f1a506de6",
        )

    def test_v0_5_release_manifest_remains_immutable(self):
        manifest_path = ROOT / "registry" / "releases" / "v0.5.0.json"
        data = manifest_path.read_bytes()
        manifest = json.loads(data)

        self.assertEqual(manifest["version"], "v0.5.0")
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "4e0703b0490529bf849def3c42c05a54c2aea44065bfefbb186ea74c6841cda3",
        )
        self.assertEqual(manifest["registry"]["skill_count"], 97)

    def test_current_release_manifest_summarizes_registry(self):
        result = run_cmd(
            "python3", "tools/build_release_manifest.py", "v0.6.0", "--check"
        )
        self.assertIn("Release manifest is current", result.stdout)
        manifest_path = ROOT / "registry" / "releases" / "v0.6.0.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["version"], "v0.6.0")
        self.assertEqual(manifest["registry"]["skill_count"], 97)
        self.assertEqual(manifest["registry"]["collection_count"], 12)
        self.assertEqual(manifest["registry"]["site_adapter_count"], 2)
        paths = {entry["path"] for entry in manifest["files"]}
        self.assertIn("registry/skill-quality.json", paths)
        self.assertIn("registry/review-status.json", paths)
        self.assertIn("registry/release-status.json", paths)
        self.assertIn("schemas/release-status.schema.json", paths)
        self.assertIn("docs/V0_6_COMPLETION.md", paths)
        self.assertIn("docs/RELEASE_NOTES_v0.6.0.md", paths)
        self.assertIn("docs/COMMUNITY_PILOT_v0.6.0.md", paths)
        self.assertIn("registry/community-pilot-v0.6.0.json", paths)
        self.assertIn("schemas/community-pilot-report.schema.json", paths)
        self.assertIn("tools/installed_release_smoke.py", paths)
        self.assertIn("agent-bench/plans/evidence-v0.5.json", paths)
        self.assertIn("docs/AGENT_BENCHMARK_DASHBOARD.html", paths)
        self.assertIn("docs/SKILL_REVIEW_DASHBOARD.html", paths)
        self.assertIn("schemas/agent-benchmark-campaign.schema.json", paths)
        self.assertIn("schemas/skill-review.schema.json", paths)
        self.assertIn("schemas/skill-review-status.schema.json", paths)

    def test_repository_release_versions_are_consistent(self):
        manifest = json.loads(
            (ROOT / "registry" / "releases" / "v0.6.0.json").read_text(
                encoding="utf-8"
            )
        )
        version = manifest["version"].removeprefix("v")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        setup = (ROOT / "setup.py").read_text(encoding="utf-8")
        package_init = (ROOT / "src" / "hpc_skill_hub" / "__init__.py").read_text(
            encoding="utf-8"
        )
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        release_notes = (ROOT / "docs" / "RELEASE_NOTES_v0.6.0.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(f'version = "{version}"', pyproject)
        self.assertIn(f'version="{version}"', setup)
        self.assertIn(f'__version__ = "{version}"', package_init)
        self.assertIn(f'version: "{version}"', citation)
        self.assertIn(f"version-{version}-", readme)
        self.assertNotIn(f"version-{version}--rc", readme)
        self.assertIn("Status: release candidate", release_notes)

    def test_safety_audit_passes(self):
        result = run_cmd("python3", "tools/audit_safety.py")
        self.assertIn("Safety audit passed", result.stdout)

    def test_safety_audit_rejects_public_safety_leaks(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            leaky = Path(tmpdir) / "leaky.md"
            leaky.write_text(
                "\n".join(
                    [
                        "ssh " + "alice" + "@login." + "private-center.edu",
                        "#SBATCH --account=" + "real_alloc_123",
                        "#SBATCH --reservation=" + "priority_window",
                        "scratch=/scratch/" + "alice/project-data",
                        "dashboard=http://192.168." + "1.20:8888",
                        "notebook=http://127.0.0.1:8888/lab?to"
                        + "ken=abc123def456ghi789",
                    ]
                ),
                encoding="utf-8",
            )

            result = run_cmd_no_check("python3", "tools/audit_safety.py", str(leaky))

            self.assertNotEqual(result.returncode, 0)
            for rule in [
                "private-ssh-hostname",
                "slurm-account-literal",
                "slurm-reservation-literal",
                "private-storage-path",
                "private-ip",
                "jupyter-token",
            ]:
                self.assertIn(rule, result.stderr)

    def test_safety_audit_allows_public_safe_placeholders(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            safe = Path(tmpdir) / "safe.md"
            safe.write_text(
                "\n".join(
                    [
                        "ssh -N -L 8888:<compute-node>:8888 <user>@<login-node>",
                        "ssh -N -L 8888:node:8888 <user>@login.example.edu",
                        "#SBATCH --account=<account>",
                        "#SBATCH --reservation=<reservation>",
                        "scratch=/scratch/<user>/demo",
                        "project=/project/${PROJECT}/demo",
                        "MASTER_ADDR=127.0.0.1",
                        "jupyter lab --ip=0.0.0.0",
                        "https://www2.mmm.ucar.edu/wrf/users/wrf_users_guide/",
                    ]
                ),
                encoding="utf-8",
            )

            result = run_cmd("python3", "tools/audit_safety.py", str(safe))

            self.assertIn("Safety audit passed", result.stdout)

    def test_index_matches_skill_manifests(self):
        index = self.load_index()
        manifest_ids = sorted(path.parent.name for path in (ROOT / "skills").glob("*/skill.json"))
        index_ids = sorted(skill["id"] for skill in index["skills"])
        self.assertEqual(manifest_ids, index_ids)
        self.assertEqual(index["skill_count"], len(manifest_ids))

    def test_index_matches_site_adapters(self):
        index = self.load_index()
        adapter_ids = sorted(path.parent.name for path in (ROOT / "site-adapters").glob("*/site.json"))
        index_ids = sorted(adapter["id"] for adapter in index["site_adapters"])
        self.assertEqual(adapter_ids, index_ids)
        self.assertEqual(index["site_adapter_count"], len(adapter_ids))
        self.assertEqual(index["schema_version"], "0.2.0")
        for adapter in index["site_adapters"]:
            self.assertIn("public_policy", adapter)
            self.assertEqual(
                adapter["skill_overrides"],
                [item["skill_id"] for item in adapter["public_policy"]["skill_overrides"]],
            )

    def test_index_matches_collections(self):
        index = self.load_index()
        collection_ids = sorted(path.stem for path in (ROOT / "collections").glob("*.json"))
        index_ids = sorted(collection["id"] for collection in index["collections"])
        self.assertEqual(collection_ids, index_ids)
        self.assertEqual(index["collection_count"], len(collection_ids))

    def test_cli_show_json(self):
        result = run_cmd("python3", "tools/hpc_skill.py", "show", "slurm-submit-job", "--json")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["id"], "slurm-submit-job")
        self.assertIn("scheduler", payload["categories"])

    def test_cli_list_json_filters(self):
        result = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "list",
            "--collection",
            "simulation-workflows",
            "--maturity",
            "seed",
            "--tool",
            "bash",
            "--json",
        )
        payload = json.loads(result.stdout)
        self.assertTrue(payload)
        self.assertTrue(all(skill["maturity"] == "seed" for skill in payload))
        self.assertTrue(all("bash" in skill["tools"] for skill in payload))
        self.assertIn(
            "scientific-simulation-workflows",
            {skill["id"] for skill in payload},
        )

    def test_cli_collection_json(self):
        result = run_cmd("python3", "tools/hpc_skill.py", "collection", "core-hpc", "--json")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["id"], "core-hpc")
        self.assertIn("slurm-submit-job", payload["skill_ids"])

    def test_cli_health_json(self):
        result = run_cmd("python3", "tools/hpc_skill.py", "health", "--json")
        payload = json.loads(result.stdout)
        index = self.load_index()
        self.assertEqual(payload["skill_count"], index["skill_count"])
        self.assertEqual(payload["collection_count"], index["collection_count"])
        self.assertIn("risk_counts", payload)

    def test_cli_validate_one_skill(self):
        result = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "validate",
            "--skill",
            "slurm-submit-job",
        )
        self.assertIn("Validated 1 skill(s).", result.stdout)
        self.assertIn("Validation completed successfully.", result.stdout)

    def test_cli_validate_json(self):
        result = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "validate",
            "--skill",
            "slurm-submit-job",
            "--json",
        )
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skill"], "slurm-submit-job")
        self.assertEqual(payload["step_count"], 3)
        self.assertEqual(
            [step["status"] for step in payload["steps"]],
            ["passed", "passed", "passed"],
        )

    def test_cli_check_alias_json(self):
        result = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "check",
            "slurm-submit-job",
            "--json",
        )
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skill"], "slurm-submit-job")
        self.assertTrue(payload["skip_generated"])

    def test_cli_validate_full_checks_compatibility(self):
        result = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "validate",
            "--skip-safety",
        )
        self.assertIn("Check generated compatibility tables", result.stdout)
        self.assertIn("Compatibility tables are current", result.stdout)

    def test_package_module_entrypoint(self):
        result = run_cmd_with_env(
            "python3",
            "-m",
            "hpc_skill_hub",
            "collection",
            "core-hpc",
            "--json",
            env={"PYTHONPATH": "src"},
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["id"], "core-hpc")

    def test_package_entrypoint_uses_packaged_registry_outside_repo(self):
        index = self.load_index()
        with tempfile.TemporaryDirectory() as tmpdir:
            package_copy = Path(tmpdir) / "hpc_skill_hub"
            shutil.copytree(ROOT / "src" / "hpc_skill_hub", package_copy)
            result = run_cmd_with_env(
                "python3",
                "-m",
                "hpc_skill_hub",
                "health",
                "--json",
                cwd=tmpdir,
                env={"PYTHONPATH": tmpdir},
            )
            resolution_result = run_cmd_with_env(
                "python3",
                "-m",
                "hpc_skill_hub",
                "resolve",
                "slurm-submit-job",
                "--adapter",
                "example-campus-cluster",
                "--json",
                cwd=tmpdir,
                env={"PYTHONPATH": tmpdir},
            )

        payload = json.loads(result.stdout)
        self.assertEqual(payload["skill_count"], index["skill_count"])
        self.assertEqual(payload["collection_count"], index["collection_count"])
        self.assertEqual(payload["site_adapter_count"], index["site_adapter_count"])
        resolution = json.loads(resolution_result.stdout)
        self.assertEqual(resolution["resolution_status"], "mapped")
        self.assertEqual(resolution["override"]["skill_id"], "slurm-submit-job")

    def test_package_validate_entrypoint(self):
        result = run_cmd_with_env(
            "python3",
            "-m",
            "hpc_skill_hub",
            "validate",
            "--skill",
            "slurm-submit-job",
            env={"PYTHONPATH": "src"},
        )
        self.assertIn("Validation completed successfully.", result.stdout)

    def test_cli_adapter_json(self):
        result = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "adapter",
            "example-campus-cluster",
            "--json",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["id"], "example-campus-cluster")
        self.assertEqual(payload["scheduler"], "slurm")
        self.assertEqual(payload["public_policy"]["scheduler"]["type"], "slurm")

    def test_cli_resolve_site_adapter_json(self):
        result = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "resolve",
            "slurm-submit-job",
            "--adapter",
            "example-campus-cluster",
            "--json",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["resolution_status"], "mapped")
        self.assertTrue(payload["compatibility"]["scheduler_compatible"])
        self.assertTrue(payload["compatibility"]["explicit_override"])
        self.assertTrue(payload["review"]["required"])
        self.assertEqual(payload["override"]["skill_id"], "slurm-submit-job")
        self.assertEqual(payload["public_policy"]["scheduler"]["type"], "slurm")

    def test_cli_resolve_compatible_unmapped_and_incompatible(self):
        compatible = run_cmd(
            "python3",
            "tools/hpc_skill.py",
            "resolve",
            "slurm-monitor-job",
            "--adapter",
            "example-campus-cluster",
            "--json",
        )
        compatible_payload = json.loads(compatible.stdout)
        self.assertEqual(compatible_payload["resolution_status"], "compatible-unmapped")
        self.assertIsNone(compatible_payload["override"])

        incompatible = run_cmd_no_check(
            "python3",
            "tools/hpc_skill.py",
            "resolve",
            "pbs-submit-job",
            "--adapter",
            "example-campus-cluster",
            "--json",
        )
        self.assertEqual(incompatible.returncode, 2)
        incompatible_payload = json.loads(incompatible.stdout)
        self.assertEqual(incompatible_payload["resolution_status"], "incompatible")
        self.assertFalse(incompatible_payload["compatibility"]["scheduler_compatible"])

    def test_scaffold_skill_and_site_adapter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            run_cmd(
                "python3",
                "tools/hpc_skill.py",
                "new",
                "skill",
                "unit-test-skill",
                "--category",
                "education",
                "--tool",
                "bash",
                "--root",
                tmpdir,
            )
            run_cmd(
                "python3",
                "tools/hpc_skill.py",
                "new",
                "site-adapter",
                "unit-test-cluster",
                "--name",
                "Unit Test Cluster",
                "--root",
                tmpdir,
            )
            self.assertTrue(Path(tmpdir, "skills/unit-test-skill/skill.json").exists())
            self.assertTrue(Path(tmpdir, "skills/unit-test-skill/examples/example.sh").exists())
            self.assertTrue(
                Path(tmpdir, "skills/unit-test-skill/examples/check-prereqs.sh").exists()
            )
            self.assertTrue(
                Path(tmpdir, "skills/unit-test-skill/examples/review-checklist.md").exists()
            )
            self.assertTrue(Path(tmpdir, "site-adapters/unit-test-cluster/site.json").exists())

    def test_static_site_build(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "index.html"
            run_cmd("python3", "tools/build_site.py", "--output", str(output))
            html = output.read_text(encoding="utf-8")
            self.assertIn("HPC Skill Hub Registry", html)
            self.assertIn("v0.6.0 Release Status", html)
            self.assertIn("Repository ready", html)
            self.assertIn("Awaiting the v0.6.0 tag and attestations", html)
            self.assertIn("Community Pilot", html)
            self.assertIn("docs/COMMUNITY_PILOT_v0.6.0.md", html)
            self.assertIn("Registry Explorer", html)
            self.assertIn("Browse by Collection", html)
            self.assertIn("Open HPC Skill Ecosystem", html)
            self.assertIn("Contribution Lanes", html)
            self.assertIn("filter-risk", html)
            self.assertIn("filter-maturity", html)
            self.assertIn("filter-category", html)
            self.assertIn("filter-scheduler", html)
            self.assertIn("filter-tool", html)
            self.assertIn("filter-collection", html)
            self.assertIn("sort-skills", html)
            self.assertIn("view-table", html)
            self.assertIn("view-cards", html)
            self.assertIn("show-more-skills", html)
            self.assertIn("matching skills", html)
            self.assertIn("No skills match the current filters.", html)
            self.assertIn("data-tools=", html)
            self.assertIn("data-collections=", html)
            self.assertIn("data-collection-shortcut=", html)
            self.assertIn("URLSearchParams", html)
            self.assertIn("hpc-skill-hub-social-preview.png", html)
            self.assertIn("docs/SKILL_LIFECYCLE.md", html)
            self.assertIn("docs/ADOPTER_PLAYBOOK.md", html)
            self.assertIn("docs/INTEGRATION_GUIDE.md", html)
            self.assertIn("skills/slurm-submit-job/README.md", html)
            self.assertIn("collections/core-hpc.json", html)
            self.assertTrue((Path(tmpdir) / "README.md").exists())
            self.assertTrue((Path(tmpdir) / "docs/COMPATIBILITY.md").exists())
            self.assertTrue((Path(tmpdir) / "docs/SKILL_LIFECYCLE.md").exists())
            self.assertTrue((Path(tmpdir) / "collections/core-hpc.json").exists())
            self.assertTrue((Path(tmpdir) / "skills/slurm-submit-job/README.md").exists())
            self.assertTrue((Path(tmpdir) / "registry/index.json").exists())
            self.assertTrue((Path(tmpdir) / "registry/health.json").exists())
            self.assertTrue((Path(tmpdir) / "registry/release-status.json").exists())
            self.assertTrue(
                (Path(tmpdir) / "registry/provenance/v0.5.0.json").exists()
            )


if __name__ == "__main__":
    unittest.main()
