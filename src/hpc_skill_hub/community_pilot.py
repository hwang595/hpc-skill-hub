"""Deterministic synthetic pilot for the community intake trust pipeline."""

from __future__ import annotations

import copy
import gzip
import io
import json
import re
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from .community_context import (
    build_community_context,
    community_resource_uri,
    validate_community_context,
)
from .community_evidence import REVIEW_SCHEMA_URL, create_review_packet, evidence_bindings
from .intake import intake_package
from .intake_receipt import DECISION_SCHEMA_URL, create_receipt
from .security_policy import canonical_digest


SCHEMA_VERSION = "0.1.0"
SCHEMA_URL = "../schemas/community-pilot-report.schema.json"
GENERATED_BY = "tools/community_pilot.py"
RELEASE = "v0.6.0"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

TRANSPORTS = ("directory", "zip", "tar")
FIXTURE_EXPECTATIONS: Mapping[str, Mapping[str, Any]] = {
    "benign": {
        "status": "ready-for-review",
        "security_verdict": "pass",
        "eligible_for_human_review": True,
        "security_finding_ids": [],
    },
    "ambiguous": {
        "status": "review-required",
        "security_verdict": "review",
        "eligible_for_human_review": True,
        "security_finding_ids": ["execution.dynamic-eval"],
    },
    "adversarial": {
        "status": "blocked",
        "security_verdict": "block",
        "eligible_for_human_review": False,
        "security_finding_ids": ["prompt.ignore-instructions"],
    },
}


class CommunityPilotError(ValueError):
    """Raised when the synthetic pilot contract is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommunityPilotError(message)


def _fixture_files(source: Path) -> Iterable[Tuple[str, bytes]]:
    for path in sorted(source.rglob("*")):
        if path.is_file():
            yield path.relative_to(source).as_posix(), path.read_bytes()


def _write_zip(source: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, content in _fixture_files(source):
            info = zipfile.ZipInfo(relative, date_time=(2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)


def _write_tar(source: Path, destination: Path) -> None:
    with destination.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for relative, content in _fixture_files(source):
                    info = tarfile.TarInfo(relative)
                    info.size = len(content)
                    info.mode = 0o644
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    archive.addfile(info, io.BytesIO(content))


def _materialize_transport(source: Path, transport: str, root: Path) -> Path:
    if transport == "directory":
        return source
    destination = root / f"{source.name}.{transport}"
    if transport == "zip":
        _write_zip(source, destination)
    elif transport == "tar":
        _write_tar(source, destination)
    else:
        raise CommunityPilotError(f"unsupported pilot transport: {transport}")
    return destination


def _case_payload(fixture: str, transport: str, report: Dict[str, Any]) -> Dict[str, Any]:
    security = report["security_report"]
    expected = copy.deepcopy(FIXTURE_EXPECTATIONS[fixture])
    observed = {
        "status": report["summary"]["status"],
        "security_verdict": report["summary"]["security_verdict"],
        "eligible_for_human_review": report["summary"]["eligible_for_human_review"],
        "context_loading_allowed": report["summary"]["context_loading_allowed"],
        "inventory_complete": report["inventory"]["complete"],
        "quarantine_cleaned": report["quarantine"]["cleaned"],
        "execution_performed": report["quarantine"]["execution_performed"],
        "instruction_content_returned": report["quarantine"]["instruction_content_returned"],
        "boundary_finding_ids": sorted(
            finding["id"] for finding in report["boundary_findings"]
        ),
        "security_finding_ids": sorted(
            finding["rule_id"] for finding in security["findings"]
        ),
        "source_digest": report["source"]["sha256"],
        "inventory_digest": report["inventory"]["content_digest"],
        "file_count": report["inventory"]["file_count"],
        "total_bytes": report["inventory"]["total_bytes"],
    }
    passed = all(
        (
            observed["status"] == expected["status"],
            observed["security_verdict"] == expected["security_verdict"],
            observed["eligible_for_human_review"]
            is expected["eligible_for_human_review"],
            observed["security_finding_ids"] == expected["security_finding_ids"],
            observed["context_loading_allowed"] is False,
            observed["inventory_complete"] is True,
            observed["quarantine_cleaned"] is True,
            observed["execution_performed"] is False,
            observed["instruction_content_returned"] is False,
            observed["boundary_finding_ids"] == [],
        )
    )
    return {
        "id": f"{fixture}-{transport}",
        "fixture": fixture,
        "transport": transport,
        "expected": expected,
        "observed": observed,
        "passed": passed,
    }


def _accepted_decision(draft: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "$schema": DECISION_SCHEMA_URL,
        "schema_version": "0.1.0",
        "reviewer_id": "pilot-intake-maintainer",
        "reviewer_role": "maintainer-intake",
        "reviewed_on": "2026-07-15",
        "disposition": "accept",
        "bindings": copy.deepcopy(draft["bindings"]),
        "acknowledged_finding_digests": [],
        "acknowledged_exception_ids": [],
        "rationale": "Synthetic pilot decision for the exact benign fixture only.",
    }


def _approved_review(packet: Dict[str, Any], scope: str) -> Dict[str, Any]:
    reviewer = (
        "pilot-domain-reviewer" if scope == "domain" else "pilot-safety-reviewer"
    )
    review = {
        "$schema": REVIEW_SCHEMA_URL,
        "schema_version": "0.1.0",
        "review_id": f"pilot-{scope}-review",
        "contribution": {"id": "community-pilot-benign", "version": "0.1.0"},
        "scope": scope,
        "reviewer_id": reviewer,
        "reviewed_on": "2026-07-15",
        "domain": "scheduler" if scope == "domain" else "safety",
        "decision": "approved",
        "independence_attestation": True,
        "conflict_disclosure": "Synthetic fixture; no real contributor relationship.",
        "evidence_url": f"https://example.com/community-pilot/{scope}-review",
        "checklist": {
            "source_digest_verified": True,
            "scope_and_assumptions_reviewed": True,
            "examples_and_side_effects_reviewed": True,
            "risk_and_site_boundaries_reviewed": True,
            "references_reviewed": True,
            "public_safe_evidence_attested": True,
        },
        "bindings": evidence_bindings(packet),
        "notes": "Synthetic review used only to exercise exact evidence bindings.",
    }
    review["review_digest"] = canonical_digest(review)
    return review


def build_accepted_context_fixture(source: Path) -> Dict[str, Any]:
    """Build the benign P2-P4 fixture without authorizing operational use."""

    draft = create_receipt(source)
    receipt = create_receipt(source, decision=_accepted_decision(draft))
    packet = create_review_packet(
        receipt,
        source,
        contribution_id="community-pilot-benign",
        version="0.1.0",
        risk_level="medium",
        domains=["scheduler"],
        submitter_id="pilot-contributor",
        artifact_url="https://example.com/community-pilot/benign-0.1.0.zip",
    )
    reviews = [
        _approved_review(packet, "domain"),
        _approved_review(packet, "safety"),
    ]
    bundle = build_community_context(source, receipt, packet, reviews)
    validate_community_context(bundle)
    return bundle


def _pipeline_payload(source: Path) -> Dict[str, Any]:
    bundle = build_accepted_context_fixture(source)
    provenance = bundle["provenance"]
    return {
        "status": "pass",
        "fixture": "benign",
        "transport": "directory",
        "receipt_status": provenance["receipt"]["status"],
        "review_status": provenance["review"]["status"],
        "maturity_promotion": provenance["maturity"]["promotion"],
        "adoption_report_count": provenance["review"]["evidence"][
            "adoption_report_count"
        ],
        "resource_uri": community_resource_uri(
            bundle["contribution"]["id"], bundle["contribution"]["version"]
        ),
        "file_count": bundle["content_manifest"]["file_count"],
        "total_bytes": bundle["content_manifest"]["total_bytes"],
        "receipt_digest": bundle["evidence"]["receipt"]["receipt_digest"],
        "packet_digest": bundle["evidence"]["packet"]["packet_digest"],
        "status_digest": bundle["evidence"]["status"]["status_digest"],
        "bundle_digest": bundle["bundle_digest"],
        "execution_authorized": False,
        "examples_execute_automatically": bundle["usage_contract"][
            "execute_examples_automatically"
        ],
    }


def build_pilot_report(fixtures: Path) -> Dict[str, Any]:
    """Run the deterministic fixture matrix and return a content-redacted report."""

    fixture_paths = {name: fixtures / name for name in FIXTURE_EXPECTATIONS}
    missing = [name for name, path in fixture_paths.items() if not path.is_dir()]
    _require(not missing, "missing pilot fixtures: " + ", ".join(sorted(missing)))

    cases: List[Dict[str, Any]] = []
    policy: Dict[str, Any] | None = None
    with tempfile.TemporaryDirectory(prefix="hpc-skill-hub-community-pilot-") as tmpdir:
        archive_root = Path(tmpdir)
        for fixture in FIXTURE_EXPECTATIONS:
            for transport in TRANSPORTS:
                source = _materialize_transport(
                    fixture_paths[fixture], transport, archive_root
                )
                intake = intake_package(source)
                cases.append(_case_payload(fixture, transport, intake))
                if policy is None:
                    policy = copy.deepcopy(intake["security_report"]["policy"])

    passed_count = sum(case["passed"] for case in cases)
    report: Dict[str, Any] = {
        "$schema": SCHEMA_URL,
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "release": RELEASE,
        "policy": {
            "id": policy["id"],
            "version": policy["version"],
            "effective_digest": policy["effective_digest"],
            "fail_on": policy["fail_on"],
        },
        "matrix": {
            "fixture_count": len(FIXTURE_EXPECTATIONS),
            "transport_count": len(TRANSPORTS),
            "case_count": len(cases),
            "passed_count": passed_count,
            "failed_count": len(cases) - passed_count,
        },
        "cases": cases,
        "accepted_context_pipeline": _pipeline_payload(fixture_paths["benign"]),
        "installed_isolation_contract": {
            "core": {
                "status": "required-in-ci",
                "command": "python3 tools/installed_release_smoke.py --wheel <wheel> --mode core",
            },
            "mcp": {
                "status": "required-in-ci",
                "command": "python3 tools/installed_release_smoke.py --wheel <wheel> --mode mcp --community-bundle <bundle>",
            },
            "requires_outside_checkout": True,
            "requires_pythonpath_removal": True,
            "requires_installed_module_path_verification": True,
        },
        "claims": {
            "synthetic_fixtures_only": True,
            "real_community_acceptance": False,
            "independent_external_review": False,
            "real_site_adoption": False,
            "maturity_promotion": False,
            "comparative_agent_lift": False,
        },
    }
    report["report_digest"] = canonical_digest(report)
    validate_pilot_report(report)
    return report


def validate_pilot_report(report: Dict[str, Any]) -> None:
    expected_keys = {
        "$schema",
        "schema_version",
        "generated_by",
        "release",
        "policy",
        "matrix",
        "cases",
        "accepted_context_pipeline",
        "installed_isolation_contract",
        "claims",
        "report_digest",
    }
    _require(isinstance(report, dict), "pilot report must be an object")
    _require(set(report) == expected_keys, "pilot report has an invalid top-level contract")
    _require(report["$schema"] == SCHEMA_URL, "pilot report schema mismatch")
    _require(report["schema_version"] == SCHEMA_VERSION, "unsupported pilot report version")
    _require(report["generated_by"] == GENERATED_BY, "pilot report generator mismatch")
    _require(report["release"] == RELEASE, "pilot report release mismatch")
    _require(
        isinstance(report["report_digest"], str)
        and SHA256_RE.fullmatch(report["report_digest"]) is not None,
        "invalid pilot report digest",
    )
    unsigned = {key: value for key, value in report.items() if key != "report_digest"}
    _require(
        report["report_digest"] == canonical_digest(unsigned),
        "pilot report digest mismatch",
    )

    policy = report["policy"]
    _require(
        isinstance(policy, dict)
        and set(policy) == {"id", "version", "effective_digest", "fail_on"},
        "pilot policy contract is invalid",
    )
    _require(policy["id"] == "community-default", "pilot policy id mismatch")
    _require(policy["fail_on"] == "high", "pilot policy threshold mismatch")
    _require(
        isinstance(policy["effective_digest"], str)
        and SHA256_RE.fullmatch(policy["effective_digest"]) is not None,
        "invalid pilot policy digest",
    )

    cases = report["cases"]
    expected_case_ids = [
        f"{fixture}-{transport}"
        for fixture in FIXTURE_EXPECTATIONS
        for transport in TRANSPORTS
    ]
    _require(isinstance(cases, list), "pilot cases must be an array")
    _require([case.get("id") for case in cases] == expected_case_ids, "pilot case matrix mismatch")
    _require(all(case.get("passed") is True for case in cases), "one or more pilot cases failed")
    for case in cases:
        _require(
            isinstance(case, dict)
            and set(case) == {"id", "fixture", "transport", "expected", "observed", "passed"},
            "pilot case contract is invalid",
        )
        expected = FIXTURE_EXPECTATIONS[case["fixture"]]
        observed = case["observed"]
        _require(case["transport"] in TRANSPORTS, "invalid pilot transport")
        _require(case["expected"] == expected, "pilot expectation drift")
        _require(
            isinstance(observed, dict)
            and set(observed)
            == {
                "status",
                "security_verdict",
                "eligible_for_human_review",
                "context_loading_allowed",
                "inventory_complete",
                "quarantine_cleaned",
                "execution_performed",
                "instruction_content_returned",
                "boundary_finding_ids",
                "security_finding_ids",
                "source_digest",
                "inventory_digest",
                "file_count",
                "total_bytes",
            },
            "pilot observation contract is invalid",
        )
        _require(observed["status"] == expected["status"], "pilot status mismatch")
        _require(
            observed["security_verdict"] == expected["security_verdict"],
            "pilot security verdict mismatch",
        )
        _require(
            observed["eligible_for_human_review"]
            is expected["eligible_for_human_review"],
            "pilot human-review eligibility mismatch",
        )
        _require(
            observed["security_finding_ids"] == expected["security_finding_ids"],
            "pilot security findings mismatch",
        )
        for name in ("source_digest", "inventory_digest"):
            _require(
                isinstance(observed[name], str)
                and SHA256_RE.fullmatch(observed[name]) is not None,
                f"invalid {case['id']} {name}",
            )
        _require(observed["context_loading_allowed"] is False, "intake exposed context")
        _require(observed["execution_performed"] is False, "intake executed content")
        _require(
            observed["instruction_content_returned"] is False,
            "intake returned instruction content",
        )
        _require(observed["quarantine_cleaned"] is True, "quarantine was not cleaned")
        _require(observed["inventory_complete"] is True, "pilot inventory is incomplete")
        _require(observed["boundary_finding_ids"] == [], "pilot has boundary findings")
        _require(
            type(observed["file_count"]) is int and observed["file_count"] > 0,
            "invalid pilot file count",
        )
        _require(
            type(observed["total_bytes"]) is int and observed["total_bytes"] > 0,
            "invalid pilot byte count",
        )

    for fixture in FIXTURE_EXPECTATIONS:
        inventory_digests = {
            case["observed"]["inventory_digest"]
            for case in cases
            if case["fixture"] == fixture
        }
        _require(
            len(inventory_digests) == 1,
            f"{fixture} inventory differs across transports",
        )

    matrix = report["matrix"]
    _require(
        isinstance(matrix, dict)
        and set(matrix)
        == {"fixture_count", "transport_count", "case_count", "passed_count", "failed_count"},
        "pilot matrix contract is invalid",
    )
    _require(matrix["fixture_count"] == len(FIXTURE_EXPECTATIONS), "pilot fixture count mismatch")
    _require(matrix["transport_count"] == len(TRANSPORTS), "pilot transport count mismatch")
    _require(matrix["case_count"] == len(cases), "pilot case count mismatch")
    _require(matrix["passed_count"] == len(cases), "pilot pass count mismatch")
    _require(matrix["failed_count"] == 0, "pilot report contains failed cases")

    pipeline = report["accepted_context_pipeline"]
    _require(
        isinstance(pipeline, dict)
        and set(pipeline)
        == {
            "status",
            "fixture",
            "transport",
            "receipt_status",
            "review_status",
            "maturity_promotion",
            "adoption_report_count",
            "resource_uri",
            "file_count",
            "total_bytes",
            "receipt_digest",
            "packet_digest",
            "status_digest",
            "bundle_digest",
            "execution_authorized",
            "examples_execute_automatically",
        },
        "accepted context pipeline contract is invalid",
    )
    _require(pipeline["status"] == "pass", "accepted context pipeline did not pass")
    _require(pipeline["receipt_status"] == "accepted", "pilot receipt is not accepted")
    _require(pipeline["review_status"] == "review-complete", "pilot review is incomplete")
    _require(
        pipeline["maturity_promotion"] == "not-authorized",
        "pilot authorized maturity promotion",
    )
    _require(pipeline["execution_authorized"] is False, "pilot authorized execution")
    _require(
        pipeline["examples_execute_automatically"] is False,
        "pilot enabled automatic example execution",
    )
    for name in ("receipt_digest", "packet_digest", "status_digest", "bundle_digest"):
        _require(
            isinstance(pipeline[name], str) and SHA256_RE.fullmatch(pipeline[name]) is not None,
            f"invalid pipeline {name}",
        )

    isolation = report["installed_isolation_contract"]
    _require(
        isinstance(isolation, dict)
        and set(isolation)
        == {
            "core",
            "mcp",
            "requires_outside_checkout",
            "requires_pythonpath_removal",
            "requires_installed_module_path_verification",
        },
        "installed isolation contract is invalid",
    )
    for mode in ("core", "mcp"):
        _require(
            isinstance(isolation[mode], dict)
            and set(isolation[mode]) == {"status", "command"}
            and isolation[mode]["status"] == "required-in-ci"
            and isinstance(isolation[mode]["command"], str)
            and "installed_release_smoke.py" in isolation[mode]["command"],
            f"invalid {mode} isolation mode",
        )
    _require(
        all(
            isolation[name] is True
            for name in (
                "requires_outside_checkout",
                "requires_pythonpath_removal",
                "requires_installed_module_path_verification",
            )
        ),
        "installed isolation requirements are incomplete",
    )

    claims = report["claims"]
    _require(
        isinstance(claims, dict)
        and set(claims)
        == {
            "synthetic_fixtures_only",
            "real_community_acceptance",
            "independent_external_review",
            "real_site_adoption",
            "maturity_promotion",
            "comparative_agent_lift",
        },
        "pilot claims contract is invalid",
    )
    _require(claims["synthetic_fixtures_only"] is True, "pilot claims are not synthetic")
    _require(
        all(value is False for key, value in claims.items() if key != "synthetic_fixtures_only"),
        "pilot report overclaims external evidence",
    )


def serialized_report(report: Dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def render_pilot_report(report: Dict[str, Any]) -> str:
    validate_pilot_report(report)
    matrix = report["matrix"]
    pipeline = report["accepted_context_pipeline"]
    lines = [
        "# v0.6 Community Intake Pilot",
        "",
        "This is a deterministic synthetic safety pilot. It validates repository",
        "contracts only; it is not evidence of a real community acceptance, external",
        "domain review, site adoption, maturity promotion, or agent-performance lift.",
        "",
        "## Result",
        "",
        f"- Matrix: {matrix['passed_count']}/{matrix['case_count']} cases passed.",
        f"- Policy: `{report['policy']['id']}@{report['policy']['version']}`.",
        f"- Accepted pipeline: `{pipeline['review_status']}` with maturity `{pipeline['maturity_promotion']}`.",
        f"- Machine-readable report: `registry/community-pilot-v0.6.0.json`.",
        f"- Report digest: `{report['report_digest']}`.",
        "",
        "## Fixture Matrix",
        "",
        "| Fixture | Transport | Expected | Observed | Findings | Result |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for case in report["cases"]:
        findings = ", ".join(case["observed"]["security_finding_ids"]) or "none"
        lines.append(
            f"| `{case['fixture']}` | `{case['transport']}` | "
            f"`{case['expected']['status']}` | `{case['observed']['status']}` | "
            f"`{findings}` | {'pass' if case['passed'] else 'fail'} |"
        )
    lines.extend(
        [
            "",
            "Every intake case kept context loading disabled, performed no execution,",
            "returned no instruction content, and cleaned its temporary quarantine.",
            "Directory, deterministic ZIP, and deterministic TAR inputs produced the",
            "same inventory digest for each fixture.",
            "",
            "## Accepted Pipeline",
            "",
            "The benign fixture additionally exercises an exact-bound accepted P2 receipt,",
            "synthetic P3 domain and safety decisions, and P4 context construction. The",
            "result is review-complete but remains non-authorizing: examples do not execute",
            "automatically, operational actions require explicit intent, and maturity",
            "promotion remains `not-authorized`.",
            "",
            "## Installed Isolation",
            "",
            "CI must build the wheel and run `tools/installed_release_smoke.py` from a",
            "temporary directory for both core and MCP modes. The verifier removes",
            "`PYTHONPATH`, checks the imported module path is outside the checkout, requires",
            "zero community resources by default, and verifies one explicit review-complete",
            "bundle without exposing it through the metadata-only catalog.",
            "",
            "## Evidence Boundary",
            "",
            "The fixtures are controlled repository test data and the reviewer identities",
            "are synthetic. A passing report cannot promote a skill, establish operational",
            "correctness, or open comparative and adoption evidence gates.",
            "",
        ]
    )
    return "\n".join(lines)
