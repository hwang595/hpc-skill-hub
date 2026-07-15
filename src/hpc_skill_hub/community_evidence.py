"""Independent review and adoption evidence for accepted community intake."""

from __future__ import annotations

import argparse
import copy
import ipaddress
import json
import os
import re
import stat
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

from .intake import IntakeError
from .intake_receipt import (
    IntakeReceiptError,
    ensure_external_artifact,
    validate_receipt,
    verify_receipt,
)
from .security_policy import SecurityPolicyError, canonical_digest


SCHEMA_VERSION = "0.1.0"
GENERATED_BY = "hpc-skill-community-evidence@0.1.0"
PACKET_SCHEMA_URL = (
    "https://hpc-skill-hub.org/schemas/community-skill-review-packet.schema.json"
)
REVIEW_SCHEMA_URL = (
    "https://hpc-skill-hub.org/schemas/community-skill-independent-review.schema.json"
)
ADOPTION_SCHEMA_URL = (
    "https://hpc-skill-hub.org/schemas/community-skill-adoption-report.schema.json"
)
STATUS_SCHEMA_URL = (
    "https://hpc-skill-hub.org/schemas/community-skill-evidence-status.schema.json"
)
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PUBLIC_ID_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,62}[A-Za-z0-9])?$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
RISK_LEVELS = {"low", "medium", "high"}
REVIEW_SCOPES = {"domain", "safety"}
REVIEW_DECISIONS = {"approved", "changes-requested", "rejected"}
ADOPTION_SCOPES = {
    "documentation-review",
    "dry-run",
    "smoke-test",
    "workflow-pilot",
    "production-use",
}
ADOPTION_OUTCOMES = {"successful", "partial", "blocked"}
ENVIRONMENT_TYPES = {
    "campus-hpc",
    "training-cluster",
    "cloud-hpc",
    "lab-managed-cluster",
    "container-test",
    "other-public",
}
SCHEDULERS = {"slurm", "pbs", "lsf", "htcondor", "grid-engine", "none", "other"}
REVIEW_QUESTIONS = [
    "Does the contribution solve one clear task for the declared domains?",
    "Are scheduler, storage, module, container, account, and network assumptions explicit?",
    "Are examples conservative about resources, cost, data movement, cleanup, and side effects?",
    "Does the declared risk cover the most powerful documented behavior?",
    "Are public references sufficient to assess portability and current behavior?",
    "Are private site details absent and local policy kept in site adapters?",
]
OWNER_ROLES = {
    "intake_acceptance": "maintainer-intake",
    "domain_review": "independent-domain-reviewer",
    "safety_review": "independent-safety-reviewer",
    "adoption_evidence": "independent-adopter",
    "maturity_promotion": "registry-maintainer",
}
CHECKLIST_KEYS = {
    "source_digest_verified",
    "scope_and_assumptions_reviewed",
    "examples_and_side_effects_reviewed",
    "risk_and_site_boundaries_reviewed",
    "references_reviewed",
    "public_safe_evidence_attested",
}
MAX_EVIDENCE_ARTIFACT_BYTES = 16_000_000


class CommunityEvidenceError(ValueError):
    """Raised when community review or adoption evidence is invalid or stale."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommunityEvidenceError(message)


def load_evidence_artifact(path: Path, label: str) -> Dict[str, Any]:
    """Load one bounded regular JSON file without following a pre-existing link."""

    try:
        before = path.lstat()
        _require(stat.S_ISREG(before.st_mode), f"{label} must be a regular file")
        _require(
            before.st_size <= MAX_EVIDENCE_ARTIFACT_BYTES,
            f"{label} exceeds {MAX_EVIDENCE_ARTIFACT_BYTES} bytes",
        )
        with path.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            _require(
                (opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
                f"{label} changed while opening",
            )
            encoded = handle.read(MAX_EVIDENCE_ARTIFACT_BYTES + 1)
            after = os.fstat(handle.fileno())
        _require(
            len(encoded) <= MAX_EVIDENCE_ARTIFACT_BYTES,
            f"{label} exceeds {MAX_EVIDENCE_ARTIFACT_BYTES} bytes",
        )
        _require(
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            == (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns),
            f"{label} changed while reading",
        )
        payload = json.loads(encoded.decode("utf-8"))
    except CommunityEvidenceError:
        raise
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CommunityEvidenceError(f"cannot read {label} {path.name}: {exc}") from exc
    _require(isinstance(payload, dict), f"{label} must be a JSON object")
    return payload


def add_artifact_digest(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Attach the canonical drift-detection digest required by a review or report."""

    _require(isinstance(payload, dict), "evidence artifact must be an object")
    schema = payload.get("$schema")
    if schema == REVIEW_SCHEMA_URL:
        digest_field = "review_digest"
    elif schema == ADOPTION_SCHEMA_URL:
        digest_field = "report_digest"
    else:
        raise CommunityEvidenceError(
            "digest supports only independent review or adoption report schemas"
        )
    normalized = copy.deepcopy(payload)
    normalized.pop(digest_field, None)
    normalized[digest_field] = canonical_digest(normalized)
    return normalized


def _sha256(value: Any, label: str, *, nullable: bool = False) -> None:
    _require(
        (nullable and value is None)
        or (isinstance(value, str) and SHA256_RE.fullmatch(value) is not None),
        f"{label} must be a lowercase SHA-256 digest",
    )


def _public_id(value: Any, label: str) -> None:
    _require(
        isinstance(value, str) and PUBLIC_ID_RE.fullmatch(value) is not None,
        f"{label} must be a public-safe identifier",
    )


def _iso_date(value: Any, label: str) -> date:
    _require(
        isinstance(value, str) and DATE_RE.fullmatch(value) is not None,
        f"{label} must use YYYY-MM-DD",
    )
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CommunityEvidenceError(f"{label} must be a valid date") from exc


def _public_text(value: Any, label: str, *, maximum: int = 1000) -> None:
    _require(
        isinstance(value, str)
        and 1 <= len(value) <= maximum
        and not any(
            ord(character) < 32 and character not in "\n\t" for character in value
        ),
        f"{label} must be 1-{maximum} public-safe text characters",
    )


def _https_url(value: Any, label: str) -> None:
    _require(
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and not any(character.isspace() for character in value),
        f"{label} must be a public HTTPS URL",
    )
    parsed = urlparse(value)
    _require(
        parsed.scheme == "https"
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None,
        f"{label} must be a public HTTPS URL without credentials",
    )
    hostname = (parsed.hostname or "").lower()
    _require(
        hostname not in {"localhost", "localhost.localdomain"},
        f"{label} cannot use localhost",
    )
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        _require(
            "." in hostname
            and not hostname.endswith((".local", ".internal", ".localhost", ".invalid")),
            f"{label} must use a public DNS name",
        )
        return
    _require(
        address.is_global,
        f"{label} cannot use a private, loopback, link-local, or reserved address",
    )


def _sorted_unique_strings(
    values: Any,
    label: str,
    *,
    allow_empty: bool = True,
    identifiers: bool = False,
) -> List[str]:
    _require(isinstance(values, list), f"{label} must be an array")
    _require(allow_empty or bool(values), f"{label} must not be empty")
    _require(
        all(isinstance(value, str) and bool(value) for value in values),
        f"{label} must contain non-empty strings",
    )
    _require(values == sorted(set(values)), f"{label} must be sorted and unique")
    if identifiers:
        _require(
            all(ID_RE.fullmatch(value) is not None for value in values),
            f"{label} contains an invalid identifier",
        )
    return values


def _contribution(
    contribution_id: Any,
    version: Any,
    risk_level: Any,
    domains: Any,
    submitter_id: Any,
    artifact_url: Any,
) -> Dict[str, Any]:
    _require(
        isinstance(contribution_id, str)
        and ID_RE.fullmatch(contribution_id) is not None,
        "contribution id is invalid",
    )
    _require(
        isinstance(version, str) and VERSION_RE.fullmatch(version) is not None,
        "contribution version is invalid",
    )
    _require(
        isinstance(risk_level, str) and risk_level in RISK_LEVELS,
        "risk level is invalid",
    )
    _require(
        isinstance(domains, (list, tuple)),
        "contribution domains must be an array",
    )
    _require(
        all(isinstance(domain, str) and bool(domain) for domain in domains),
        "contribution domains must contain non-empty strings",
    )
    normalized_domains = sorted(set(domains))
    _sorted_unique_strings(
        normalized_domains,
        "contribution domains",
        allow_empty=False,
        identifiers=True,
    )
    _public_id(submitter_id, "submitter_id")
    _https_url(artifact_url, "artifact_url")
    return {
        "id": contribution_id,
        "version": version,
        "risk_level": risk_level,
        "domains": normalized_domains,
        "submitter_id": submitter_id,
        "artifact_url": artifact_url,
    }


def _packet_bindings(receipt: Dict[str, Any], contribution: Dict[str, Any]) -> Dict[str, Any]:
    bindings = {
        "receipt_digest": receipt["receipt_digest"],
        "source_digest": receipt["bindings"]["source_digest"],
        "inventory_digest": receipt["bindings"]["inventory_digest"],
        "policy_digest": receipt["bindings"]["policy_digest"],
        "context_digest": receipt["accepted_context"]["accepted_digest"],
        "contribution_record_digest": canonical_digest(contribution),
    }
    bindings["review_basis_digest"] = canonical_digest(bindings)
    return bindings


def _derive_packet(receipt: Dict[str, Any], contribution: Dict[str, Any]) -> Dict[str, Any]:
    validate_receipt(receipt)
    _require(receipt["summary"]["status"] == "accepted", "P3 requires an accepted P2 receipt")
    decision = receipt["reviewer_decision"]
    _require(
        isinstance(decision, dict) and decision.get("disposition") == "accept",
        "P3 requires an exact maintainer intake acceptance",
    )
    _require(
        receipt["accepted_context"]["loading_allowed"] is True
        and receipt["accepted_context"]["accepted_digest"] is not None,
        "P3 requires an accepted context digest",
    )
    exceptions = [item["id"] for item in receipt["accepted_exceptions"]]
    bindings = _packet_bindings(receipt, contribution)
    packet = {
        "$schema": PACKET_SCHEMA_URL,
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "contribution": copy.deepcopy(contribution),
        "intake": {
            "status": "accepted",
            "receipt_digest": receipt["receipt_digest"],
            "maintainer_id": decision["reviewer_id"],
            "reviewed_on": decision["reviewed_on"],
            "policy_digest": receipt["bindings"]["policy_digest"],
            "accepted_exception_ids": exceptions,
        },
        "bindings": bindings,
        "requirements": {
            "domain_review_required": True,
            "safety_review_required": contribution["risk_level"] != "low",
            "adoption_evidence_required_for_field_tested": True,
            "maturity_decision_required": True,
        },
        "owners": copy.deepcopy(OWNER_ROLES),
        "review_questions": list(REVIEW_QUESTIONS),
        "summary": {
            "status": "awaiting-independent-review",
            "domain_review_complete": False,
            "safety_review_complete": False,
            "adoption_evidence_recorded": False,
            "maturity_promotion_authorized": False,
        },
    }
    packet["packet_digest"] = canonical_digest(packet)
    return packet


def create_review_packet(
    receipt: Dict[str, Any],
    source: Path,
    *,
    contribution_id: str,
    version: str,
    risk_level: str,
    domains: Sequence[str],
    submitter_id: str,
    artifact_url: str,
    policy_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Verify fresh P2 evidence and create a deterministic P3 review packet."""

    verification = verify_receipt(receipt, source, policy_path=policy_path)
    _require(verification["status"] == "accepted", "P3 requires an accepted P2 receipt")
    contribution = _contribution(
        contribution_id,
        version,
        risk_level,
        domains,
        submitter_id,
        artifact_url,
    )
    return _derive_packet(receipt, contribution)


def validate_review_packet(packet: Dict[str, Any]) -> None:
    expected_keys = {
        "$schema",
        "schema_version",
        "generated_by",
        "contribution",
        "intake",
        "bindings",
        "requirements",
        "owners",
        "review_questions",
        "summary",
        "packet_digest",
    }
    _require(isinstance(packet, dict), "review packet must be an object")
    _require(set(packet) == expected_keys, "review packet has an invalid top-level contract")
    _require(packet["$schema"] == PACKET_SCHEMA_URL, "review packet schema mismatch")
    _require(packet["schema_version"] == SCHEMA_VERSION, "unsupported packet schema version")
    _require(packet["generated_by"] == GENERATED_BY, "review packet generator mismatch")
    _sha256(packet["packet_digest"], "packet_digest")
    unsigned = {key: value for key, value in packet.items() if key != "packet_digest"}
    _require(packet["packet_digest"] == canonical_digest(unsigned), "review packet digest mismatch")

    contribution = packet["contribution"]
    _require(isinstance(contribution, dict), "contribution must be an object")
    _require(
        contribution
        == _contribution(
            contribution.get("id"),
            contribution.get("version"),
            contribution.get("risk_level"),
            contribution.get("domains", []),
            contribution.get("submitter_id"),
            contribution.get("artifact_url"),
        ),
        "contribution contract mismatch",
    )
    intake = packet["intake"]
    _require(
        isinstance(intake, dict)
        and set(intake)
        == {
            "status",
            "receipt_digest",
            "maintainer_id",
            "reviewed_on",
            "policy_digest",
            "accepted_exception_ids",
        },
        "intake evidence has an invalid contract",
    )
    _require(intake["status"] == "accepted", "intake evidence is not accepted")
    _sha256(intake["receipt_digest"], "intake.receipt_digest")
    _public_id(intake["maintainer_id"], "intake.maintainer_id")
    _iso_date(intake["reviewed_on"], "intake.reviewed_on")
    _sha256(intake["policy_digest"], "intake.policy_digest", nullable=True)
    _sorted_unique_strings(
        intake["accepted_exception_ids"],
        "intake.accepted_exception_ids",
        identifiers=True,
    )

    bindings = packet["bindings"]
    _require(
        isinstance(bindings, dict)
        and set(bindings)
        == {
            "receipt_digest",
            "source_digest",
            "inventory_digest",
            "policy_digest",
            "context_digest",
            "contribution_record_digest",
            "review_basis_digest",
        },
        "packet bindings have an invalid contract",
    )
    for name in (
        "receipt_digest",
        "source_digest",
        "inventory_digest",
        "context_digest",
        "contribution_record_digest",
        "review_basis_digest",
    ):
        _sha256(bindings[name], f"bindings.{name}")
    _sha256(bindings["policy_digest"], "bindings.policy_digest", nullable=True)
    _require(bindings["receipt_digest"] == intake["receipt_digest"], "receipt binding mismatch")
    _require(bindings["policy_digest"] == intake["policy_digest"], "policy binding mismatch")
    _require(
        bindings["contribution_record_digest"] == canonical_digest(contribution),
        "contribution record digest mismatch",
    )
    basis = {key: value for key, value in bindings.items() if key != "review_basis_digest"}
    _require(
        bindings["review_basis_digest"] == canonical_digest(basis),
        "review basis digest mismatch",
    )
    expected_requirements = {
        "domain_review_required": True,
        "safety_review_required": contribution["risk_level"] != "low",
        "adoption_evidence_required_for_field_tested": True,
        "maturity_decision_required": True,
    }
    _require(packet["requirements"] == expected_requirements, "review requirements mismatch")
    _require(packet["owners"] == OWNER_ROLES, "evidence owner roles mismatch")
    _require(packet["review_questions"] == REVIEW_QUESTIONS, "review questions mismatch")
    _require(
        packet["summary"]
        == {
            "status": "awaiting-independent-review",
            "domain_review_complete": False,
            "safety_review_complete": False,
            "adoption_evidence_recorded": False,
            "maturity_promotion_authorized": False,
        },
        "review packet summary mismatch",
    )


def verify_review_packet(
    packet: Dict[str, Any],
    receipt: Dict[str, Any],
    source: Path,
    policy_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Re-run P2 verification and reject a stale or substituted review packet."""

    validate_review_packet(packet)
    contribution = packet["contribution"]
    expected = create_review_packet(
        receipt,
        source,
        contribution_id=contribution["id"],
        version=contribution["version"],
        risk_level=contribution["risk_level"],
        domains=contribution["domains"],
        submitter_id=contribution["submitter_id"],
        artifact_url=contribution["artifact_url"],
        policy_path=policy_path,
    )
    _require(expected == packet, "review packet has stale receipt or source bindings")
    return {
        "ok": True,
        "packet_digest": packet["packet_digest"],
        "receipt_digest": packet["bindings"]["receipt_digest"],
        "source_digest": packet["bindings"]["source_digest"],
        "context_digest": packet["bindings"]["context_digest"],
    }


def evidence_bindings(packet: Dict[str, Any]) -> Dict[str, Any]:
    validate_review_packet(packet)
    return {
        "packet_digest": packet["packet_digest"],
        "receipt_digest": packet["bindings"]["receipt_digest"],
        "source_digest": packet["bindings"]["source_digest"],
        "inventory_digest": packet["bindings"]["inventory_digest"],
        "context_digest": packet["bindings"]["context_digest"],
        "contribution_record_digest": packet["bindings"]["contribution_record_digest"],
        "review_basis_digest": packet["bindings"]["review_basis_digest"],
    }


def _validate_evidence_bindings(values: Any, packet: Dict[str, Any], label: str) -> None:
    _require(isinstance(values, dict), f"{label} bindings must be an object")
    for name, value in values.items():
        _sha256(value, f"{label}.bindings.{name}")
    _require(values == evidence_bindings(packet), f"{label} has stale packet bindings")


def validate_independent_review(review: Dict[str, Any], packet: Dict[str, Any]) -> None:
    validate_review_packet(packet)
    expected_keys = {
        "$schema",
        "schema_version",
        "review_id",
        "contribution",
        "scope",
        "reviewer_id",
        "reviewed_on",
        "domain",
        "decision",
        "independence_attestation",
        "conflict_disclosure",
        "evidence_url",
        "checklist",
        "bindings",
        "notes",
        "review_digest",
    }
    _require(isinstance(review, dict), "independent review must be an object")
    _require(set(review) == expected_keys, "independent review has an invalid contract")
    _require(review["$schema"] == REVIEW_SCHEMA_URL, "independent review schema mismatch")
    _require(review["schema_version"] == SCHEMA_VERSION, "unsupported review schema version")
    _public_id(review["review_id"], "review_id")
    _require(
        review["contribution"]
        == {"id": packet["contribution"]["id"], "version": packet["contribution"]["version"]},
        "review contribution version binding mismatch",
    )
    _require(review["scope"] in REVIEW_SCOPES, "review scope is invalid")
    _public_id(review["reviewer_id"], "reviewer_id")
    _require(
        review["reviewer_id"]
        not in {packet["contribution"]["submitter_id"], packet["intake"]["maintainer_id"]},
        "independent reviewer cannot be the submitter or intake decision maker",
    )
    reviewed_on = _iso_date(review["reviewed_on"], "reviewed_on")
    _require(
        reviewed_on >= _iso_date(packet["intake"]["reviewed_on"], "intake.reviewed_on"),
        "independent review predates intake acceptance",
    )
    _require(
        isinstance(review["domain"], str) and ID_RE.fullmatch(review["domain"]),
        "review domain is invalid",
    )
    if review["scope"] == "domain":
        _require(
            review["domain"] in packet["contribution"]["domains"],
            "review domain is out of scope",
        )
    else:
        _require(review["domain"] == "safety", "safety review domain must be safety")
    _require(review["decision"] in REVIEW_DECISIONS, "review decision is invalid")
    _require(review["independence_attestation"] is True, "independence attestation is required")
    _public_text(review["conflict_disclosure"], "conflict_disclosure", maximum=500)
    _https_url(review["evidence_url"], "evidence_url")
    checklist = review["checklist"]
    _require(
        isinstance(checklist, dict)
        and set(checklist) == CHECKLIST_KEYS
        and all(type(value) is bool for value in checklist.values()),
        "review checklist has an invalid contract",
    )
    if review["decision"] == "approved":
        _require(all(checklist.values()), "approved review requires every checklist item")
    _validate_evidence_bindings(review["bindings"], packet, "review")
    _public_text(review["notes"], "review notes")
    _sha256(review["review_digest"], "review_digest")
    unsigned = {key: value for key, value in review.items() if key != "review_digest"}
    _require(review["review_digest"] == canonical_digest(unsigned), "review digest mismatch")


def validate_adoption_report(report: Dict[str, Any], packet: Dict[str, Any]) -> None:
    validate_review_packet(packet)
    expected_keys = {
        "$schema",
        "schema_version",
        "report_id",
        "contribution",
        "adopter_id",
        "reported_on",
        "scope",
        "outcome",
        "environment",
        "observations",
        "evidence_url",
        "bindings",
        "independent_adopter_attestation",
        "public_safe_attestation",
        "no_maturity_claim",
        "report_digest",
    }
    _require(isinstance(report, dict), "adoption report must be an object")
    _require(set(report) == expected_keys, "adoption report has an invalid contract")
    _require(report["$schema"] == ADOPTION_SCHEMA_URL, "adoption report schema mismatch")
    _require(report["schema_version"] == SCHEMA_VERSION, "unsupported adoption schema version")
    _public_id(report["report_id"], "report_id")
    _require(
        report["contribution"]
        == {"id": packet["contribution"]["id"], "version": packet["contribution"]["version"]},
        "adoption contribution version binding mismatch",
    )
    _public_id(report["adopter_id"], "adopter_id")
    _require(
        report["adopter_id"]
        not in {packet["contribution"]["submitter_id"], packet["intake"]["maintainer_id"]},
        "independent adopter cannot be the submitter or intake decision maker",
    )
    reported_on = _iso_date(report["reported_on"], "reported_on")
    _require(
        reported_on >= _iso_date(packet["intake"]["reviewed_on"], "intake.reviewed_on"),
        "adoption report predates intake acceptance",
    )
    _require(report["scope"] in ADOPTION_SCOPES, "adoption scope is invalid")
    _require(report["outcome"] in ADOPTION_OUTCOMES, "adoption outcome is invalid")
    environment = report["environment"]
    _require(
        isinstance(environment, dict)
        and set(environment)
        == {
            "type",
            "scheduler",
            "site_adapter_id",
            "public_documentation_urls",
            "private_details_omitted",
        },
        "adoption environment has an invalid contract",
    )
    _require(environment["type"] in ENVIRONMENT_TYPES, "environment type is invalid")
    _require(environment["scheduler"] in SCHEDULERS, "environment scheduler is invalid")
    _require(
        environment["site_adapter_id"] is None
        or (
            isinstance(environment["site_adapter_id"], str)
            and ID_RE.fullmatch(environment["site_adapter_id"]) is not None
        ),
        "site_adapter_id is invalid",
    )
    urls = _sorted_unique_strings(
        environment["public_documentation_urls"],
        "public_documentation_urls",
    )
    for index, url in enumerate(urls):
        _https_url(url, f"public_documentation_urls[{index}]")
    _require(environment["private_details_omitted"] is True, "private details must be omitted")
    observations = report["observations"]
    _require(
        isinstance(observations, dict)
        and set(observations) == {"worked", "changes_required", "blockers", "follow_up_urls"},
        "adoption observations have an invalid contract",
    )
    for name in ("worked", "changes_required", "blockers"):
        values = _sorted_unique_strings(observations[name], f"observations.{name}")
        _require(len(values) <= 10, f"observations.{name} exceeds 10 items")
        for index, value in enumerate(values):
            _public_text(value, f"observations.{name}[{index}]", maximum=500)
    follow_ups = _sorted_unique_strings(observations["follow_up_urls"], "observations.follow_up_urls")
    for index, url in enumerate(follow_ups):
        _https_url(url, f"observations.follow_up_urls[{index}]")
    if report["outcome"] == "successful":
        _require(bool(observations["worked"]), "successful adoption must record what worked")
    if report["outcome"] == "blocked":
        _require(bool(observations["blockers"]), "blocked adoption must record blockers")
    _https_url(report["evidence_url"], "evidence_url")
    _validate_evidence_bindings(report["bindings"], packet, "adoption report")
    _require(
        report["independent_adopter_attestation"] is True,
        "independent adopter attestation is required",
    )
    _require(report["public_safe_attestation"] is True, "public-safe attestation is required")
    _require(report["no_maturity_claim"] is True, "adoption report cannot claim maturity promotion")
    _sha256(report["report_digest"], "report_digest")
    unsigned = {key: value for key, value in report.items() if key != "report_digest"}
    _require(report["report_digest"] == canonical_digest(unsigned), "adoption report digest mismatch")


def _scope_state(reviews: List[Dict[str, Any]], scope: str) -> str:
    decisions = [item["decision"] for item in reviews if item["scope"] == scope]
    if "rejected" in decisions:
        return "rejected"
    if "changes-requested" in decisions:
        return "changes-requested"
    if "approved" in decisions:
        return "passed"
    return "pending"


def _domain_state(reviews: List[Dict[str, Any]], required_domains: Sequence[str]) -> str:
    domain_reviews = [item for item in reviews if item["scope"] == "domain"]
    decisions = [item["decision"] for item in domain_reviews]
    if "rejected" in decisions:
        return "rejected"
    if "changes-requested" in decisions:
        return "changes-requested"
    approved_domains = {
        item["domain"] for item in domain_reviews if item["decision"] == "approved"
    }
    if set(required_domains).issubset(approved_domains):
        return "passed"
    return "pending"


def build_evidence_status(
    packet: Dict[str, Any],
    reviews: Sequence[Dict[str, Any]] = (),
    adoption_reports: Sequence[Dict[str, Any]] = (),
) -> Dict[str, Any]:
    """Aggregate exact-bound evidence while keeping every decision gate separate."""

    validate_review_packet(packet)
    review_list = [copy.deepcopy(item) for item in reviews]
    report_list = [copy.deepcopy(item) for item in adoption_reports]
    for review in review_list:
        validate_independent_review(review, packet)
    for report in report_list:
        validate_adoption_report(report, packet)
    review_ids = [item["review_id"] for item in review_list]
    report_ids = [item["report_id"] for item in report_list]
    _require(len(review_ids) == len(set(review_ids)), "review ids must be unique")
    _require(len(report_ids) == len(set(report_ids)), "adoption report ids must be unique")
    reviewer_scopes = [(item["reviewer_id"], item["scope"]) for item in review_list]
    _require(len(reviewer_scopes) == len(set(reviewer_scopes)), "reviewer may decide each scope once")
    domain_reviewers = sorted(
        item["reviewer_id"] for item in review_list if item["scope"] == "domain"
    )
    safety_reviewers = sorted(
        item["reviewer_id"] for item in review_list if item["scope"] == "safety"
    )
    _require(
        not set(domain_reviewers).intersection(safety_reviewers),
        "domain and safety reviews need different owners",
    )
    adopters = sorted({item["adopter_id"] for item in report_list})
    _require(
        not set(adopters).intersection(domain_reviewers + safety_reviewers),
        "adoption evidence and independent reviews need different owners",
    )

    domain_state = _domain_state(review_list, packet["contribution"]["domains"])
    safety_state = _scope_state(review_list, "safety")
    if not packet["requirements"]["safety_review_required"] and safety_state == "pending":
        safety_state = "not-required"
    if "rejected" in {domain_state, safety_state}:
        status_name = "rejected"
    elif "changes-requested" in {domain_state, safety_state}:
        status_name = "changes-requested"
    elif domain_state == "passed" and safety_state in {"passed", "not-required"}:
        status_name = "review-complete"
    else:
        status_name = "awaiting-independent-review"

    approved_domain = sum(
        item["scope"] == "domain" and item["decision"] == "approved" for item in review_list
    )
    approved_domains = sorted(
        {
            item["domain"]
            for item in review_list
            if item["scope"] == "domain" and item["decision"] == "approved"
        }
    )
    approved_safety = sum(
        item["scope"] == "safety" and item["decision"] == "approved" for item in review_list
    )
    successful_adoptions = sum(item["outcome"] == "successful" for item in report_list)
    status = {
        "$schema": STATUS_SCHEMA_URL,
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "contribution": {
            "id": packet["contribution"]["id"],
            "version": packet["contribution"]["version"],
            "risk_level": packet["contribution"]["risk_level"],
            "domains": packet["contribution"]["domains"],
        },
        "bindings": evidence_bindings(packet),
        "gates": {
            "intake_acceptance": "passed",
            "domain_review": domain_state,
            "safety_review": safety_state,
            "adoption_evidence": "recorded" if report_list else "none",
            "maturity_promotion": "not-authorized",
        },
        "owners": {
            "intake_maintainer": packet["intake"]["maintainer_id"],
            "domain_reviewers": domain_reviewers,
            "safety_reviewers": safety_reviewers,
            "adopters": adopters,
            "maturity_decider": None,
        },
        "evidence": {
            "review_count": len(review_list),
            "approved_domain_review_count": approved_domain,
            "approved_domains": approved_domains,
            "approved_safety_review_count": approved_safety,
            "adoption_report_count": len(report_list),
            "successful_adoption_count": successful_adoptions,
        },
        "summary": {
            "status": status_name,
            "domain_review_complete": domain_state == "passed",
            "safety_review_complete": safety_state in {"passed", "not-required"},
            "adoption_evidence_recorded": bool(report_list),
            "maturity_promotion_authorized": False,
        },
    }
    status["status_digest"] = canonical_digest(status)
    validate_evidence_status(status, packet)
    return status


def validate_evidence_status(status: Dict[str, Any], packet: Dict[str, Any]) -> None:
    """Validate an aggregate without granting it maturity decision authority."""

    validate_review_packet(packet)
    expected_keys = {
        "$schema",
        "schema_version",
        "generated_by",
        "contribution",
        "bindings",
        "gates",
        "owners",
        "evidence",
        "summary",
        "status_digest",
    }
    _require(isinstance(status, dict), "evidence status must be an object")
    _require(set(status) == expected_keys, "evidence status has an invalid contract")
    _require(status["$schema"] == STATUS_SCHEMA_URL, "evidence status schema mismatch")
    _require(status["schema_version"] == SCHEMA_VERSION, "unsupported status schema version")
    _require(status["generated_by"] == GENERATED_BY, "evidence status generator mismatch")
    _sha256(status["status_digest"], "status_digest")
    unsigned = {key: value for key, value in status.items() if key != "status_digest"}
    _require(
        status["status_digest"] == canonical_digest(unsigned),
        "evidence status digest mismatch",
    )
    expected_contribution = {
        "id": packet["contribution"]["id"],
        "version": packet["contribution"]["version"],
        "risk_level": packet["contribution"]["risk_level"],
        "domains": packet["contribution"]["domains"],
    }
    _require(status["contribution"] == expected_contribution, "status contribution binding mismatch")
    _validate_evidence_bindings(status["bindings"], packet, "evidence status")

    gates = status["gates"]
    _require(
        isinstance(gates, dict)
        and set(gates)
        == {
            "intake_acceptance",
            "domain_review",
            "safety_review",
            "adoption_evidence",
            "maturity_promotion",
        },
        "evidence gates have an invalid contract",
    )
    _require(gates["intake_acceptance"] == "passed", "intake gate must remain passed")
    review_states = {"pending", "passed", "changes-requested", "rejected"}
    _require(gates["domain_review"] in review_states, "domain review gate is invalid")
    _require(
        gates["safety_review"] in review_states | {"not-required"},
        "safety review gate is invalid",
    )
    _require(
        not (
            packet["requirements"]["safety_review_required"]
            and gates["safety_review"] == "not-required"
        ),
        "required safety review cannot be marked not-required",
    )
    _require(gates["adoption_evidence"] in {"none", "recorded"}, "adoption gate is invalid")
    _require(
        gates["maturity_promotion"] == "not-authorized",
        "community evidence cannot authorize maturity promotion",
    )

    owners = status["owners"]
    _require(
        isinstance(owners, dict)
        and set(owners)
        == {
            "intake_maintainer",
            "domain_reviewers",
            "safety_reviewers",
            "adopters",
            "maturity_decider",
        },
        "evidence owners have an invalid contract",
    )
    _require(
        owners["intake_maintainer"] == packet["intake"]["maintainer_id"],
        "intake maintainer binding mismatch",
    )
    for name in ("domain_reviewers", "safety_reviewers", "adopters"):
        values = _sorted_unique_strings(owners[name], f"owners.{name}")
        for index, value in enumerate(values):
            _public_id(value, f"owners.{name}[{index}]")
    _require(owners["maturity_decider"] is None, "maturity decider must remain unassigned")
    _require(
        not set(owners["domain_reviewers"]).intersection(owners["safety_reviewers"]),
        "domain and safety reviews need different owners",
    )
    _require(
        not set(owners["adopters"]).intersection(
            owners["domain_reviewers"] + owners["safety_reviewers"]
        ),
        "adoption evidence and independent reviews need different owners",
    )

    evidence = status["evidence"]
    evidence_keys = {
        "review_count",
        "approved_domain_review_count",
        "approved_domains",
        "approved_safety_review_count",
        "adoption_report_count",
        "successful_adoption_count",
    }
    _require(
        isinstance(evidence, dict)
        and set(evidence) == evidence_keys
        and all(
            type(evidence[name]) is int and evidence[name] >= 0
            for name in evidence_keys - {"approved_domains"}
        ),
        "evidence counts have an invalid contract",
    )
    approved_domains = _sorted_unique_strings(
        evidence["approved_domains"],
        "evidence.approved_domains",
        identifiers=True,
    )
    _require(
        set(approved_domains).issubset(packet["contribution"]["domains"]),
        "approved domains exceed the contribution scope",
    )
    _require(
        evidence["review_count"]
        == len(owners["domain_reviewers"]) + len(owners["safety_reviewers"]),
        "review count does not match review owners",
    )
    _require(
        evidence["approved_domain_review_count"] <= len(owners["domain_reviewers"]),
        "approved domain review count exceeds review owners",
    )
    _require(
        evidence["approved_domain_review_count"] >= len(approved_domains),
        "approved domain coverage exceeds approved review count",
    )
    _require(
        evidence["approved_safety_review_count"] <= len(owners["safety_reviewers"]),
        "approved safety review count exceeds review owners",
    )
    _require(
        evidence["successful_adoption_count"] <= evidence["adoption_report_count"],
        "successful adoption count exceeds reports",
    )
    if gates["domain_review"] == "passed":
        _require(
            approved_domains == packet["contribution"]["domains"],
            "passed domain gate requires every declared domain",
        )
    if gates["domain_review"] == "pending":
        _require(
            approved_domains != packet["contribution"]["domains"],
            "pending domain gate cannot cover every declared domain",
        )
    if gates["safety_review"] == "passed":
        _require(
            evidence["approved_safety_review_count"] > 0,
            "passed safety gate requires approved evidence",
        )
    if gates["safety_review"] in {"pending", "not-required"}:
        _require(
            evidence["approved_safety_review_count"] == 0,
            "pending safety gate cannot contain approved evidence",
        )
    _require(
        (gates["adoption_evidence"] == "recorded")
        == (evidence["adoption_report_count"] > 0),
        "adoption gate conflicts with evidence count",
    )

    if "rejected" in {gates["domain_review"], gates["safety_review"]}:
        status_name = "rejected"
    elif "changes-requested" in {gates["domain_review"], gates["safety_review"]}:
        status_name = "changes-requested"
    elif gates["domain_review"] == "passed" and gates["safety_review"] in {
        "passed",
        "not-required",
    }:
        status_name = "review-complete"
    else:
        status_name = "awaiting-independent-review"
    expected_summary = {
        "status": status_name,
        "domain_review_complete": gates["domain_review"] == "passed",
        "safety_review_complete": gates["safety_review"] in {"passed", "not-required"},
        "adoption_evidence_recorded": gates["adoption_evidence"] == "recorded",
        "maturity_promotion_authorized": False,
    }
    _require(status["summary"] == expected_summary, "evidence status summary mismatch")


def issue_summary(packet: Dict[str, Any], status: Optional[Dict[str, Any]] = None) -> str:
    validate_review_packet(packet)
    if status is None:
        status = build_evidence_status(packet)
    else:
        validate_evidence_status(status, packet)
    contribution = packet["contribution"]
    gates = status["gates"]
    safety_required = packet["requirements"]["safety_review_required"]
    lines = [
        f"# Community review: {contribution['id']} v{contribution['version']}",
        "",
        "## Immutable Evidence",
        "",
        f"- Artifact: {contribution['artifact_url']}",
        f"- Source SHA-256: `{packet['bindings']['source_digest']}`",
        f"- Receipt SHA-256: `{packet['bindings']['receipt_digest']}`",
        f"- Context SHA-256: `{packet['bindings']['context_digest']}`",
        f"- Review basis SHA-256: `{packet['bindings']['review_basis_digest']}`",
        f"- Risk: `{contribution['risk_level']}`",
        f"- Domains: `{', '.join(contribution['domains'])}`",
        "",
        "## Review Gates",
        "",
        f"- [x] Maintainer intake acceptance: `{gates['intake_acceptance']}`",
        (
            f"- [{'x' if gates['domain_review'] == 'passed' else ' '}] "
            f"Independent domain review: `{gates['domain_review']}`"
        ),
        (
            f"- [{'x' if gates['safety_review'] in {'passed', 'not-required'} else ' '}] "
            f"Independent safety review: `{gates['safety_review']}`"
            + (" (required)" if safety_required else " (not required by declared risk)")
        ),
        (
            f"- [{'x' if gates['adoption_evidence'] == 'recorded' else ' '}] "
            f"Public-safe adoption evidence: `{gates['adoption_evidence']}`"
        ),
        "- [ ] Registry maturity decision: separate pull request and maintainer owner required",
        "",
        "## Reviewer Checklist",
        "",
    ]
    lines.extend(f"- [ ] {question}" for question in packet["review_questions"])
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            (
                "This packet contains no contribution instruction content. "
                "Digests detect drift but are not signatures."
            ),
            (
                "Intake acceptance, domain review, safety review, adoption "
                "evidence, and maturity promotion are separate decisions."
            ),
            (
                "No receipt, review, adoption report, or generated status "
                "authorizes execution or automatic maturity promotion."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_json_artifact(path: Path, payload: Dict[str, Any], label: str) -> None:
    try:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        raise CommunityEvidenceError(f"cannot write {label} {path.name}: {exc}") from exc


def write_text_artifact(path: Path, value: str, label: str) -> None:
    try:
        path.write_text(value, encoding="utf-8")
    except OSError as exc:
        raise CommunityEvidenceError(f"cannot write {label} {path.name}: {exc}") from exc


def ensure_distinct_artifacts(artifacts: Sequence[Tuple[Path, str]]) -> None:
    """Prevent generated evidence from overwriting any input or sibling output."""

    seen: Dict[Path, str] = {}
    for path, label in artifacts:
        normalized = path.expanduser().resolve(strict=False)
        if normalized in seen:
            raise CommunityEvidenceError(
                f"{label} must not reuse the {seen[normalized]} path"
            )
        seen[normalized] = label


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and verify community review evidence"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    packet = subparsers.add_parser("packet", help="Create a fresh maintainer review packet")
    packet.add_argument("receipt", type=Path)
    packet.add_argument("--source", required=True, type=Path)
    packet.add_argument("--policy", type=Path)
    packet.add_argument("--id", dest="contribution_id", required=True)
    packet.add_argument("--version", required=True)
    packet.add_argument("--risk", required=True, choices=sorted(RISK_LEVELS))
    packet.add_argument("--domain", action="append", required=True)
    packet.add_argument("--submitter", required=True)
    packet.add_argument("--artifact-url", required=True)
    packet.add_argument("--output", type=Path)
    packet.add_argument("--summary-output", type=Path)
    packet.add_argument("--json", action="store_true")
    check = subparsers.add_parser("check", help="Verify packet, reviews, and adoption reports")
    check.add_argument("packet", type=Path)
    check.add_argument("--receipt", required=True, type=Path)
    check.add_argument("--source", required=True, type=Path)
    check.add_argument("--policy", type=Path)
    check.add_argument("--review", action="append", type=Path, default=[])
    check.add_argument("--adoption", action="append", type=Path, default=[])
    check.add_argument("--output", type=Path)
    check.add_argument("--summary-output", type=Path)
    check.add_argument("--json", action="store_true")
    digest = subparsers.add_parser(
        "digest", help="Attach a canonical review or adoption self-digest"
    )
    digest.add_argument("artifact", type=Path)
    digest.add_argument("--output", type=Path)
    digest.add_argument("--json", action="store_true")
    return parser


def run_cli(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "digest":
            artifacts = [(args.artifact, "evidence artifact")]
            if args.output:
                artifacts.append((args.output, "digested artifact output"))
            ensure_distinct_artifacts(artifacts)
            payload = add_artifact_digest(
                load_evidence_artifact(args.artifact, "evidence artifact")
            )
            if args.output:
                write_json_artifact(args.output, payload, "digested evidence artifact")
            if args.json:
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                digest_field = (
                    "review_digest" if payload["$schema"] == REVIEW_SCHEMA_URL else "report_digest"
                )
                print(f"{digest_field}: {payload[digest_field]}")
            return 0

        source = args.source
        if args.command == "packet":
            artifacts = [(source, "contribution"), (args.receipt, "intake receipt")]
            if args.policy:
                artifacts.append((args.policy, "external policy"))
            if args.output:
                artifacts.append((args.output, "review packet output"))
            if args.summary_output:
                artifacts.append((args.summary_output, "issue summary output"))
            ensure_distinct_artifacts(artifacts)
            ensure_external_artifact(source, args.receipt, "intake receipt")
            receipt = load_evidence_artifact(args.receipt, "intake receipt")
            packet = create_review_packet(
                receipt,
                source,
                contribution_id=args.contribution_id,
                version=args.version,
                risk_level=args.risk,
                domains=args.domain,
                submitter_id=args.submitter,
                artifact_url=args.artifact_url,
                policy_path=args.policy,
            )
            if args.output:
                ensure_external_artifact(source, args.output, "review packet")
                write_json_artifact(args.output, packet, "review packet")
            summary = issue_summary(packet)
            if args.summary_output:
                ensure_external_artifact(source, args.summary_output, "issue summary")
                write_text_artifact(args.summary_output, summary, "issue summary")
            if args.json:
                print(json.dumps(packet, indent=2, sort_keys=True))
            else:
                print(summary)
            return 0

        artifacts = [
            (args.packet, "review packet"),
            (args.receipt, "intake receipt"),
            *((path, "independent review") for path in args.review),
            *((path, "adoption report") for path in args.adoption),
        ]
        if args.policy:
            artifacts.append((args.policy, "external policy"))
        if args.output:
            artifacts.append((args.output, "evidence status output"))
        if args.summary_output:
            artifacts.append((args.summary_output, "issue summary output"))
        ensure_distinct_artifacts([(source, "contribution"), *artifacts])
        for path, label in artifacts:
            if label.endswith("output") or label == "external policy":
                continue
            ensure_external_artifact(source, path, label)
        packet = load_evidence_artifact(args.packet, "review packet")
        receipt = load_evidence_artifact(args.receipt, "intake receipt")
        verify_review_packet(packet, receipt, source, policy_path=args.policy)
        reviews = [load_evidence_artifact(path, "independent review") for path in args.review]
        reports = [load_evidence_artifact(path, "adoption report") for path in args.adoption]
        status = build_evidence_status(packet, reviews, reports)
        if args.output:
            ensure_external_artifact(source, args.output, "evidence status")
            write_json_artifact(args.output, status, "evidence status")
        summary = issue_summary(packet, status)
        if args.summary_output:
            ensure_external_artifact(source, args.summary_output, "issue summary")
            write_text_artifact(args.summary_output, summary, "issue summary")
        if args.json:
            print(json.dumps(status, indent=2, sort_keys=True))
        else:
            print(summary)
        return 1 if status["summary"]["status"] in {"changes-requested", "rejected"} else 0
    except (
        CommunityEvidenceError,
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
