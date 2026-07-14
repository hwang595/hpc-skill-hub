import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub import doctor


class DoctorTests(unittest.TestCase):
    def test_default_report_passes_core_checks(self):
        report = doctor.doctor_report()
        checks = {check["id"]: check for check in report["checks"]}

        self.assertTrue(report["ok"], report)
        self.assertIn(report["status"], {"pass", "warn"})
        for check_id in (
            "python",
            "package-data",
            "security-policy",
            "registry",
            "release-status",
            "context-digests",
            "client-contract",
        ):
            self.assertEqual(checks[check_id]["status"], "pass", checks[check_id])
        self.assertEqual(checks["registry"]["details"]["skill_count"], 97)
        self.assertEqual(checks["context-digests"]["details"]["file_count"], 344)
        self.assertTrue(
            checks["release-status"]["details"]["repository_capability_ready"]
        )
        self.assertFalse(
            checks["release-status"]["details"]["external_evidence_ready"]
        )

    def test_cli_emits_machine_readable_report(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        result = subprocess.run(
            ["python3", "-m", "hpc_skill_hub", "doctor", "--json"],
            cwd=str(ROOT),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["source_mode"], "repository")

    def test_missing_optional_sdk_is_warning_unless_required(self):
        missing = doctor.metadata.PackageNotFoundError("mcp")
        with mock.patch.object(doctor.sys, "version_info", (3, 10, 0)):
            with mock.patch.object(doctor.metadata, "version", side_effect=missing):
                optional = doctor._check_mcp_dependency(False)
                required = doctor._check_mcp_dependency(True)

        self.assertEqual(optional.status, "warn")
        self.assertEqual(required.status, "fail")

    def test_unsupported_mcp_version_fails_closed(self):
        with mock.patch.object(doctor.sys, "version_info", (3, 10, 0)):
            with mock.patch.object(doctor.metadata, "version", return_value="2.0.0"):
                check = doctor._check_mcp_dependency(False)

        self.assertEqual(check.status, "fail")
        self.assertIn("stable v1", check.summary)

    def test_installed_package_version_mismatch_fails_closed(self):
        with mock.patch.object(doctor, "discover_repo_root", return_value=None):
            with mock.patch.object(doctor.metadata, "version", return_value="0.4.0"):
                check = doctor._check_package_version()

        self.assertEqual(check.status, "fail")
        self.assertEqual(check.details["source_mode"], "packaged")

    @unittest.skipUnless(
        sys.version_info[:2] >= (3, 10),
        "MCP optional dependency requires Python 3.10+",
    )
    def test_required_mcp_probe_when_sdk_is_installed(self):
        try:
            doctor.metadata.version("mcp")
        except doctor.metadata.PackageNotFoundError:
            self.skipTest("optional MCP SDK is not installed")

        report = doctor.doctor_report(require_mcp=True)
        checks = {check["id"]: check for check in report["checks"]}
        self.assertTrue(report["ok"], report)
        self.assertEqual(checks["mcp-dependency"]["status"], "pass")
        self.assertEqual(checks["mcp-protocol"]["status"], "pass")
        self.assertEqual(
            checks["mcp-protocol"]["details"]["probe_skill_id"],
            "slurm-submit-job",
        )
        self.assertGreater(
            checks["mcp-protocol"]["details"]["probe_file_count"], 0
        )


if __name__ == "__main__":
    unittest.main()
