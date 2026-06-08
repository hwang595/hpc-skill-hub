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

    def test_safety_audit_passes(self):
        result = run_cmd("python3", "tools/audit_safety.py")
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
        self.assertEqual(payload["skill_count"], 32)
        self.assertEqual(payload["collection_count"], 5)
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
            self.assertTrue((Path(tmpdir) / "collections/core-hpc.json").exists())
            self.assertTrue((Path(tmpdir) / "skills/slurm-submit-job/README.md").exists())
            self.assertTrue((Path(tmpdir) / "registry/index.json").exists())
            self.assertTrue((Path(tmpdir) / "registry/health.json").exists())


if __name__ == "__main__":
    unittest.main()
