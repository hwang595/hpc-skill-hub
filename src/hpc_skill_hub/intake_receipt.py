"""Deterministic acceptance receipts for quarantined community intake."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .intake import DEFAULT_LIMITS, IntakeError, IntakeLimits, intake_package
from .security_policy import SecurityPolicyError, canonical_digest


RECEIPT_NAME = "hpc-skill-community-intake-receipt"
RECEIPT_VERSION = "0.1.0"
RECEIPT_SCHEMA_URL = (
    "https://hpc-skill-hub.org/schemas/community-skill-intake-receipt.schema.json"
)
DECISION_SCHEMA_URL = (
    "https://hpc-skill-hub.org/schemas/community-skill-intake-decision.schema.json"
)
CONTEXT_FORMAT = "bounded-text-inventory-v1"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
REVIEWER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,62}[A-Za-z0-9])?$")


class IntakeReceiptError(ValueError):
    """Raised when an intake receipt or reviewer decision is invalid or stale."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise IntakeReceiptError(message)


def _is_sha256(value: Any, *, nullable: bool = False) -> bool:
    return (nullable and value is None) or (
        isinstance(value, str) and SHA256_RE.fullmatch(value) is not None
    )


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def ensure_external_artifact(source: Path, artifact: Path, label: str) -> None:
    """Reject decisions and receipts stored inside the contribution."""

    source = source.expanduser().absolute()
    artifact = artifact.expanduser().absolute()
    if source.is_dir() and _inside(artifact, source):
        raise IntakeReceiptError(f"{label} must be stored outside the contribution")
    if source.is_file() and artifact == source:
        raise IntakeReceiptError(f"the contribution cannot be its own {label}")


def load_json_artifact(path: Path, label: str) -> Dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntakeReceiptError(f"cannot read {label} {path.name}: {exc}") from exc
    _require(isinstance(payload, dict), f"{label} must be a JSON object")
    return payload


def _portable_intake_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Remove the local source filename while retaining all bounded evidence."""

    normalized = copy.deepcopy(report)
    try:
        normalized["source"]["label"] = "contribution"
    except (KeyError, TypeError) as exc:
        raise IntakeReceiptError("intake report has an invalid source contract") from exc
    return normalized


def _accepted_exceptions(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    security = report.get("security_report")
    if security is None:
        return []
    _require(isinstance(security, dict), "security_report must be an object or null")
    findings = security.get("findings")
    _require(isinstance(findings, list), "security findings must be an array")
    accepted: List[Dict[str, Any]] = []
    for finding in findings:
        _require(isinstance(finding, dict), "security finding must be an object")
        if finding.get("disposition") != "accepted":
            continue
        exception = finding.get("exception")
        _require(isinstance(exception, dict), "accepted finding is missing its exception")
        record = {
            "id": exception.get("id"),
            "finding_digest": finding.get("finding_digest"),
            "rule_id": finding.get("rule_id"),
            "path": finding.get("path"),
            "expires_on": exception.get("expires_on"),
            "review_digest": exception.get("review_digest"),
        }
        _require(
            isinstance(record["id"], str)
            and re.fullmatch(r"[a-z][a-z0-9-]*", record["id"]) is not None,
            "accepted exception id is invalid",
        )
        _require(_is_sha256(record["finding_digest"]), "accepted finding digest is invalid")
        _require(
            isinstance(record["rule_id"], str) and bool(record["rule_id"]),
            "accepted exception rule id is invalid",
        )
        _require(
            isinstance(record["path"], str) and bool(record["path"]),
            "accepted exception path is invalid",
        )
        _require(
            isinstance(record["expires_on"], str)
            and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", record["expires_on"])
            is not None,
            "accepted exception expiration is invalid",
        )
        _require(_is_sha256(record["review_digest"]), "exception review digest is invalid")
        accepted.append(record)
    accepted.sort(key=lambda item: (str(item["id"]), str(item["finding_digest"])))
    _require(
        len({item["id"] for item in accepted}) == len(accepted),
        "accepted exception ids must be unique",
    )
    applied_ids = security.get("provenance", {}).get("applied_exception_ids")
    accepted_count = security.get("summary", {}).get("accepted_exception_count")
    _require(
        isinstance(applied_ids, list)
        and applied_ids == sorted(item["id"] for item in accepted)
        and accepted_count == len(accepted),
        "accepted exception provenance is inconsistent",
    )
    return accepted


def _active_finding_digests(report: Dict[str, Any]) -> List[str]:
    security = report.get("security_report")
    if security is None:
        return []
    digests = [
        item.get("finding_digest")
        for item in security.get("findings", [])
        if isinstance(item, dict) and item.get("disposition") == "active"
    ]
    _require(all(_is_sha256(value) for value in digests), "active finding digest is invalid")
    _require(len(set(digests)) == len(digests), "active finding digests must be unique")
    return sorted(digests)


def _candidate_context(report: Dict[str, Any]) -> Dict[str, Any]:
    inventory = report.get("inventory")
    if not isinstance(inventory, dict) or inventory.get("complete") is not True:
        return {
            "format": CONTEXT_FORMAT,
            "candidate_digest": None,
            "accepted_digest": None,
            "file_count": 0,
            "total_bytes": 0,
            "loading_allowed": False,
        }
    files = inventory.get("files")
    if not isinstance(files, list):
        raise IntakeReceiptError("inventory files must be an array")
    records = []
    for item in files:
        if not (
            isinstance(item, dict)
            and item.get("type") == "file"
            and item.get("content_type") == "text"
            and isinstance(item.get("path"), str)
            and isinstance(item.get("bytes"), int)
            and _is_sha256(item.get("sha256"))
        ):
            return {
                "format": CONTEXT_FORMAT,
                "candidate_digest": None,
                "accepted_digest": None,
                "file_count": 0,
                "total_bytes": 0,
                "loading_allowed": False,
            }
        records.append(
            {
                "path": item["path"],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
            }
        )
    records.sort(key=lambda item: item["path"])
    candidate_digest = canonical_digest({"format": CONTEXT_FORMAT, "files": records})
    return {
        "format": CONTEXT_FORMAT,
        "candidate_digest": candidate_digest,
        "accepted_digest": None,
        "file_count": len(records),
        "total_bytes": sum(item["bytes"] for item in records),
        "loading_allowed": False,
    }


def _binding_payload(
    report: Dict[str, Any],
    exceptions: List[Dict[str, Any]],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    security = report.get("security_report")
    security_findings = security.get("findings", []) if isinstance(security, dict) else []
    policy_digest = (
        security.get("provenance", {}).get("policy_digest")
        if isinstance(security, dict)
        else None
    )
    bindings = {
        "source_digest": report.get("source", {}).get("sha256"),
        "inventory_digest": canonical_digest(report.get("inventory")),
        "policy_digest": policy_digest,
        "findings_digest": canonical_digest(
            {
                "boundary": report.get("boundary_findings"),
                "security": security_findings,
            }
        ),
        "exceptions_digest": canonical_digest(exceptions),
        "context_digest": context["candidate_digest"],
        "intake_digest": canonical_digest(report),
    }
    bindings["review_basis_digest"] = canonical_digest(bindings)
    return bindings


def _validate_bindings(bindings: Any) -> None:
    expected_keys = {
        "source_digest",
        "inventory_digest",
        "policy_digest",
        "findings_digest",
        "exceptions_digest",
        "context_digest",
        "intake_digest",
        "review_basis_digest",
    }
    _require(isinstance(bindings, dict), "bindings must be an object")
    _require(set(bindings) == expected_keys, "bindings have an invalid contract")
    _require(_is_sha256(bindings["source_digest"], nullable=True), "source binding is invalid")
    _require(_is_sha256(bindings["policy_digest"], nullable=True), "policy binding is invalid")
    _require(_is_sha256(bindings["context_digest"], nullable=True), "context binding is invalid")
    for name in (
        "inventory_digest",
        "findings_digest",
        "exceptions_digest",
        "intake_digest",
        "review_basis_digest",
    ):
        _require(_is_sha256(bindings[name]), f"{name} is invalid")
    basis = {key: value for key, value in bindings.items() if key != "review_basis_digest"}
    _require(
        bindings["review_basis_digest"] == canonical_digest(basis),
        "review basis digest mismatch",
    )


def validate_decision(
    decision: Dict[str, Any],
    bindings: Dict[str, Any],
    active_finding_digests: List[str],
    accepted_exception_ids: List[str],
    intake_status: str,
) -> None:
    expected_keys = {
        "$schema",
        "schema_version",
        "reviewer_id",
        "reviewer_role",
        "reviewed_on",
        "disposition",
        "bindings",
        "acknowledged_finding_digests",
        "acknowledged_exception_ids",
        "rationale",
    }
    _require(isinstance(decision, dict), "reviewer decision must be an object")
    _require(set(decision) == expected_keys, "reviewer decision has an invalid contract")
    _require(decision["$schema"] == DECISION_SCHEMA_URL, "reviewer decision schema mismatch")
    _require(decision["schema_version"] == "0.1.0", "unsupported decision schema version")
    _require(
        isinstance(decision["reviewer_id"], str)
        and REVIEWER_RE.fullmatch(decision["reviewer_id"]) is not None,
        "reviewer_id must be a public-safe identifier",
    )
    _require(decision["reviewer_role"] == "maintainer-intake", "reviewer_role mismatch")
    _require(
        isinstance(decision["reviewed_on"], str)
        and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", decision["reviewed_on"])
        is not None,
        "reviewed_on must be an ISO 8601 date",
    )
    try:
        date.fromisoformat(decision["reviewed_on"])
    except (TypeError, ValueError) as exc:
        raise IntakeReceiptError("reviewed_on must be an ISO 8601 date") from exc
    _require(
        decision["disposition"] in {"accept", "request-changes", "reject"},
        "reviewer disposition is invalid",
    )
    _validate_bindings(decision["bindings"])
    _require(decision["bindings"] == bindings, "reviewer decision has stale evidence bindings")

    acknowledged_findings = decision["acknowledged_finding_digests"]
    _require(
        isinstance(acknowledged_findings, list)
        and acknowledged_findings == sorted(set(acknowledged_findings))
        and all(_is_sha256(item) for item in acknowledged_findings),
        "acknowledged finding digests must be sorted, unique SHA-256 values",
    )
    _require(
        set(acknowledged_findings).issubset(active_finding_digests),
        "reviewer decision acknowledges an unknown or inactive finding",
    )
    acknowledged_exceptions = decision["acknowledged_exception_ids"]
    _require(
        isinstance(acknowledged_exceptions, list)
        and acknowledged_exceptions == sorted(set(acknowledged_exceptions))
        and all(isinstance(item, str) and bool(item) for item in acknowledged_exceptions),
        "acknowledged exception ids must be sorted and unique",
    )
    _require(
        set(acknowledged_exceptions).issubset(accepted_exception_ids),
        "reviewer decision acknowledges an unknown exception",
    )
    rationale = decision["rationale"]
    _require(
        isinstance(rationale, str)
        and 1 <= len(rationale) <= 1000
        and not any(ord(character) < 32 and character not in "\n\t" for character in rationale),
        "rationale must be 1-1000 public-safe text characters",
    )

    if decision["disposition"] == "accept":
        _require(intake_status != "blocked", "a blocked intake cannot be accepted")
        _require(bindings["context_digest"] is not None, "accepted context is unavailable")
        _require(
            acknowledged_findings == active_finding_digests,
            "acceptance must acknowledge every active finding digest",
        )
        _require(
            acknowledged_exceptions == accepted_exception_ids,
            "acceptance must acknowledge every accepted policy exception",
        )


def _limits_are_bounded(limits: Dict[str, Any]) -> bool:
    defaults = DEFAULT_LIMITS.__dict__
    return set(limits) == set(defaults) and all(
        isinstance(limits[name], int)
        and 0 < limits[name] <= defaults[name]
        for name in defaults
    )


def _derive_receipt(
    report: Dict[str, Any],
    decision: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    report = _portable_intake_report(report)
    try:
        intake_status = report["summary"]["status"]
        limits = report["limits"]
    except (KeyError, TypeError) as exc:
        raise IntakeReceiptError("intake report has an invalid summary contract") from exc
    _require(
        intake_status in {"ready-for-review", "review-required", "blocked"},
        "intake status is invalid",
    )
    _require(_limits_are_bounded(limits), "receipt intake limits exceed the accepted boundary")

    exceptions = _accepted_exceptions(report)
    context = _candidate_context(report)
    bindings = _binding_payload(report, exceptions, context)
    active_findings = _active_finding_digests(report)
    exception_ids = sorted(item["id"] for item in exceptions)

    if decision is not None:
        validate_decision(
            decision,
            bindings,
            active_findings,
            exception_ids,
            intake_status,
        )

    if intake_status == "blocked" or (
        decision is not None and decision["disposition"] == "reject"
    ):
        status = "blocked"
    elif decision is not None and decision["disposition"] == "accept":
        status = "accepted"
    else:
        status = "review-required"

    if status == "accepted":
        context["accepted_digest"] = context["candidate_digest"]
        context["loading_allowed"] = True

    receipt = {
        "$schema": RECEIPT_SCHEMA_URL,
        "schema_version": "0.1.0",
        "engine": {"name": RECEIPT_NAME, "version": RECEIPT_VERSION},
        "intake_report": report,
        "bindings": bindings,
        "accepted_exceptions": exceptions,
        "reviewer_decision": copy.deepcopy(decision),
        "accepted_context": context,
        "summary": {
            "status": status,
            "intake_status": intake_status,
            "reviewer_disposition": decision["disposition"] if decision else None,
            "context_loading_allowed": status == "accepted",
            "scanner_pass_establishes_domain_correctness": False,
            "domain_review_complete": False,
            "independent_review_complete": False,
        },
    }
    receipt["receipt_digest"] = canonical_digest(receipt)
    return receipt


def create_receipt(
    source: Path,
    policy_path: Optional[Path] = None,
    decision: Optional[Dict[str, Any]] = None,
    limits: IntakeLimits = DEFAULT_LIMITS,
    temp_parent: Optional[Path] = None,
) -> Dict[str, Any]:
    """Create a deterministic receipt from one fresh quarantined intake."""

    report = intake_package(
        source,
        policy_path=policy_path,
        limits=limits,
        temp_parent=temp_parent,
    )
    return _derive_receipt(report, decision)


def validate_receipt(receipt: Dict[str, Any]) -> None:
    """Validate one receipt's closed contract and all internal bindings."""

    expected_keys = {
        "$schema",
        "schema_version",
        "engine",
        "intake_report",
        "bindings",
        "accepted_exceptions",
        "reviewer_decision",
        "accepted_context",
        "summary",
        "receipt_digest",
    }
    _require(isinstance(receipt, dict), "receipt must be an object")
    _require(set(receipt) == expected_keys, "receipt has an invalid top-level contract")
    _require(receipt["$schema"] == RECEIPT_SCHEMA_URL, "receipt schema mismatch")
    _require(receipt["schema_version"] == "0.1.0", "unsupported receipt schema version")
    _require(
        receipt["engine"] == {"name": RECEIPT_NAME, "version": RECEIPT_VERSION},
        "receipt engine mismatch",
    )
    _require(_is_sha256(receipt["receipt_digest"]), "receipt digest is invalid")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_digest"}
    _require(
        receipt["receipt_digest"] == canonical_digest(unsigned),
        "receipt digest mismatch",
    )
    expected = _derive_receipt(receipt["intake_report"], receipt["reviewer_decision"])
    _require(expected == receipt, "receipt evidence or disposition binding mismatch")


def _stale_reason(stored: Dict[str, Any], current: Dict[str, Any]) -> str:
    if stored.get("inventory") != current.get("inventory"):
        return "stale inventory binding"
    stored_security = stored.get("security_report")
    current_security = current.get("security_report")
    stored_exceptions = _accepted_exceptions(stored)
    current_exceptions = _accepted_exceptions(current)
    if stored_exceptions != current_exceptions:
        return "stale exception binding"
    stored_policy = (
        stored_security.get("policy") if isinstance(stored_security, dict) else None
    )
    current_policy = (
        current_security.get("policy") if isinstance(current_security, dict) else None
    )
    if stored_policy != current_policy:
        return "stale policy binding"
    if stored.get("source") != current.get("source"):
        return "stale source binding"
    stored_findings = (
        stored.get("boundary_findings"),
        stored_security.get("findings") if isinstance(stored_security, dict) else None,
    )
    current_findings = (
        current.get("boundary_findings"),
        current_security.get("findings") if isinstance(current_security, dict) else None,
    )
    if stored_findings != current_findings:
        return "stale findings binding"
    return "stale intake, scanner, or policy binding"


def verify_receipt(
    receipt: Dict[str, Any],
    source: Path,
    policy_path: Optional[Path] = None,
    temp_parent: Optional[Path] = None,
) -> Dict[str, Any]:
    """Re-run intake and reject any stale receipt evidence binding."""

    validate_receipt(receipt)
    try:
        limits = IntakeLimits(**receipt["intake_report"]["limits"])
    except (KeyError, TypeError) as exc:
        raise IntakeReceiptError("receipt intake limits are invalid") from exc
    current = _portable_intake_report(
        intake_package(
            source,
            policy_path=policy_path,
            limits=limits,
            temp_parent=temp_parent,
        )
    )
    if current != receipt["intake_report"]:
        raise IntakeReceiptError(_stale_reason(receipt["intake_report"], current))
    return {
        "ok": True,
        "status": receipt["summary"]["status"],
        "receipt_digest": receipt["receipt_digest"],
        "source_digest": receipt["bindings"]["source_digest"],
        "inventory_digest": receipt["bindings"]["inventory_digest"],
        "policy_digest": receipt["bindings"]["policy_digest"],
        "context_digest": receipt["accepted_context"]["accepted_digest"],
        "context_loading_allowed": receipt["summary"]["context_loading_allowed"],
        "domain_correctness_established": False,
    }


def text_report(receipt: Dict[str, Any]) -> str:
    summary = receipt["summary"]
    review = receipt["reviewer_decision"]
    context = receipt["accepted_context"]
    lines = [
        f"Community intake receipt: {summary['status'].upper()}",
        f"Receipt digest: {receipt['receipt_digest']}",
        f"Source digest: {receipt['bindings']['source_digest'] or 'unavailable'}",
        f"Inventory digest: {receipt['bindings']['inventory_digest']}",
        f"Policy digest: {receipt['bindings']['policy_digest'] or 'unavailable'}",
    ]
    if review:
        lines.append(
            f"Maintainer disposition: {review['disposition']} by {review['reviewer_id']} "
            f"on {review['reviewed_on']}"
        )
    else:
        lines.append("Maintainer disposition: pending")
    lines.append(
        "Accepted context: "
        + (context["accepted_digest"] or "disabled pending exact reviewed acceptance")
    )
    lines.append("Static intake does not establish domain correctness or independent review.")
    return "\n".join(lines)


def write_json_artifact(path: Path, payload: Dict[str, Any]) -> None:
    try:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        raise IntakeReceiptError(f"cannot write receipt {path.name}: {exc}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and verify deterministic community intake receipts"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="Create a fresh intake receipt")
    create.add_argument("source", help="Community directory, ZIP, or TAR input")
    create.add_argument("--policy", type=Path, help="External strengthening policy")
    create.add_argument("--decision", type=Path, help="External reviewer decision JSON")
    create.add_argument("--output", type=Path, help="Write the receipt to this external path")
    create.add_argument("--json", action="store_true", help="Emit the full JSON receipt")
    verify = subparsers.add_parser("verify", help="Verify a receipt against fresh intake")
    verify.add_argument("receipt", type=Path, help="Receipt JSON to verify")
    verify.add_argument("--source", required=True, type=Path, help="Contribution source")
    verify.add_argument("--policy", type=Path, help="External strengthening policy")
    verify.add_argument("--json", action="store_true", help="Emit JSON verification")
    return parser


def run_cli(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "create":
            source = args.source if isinstance(args.source, Path) else Path(args.source)
            decision = None
            if args.decision:
                ensure_external_artifact(source, args.decision, "reviewer decision")
                decision = load_json_artifact(args.decision, "reviewer decision")
            receipt = create_receipt(source, policy_path=args.policy, decision=decision)
            if args.output:
                ensure_external_artifact(source, args.output, "intake receipt")
                write_json_artifact(args.output, receipt)
            if args.json:
                print(json.dumps(receipt, indent=2, sort_keys=True))
            else:
                print(text_report(receipt))
            return 1 if receipt["summary"]["status"] == "blocked" else 0

        source = args.source
        ensure_external_artifact(source, args.receipt, "intake receipt")
        receipt = load_json_artifact(args.receipt, "intake receipt")
        verification = verify_receipt(receipt, source, policy_path=args.policy)
        if args.json:
            print(json.dumps(verification, indent=2, sort_keys=True))
        else:
            print(
                f"Intake receipt verified: {verification['status'].upper()} "
                f"({verification['receipt_digest']})"
            )
        return 1 if verification["status"] == "blocked" else 0
    except (
        FileNotFoundError,
        IntakeError,
        IntakeReceiptError,
        OSError,
        SecurityPolicyError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
