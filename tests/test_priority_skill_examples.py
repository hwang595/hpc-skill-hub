import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_example(argv, env=None):
    command_env = os.environ.copy()
    if env:
        command_env.update(env)
    return subprocess.run(
        argv,
        cwd=str(ROOT),
        env=command_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class PrioritySkillExampleTests(unittest.TestCase):
    def test_oom_collector_writes_new_report_and_refuses_overwrite(self):
        script = ROOT / "skills/slurm-oom-memory-triage/examples/slurm-oom-triage.sh"
        log = ROOT / "benchmarks/fixtures/slurm/oom-log.txt"
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "oom-report"
            env = {"JOB_LOG": str(log), "REPORT_DIR": str(report), "JOB_ID": ""}
            first = run_example(["bash", str(script)], env)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("oom-kill", (report / "log-memory-signals.txt").read_text())

            second = run_example(["bash", str(script)], env)
            self.assertEqual(second.returncode, 2)
            self.assertIn("already exists", second.stderr)

    def test_output_log_collector_refuses_report_overwrite(self):
        script = ROOT / "skills/slurm-output-log-triage/examples/slurm-output-log-triage.sh"
        log = ROOT / "benchmarks/fixtures/slurm/output-log-filesystem.txt"
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "output-report"
            env = {"JOB_LOG": str(log), "REPORT_DIR": str(report), "JOB_ID": ""}
            first = run_example(["bash", str(script)], env)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue((report / "path-checks.txt").is_file())

            second = run_example(["bash", str(script)], env)
            self.assertEqual(second.returncode, 2)
            self.assertIn("already exists", second.stderr)

    def test_permission_collector_rejects_missing_requested_log(self):
        script = ROOT / "skills/shared-project-permissions-triage/examples/permission-triage.sh"
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_log = Path(temp_dir) / "missing.log"
            result = run_example(["bash", str(script), ".", str(missing_log)])
        self.assertEqual(result.returncode, 2)
        self.assertIn("does not exist", result.stderr)

    def test_storage_preflight_does_not_create_unapproved_root(self):
        script = ROOT / "skills/ior-mdtest-storage-smoke/examples/storage-smoke-preflight.sh"
        with tempfile.TemporaryDirectory() as temp_dir:
            planned_root = Path(temp_dir) / "planned" / "ior-mdtest-smoke"
            result = run_example(
                ["bash", str(script), "--paths-only", str(planned_root)],
                {"CREATE_BENCH_ROOT": "0"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(planned_root.exists())
            self.assertIn("No directory was created", result.stdout)


if __name__ == "__main__":
    unittest.main()
