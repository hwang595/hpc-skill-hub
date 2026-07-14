import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.release_provenance import (  # noqa: E402
    ReleaseProvenanceError,
    validate_release_provenance,
)


class ReleaseProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(
            (ROOT / "registry" / "provenance" / "v0.5.0.json").read_text(
                encoding="utf-8"
            )
        )
        cls.manifest_digest = hashlib.sha256(
            (ROOT / "registry" / "releases" / "v0.5.0.json").read_bytes()
        ).hexdigest()

    def test_current_receipt_is_valid(self):
        validate_release_provenance(
            self.receipt,
            "v0.5.0",
            self.manifest_digest,
        )

    def test_rejects_unverified_artifact(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["artifacts"][1]["attestation"]["status"] = "pending"

        with self.assertRaisesRegex(ReleaseProvenanceError, "not verified"):
            validate_release_provenance(receipt, "v0.5.0", self.manifest_digest)

    def test_rejects_manifest_digest_mismatch(self):
        with self.assertRaisesRegex(ReleaseProvenanceError, "manifest digest"):
            validate_release_provenance(self.receipt, "v0.5.0", "0" * 64)

    def test_rejects_unknown_contract_field(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["unsigned_note"] = "not part of the contract"

        with self.assertRaisesRegex(ReleaseProvenanceError, "top-level contract"):
            validate_release_provenance(receipt, "v0.5.0", self.manifest_digest)

    def test_rejects_verification_before_workflow_completion(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["verification"]["verified_at"] = "2026-07-14T23:14:00Z"

        with self.assertRaisesRegex(ReleaseProvenanceError, "predates"):
            validate_release_provenance(receipt, "v0.5.0", self.manifest_digest)


if __name__ == "__main__":
    unittest.main()
