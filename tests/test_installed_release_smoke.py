import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "installed_release_smoke.py"


def load_module():
    spec = importlib.util.spec_from_file_location("installed_release_smoke", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class InstalledReleaseSmokeTests(unittest.TestCase):
    def test_isolated_environment_removes_source_overrides(self):
        module = load_module()
        previous_pythonpath = os.environ.get("PYTHONPATH")
        previous_root = os.environ.get("HPC_SKILL_HUB_ROOT")
        try:
            os.environ["PYTHONPATH"] = "/tmp/source-override"
            os.environ["HPC_SKILL_HUB_ROOT"] = "/tmp/repository-override"
            env = module._isolated_environment()
        finally:
            if previous_pythonpath is None:
                os.environ.pop("PYTHONPATH", None)
            else:
                os.environ["PYTHONPATH"] = previous_pythonpath
            if previous_root is None:
                os.environ.pop("HPC_SKILL_HUB_ROOT", None)
            else:
                os.environ["HPC_SKILL_HUB_ROOT"] = previous_root

        self.assertNotIn("PYTHONPATH", env)
        self.assertNotIn("HPC_SKILL_HUB_ROOT", env)
        self.assertEqual(env["PYTHONNOUSERSITE"], "1")

    def test_outside_check_distinguishes_checkout_and_temporary_workspace(self):
        module = load_module()
        self.assertFalse(module._outside(ROOT / "src", ROOT))
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertTrue(module._outside(Path(tmpdir), ROOT))

    def test_missing_wheel_fails_before_environment_creation(self):
        module = load_module()
        with self.assertRaisesRegex(module.InstalledSmokeError, "wheel does not exist"):
            module.verify_installed_wheel(ROOT / "dist" / "missing.whl", "core")

    def test_cli_help_documents_both_modes(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "--help"],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("core", result.stdout)
        self.assertIn("mcp", result.stdout)


if __name__ == "__main__":
    unittest.main()
