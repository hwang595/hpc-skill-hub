import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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

    def test_generated_release_manifest_is_current(self):
        result = run_cmd(
            "python3",
            "tools/build_release_manifest.py",
            "v0.1.0",
            "--check",
        )
        self.assertIn("Release manifest is current", result.stdout)

    def test_release_manifest_summarizes_registry(self):
        manifest_path = ROOT / "registry" / "releases" / "v0.1.0.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        index = self.load_index()

        self.assertEqual(manifest["version"], "v0.1.0")
        self.assertEqual(manifest["registry"]["skill_count"], index["skill_count"])
        self.assertEqual(
            manifest["registry"]["collection_count"], index["collection_count"]
        )
        self.assertEqual(
            manifest["registry"]["site_adapter_count"], index["site_adapter_count"]
        )
        paths = {entry["path"] for entry in manifest["files"]}
        self.assertIn("registry/index.json", paths)
        self.assertIn("docs/COMPATIBILITY.md", paths)
        self.assertIn("skills/slurm-submit-job/skill.json", paths)

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

    def test_scaffold_skill_and_site_adapter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            run_cmd(
                "python3",
                "tools/hpc_skill.py",
                "scaffold",
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
                "scaffold",
                "site-adapter",
                "unit-test-cluster",
                "--name",
                "Unit Test Cluster",
                "--root",
                tmpdir,
            )
            self.assertTrue(Path(tmpdir, "skills/unit-test-skill/skill.json").exists())
            self.assertTrue(Path(tmpdir, "skills/unit-test-skill/examples/example.sh").exists())
            self.assertTrue(Path(tmpdir, "site-adapters/unit-test-cluster/site.json").exists())

    def test_static_site_build(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "index.html"
            run_cmd("python3", "tools/build_site.py", "--output", str(output))
            html = output.read_text(encoding="utf-8")
            self.assertIn("HPC Skill Hub Registry", html)
            self.assertIn("skills/slurm-submit-job/README.md", html)
            self.assertIn("collections/core-hpc.json", html)
            self.assertTrue((Path(tmpdir) / "README.md").exists())
            self.assertTrue((Path(tmpdir) / "docs/COMPATIBILITY.md").exists())
            self.assertTrue((Path(tmpdir) / "collections/core-hpc.json").exists())
            self.assertTrue((Path(tmpdir) / "skills/slurm-submit-job/README.md").exists())
            self.assertTrue((Path(tmpdir) / "registry/index.json").exists())
            self.assertTrue((Path(tmpdir) / "registry/health.json").exists())


if __name__ == "__main__":
    unittest.main()
