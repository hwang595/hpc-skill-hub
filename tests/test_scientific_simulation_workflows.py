import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "scientific-simulation-workflows"


def run_cmd(*args, cwd=ROOT, env=None):
    return subprocess.run(
        args,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class ScientificSimulationWorkflowTests(unittest.TestCase):
    def test_run_plan_defaults_to_plan_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            work = Path(tmpdir)
            input_file = work / "case.in"
            input_file.write_text("small smoke input\n", encoding="utf-8")
            output_dir = work / "plan"
            marker = work / "unexpected-run.txt"

            env = {
                "PATH": "/usr/bin:/bin",
                "SIM_SOFTWARE": "example-solver",
                "SIM_INPUTS": str(input_file),
                "SIM_COMMAND": f"printf ran > {marker}",
                "OUTPUT_DIR": str(output_dir),
            }
            run_cmd(
                "bash",
                str(SKILL_DIR / "examples" / "simulation-run-plan.sh"),
                cwd=work,
                env=env,
            )

            self.assertFalse(marker.exists())
            plan = (output_dir / "run-plan.md").read_text(encoding="utf-8")
            checks = (output_dir / "input-checks.txt").read_text(encoding="utf-8")
            command_log = (output_dir / "command-log.txt").read_text(encoding="utf-8")

            self.assertIn("example-solver", plan)
            self.assertIn(f"{input_file}: present file", checks)
            self.assertIn("Plan-only mode. SIM_COMMAND was not executed.", command_log)

    def test_log_scanner_reports_common_simulation_signals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "run.log"
            log_path.write_text(
                "\n".join(
                    [
                        "Step 10 completed",
                        "MPI_ABORT was invoked on rank 3",
                        "CUDA out of memory while allocating buffer",
                        "convergence not achieved after 100 iterations",
                    ]
                ),
                encoding="utf-8",
            )

            result = run_cmd(
                "python3",
                str(SKILL_DIR / "examples" / "check-simulation-log.py"),
                "--json",
                "--log",
                str(log_path),
            )
            payload = json.loads(result.stdout)
            signals = {finding["signal"] for finding in payload["findings"]}

            self.assertEqual(payload["missing_logs"], [])
            self.assertIn("mpi-abort", signals)
            self.assertIn("gpu-memory", signals)
            self.assertIn("convergence", signals)


if __name__ == "__main__":
    unittest.main()
