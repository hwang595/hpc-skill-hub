"""Build and verify review-gated community context for read-only agents."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .community_evidence import (
    build_evidence_status,
    load_evidence_artifact,
    validate_review_packet,
    verify_review_packet,
)
from .intake import DEFAULT_LIMITS, IntakeLimits, intake_package
from .intake_receipt import validate_receipt
from .security_policy import canonical_digest


SCHEMA_VERSION = "0.1.0"
GENERATED_BY = "hpc-skill-community-context@0.1.0"
SCHEMA_URL = (
    "https://hpc-skill-hub.org/schemas/community-skill-context-bundle.schema.json"
)
RESOURCE_URI_TEMPLATE = "hpc-skill://community/{contribution_id}/{version}"
CONTEXT_FORMAT = "bounded-text-inventory-v1"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
MAX_CONTEXT_BUNDLES = 64
MAX_CONTEXT_BUNDLE_BYTES = 16_000_000
MAX_CONTEXT_TOTAL_BYTES = 64_000_000


class CommunityContextError(ValueError):
    """Raised when trusted community context cannot be built or verified."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CommunityContextError(message)


def _sha256(value: Any, label: str) -> str:
    _require(
        isinstance(value, str) and SHA256_RE.fullmatch(value) is not None,
        f"{label} is invalid",
    )
    return value


def _safe_path(value: Any, label: str) -> str:
    _require(isinstance(value, str) and bool(value), f"{label} is invalid")
    path = PurePosixPath(value)
    _require(
        value != "."
        and "\\" not in value
        and not path.is_absolute()
        and ".." not in path.parts,
        f"{label} escapes the bundle",
    )
    _require(path.as_posix() == value, f"{label} must be normalized POSIX")
    return value


def _bounded_limits(values: Any) -> IntakeLimits:
    _require(isinstance(values, dict), "context limits are invalid")
    try:
        limits = IntakeLimits(**values)
    except TypeError as exc:
        raise CommunityContextError("context limits are invalid") from exc
    for name in DEFAULT_LIMITS.__dataclass_fields__:
        value = getattr(limits, name)
        _require(
            isinstance(value, int)
            and not isinstance(value, bool)
            and 0 < value <= getattr(DEFAULT_LIMITS, name),
            f"limits.{name} is invalid",
        )
    return limits


def community_resource_uri(contribution_id: str, version: str) -> str:
    _require(
        isinstance(contribution_id, str)
        and ID_RE.fullmatch(contribution_id) is not None,
        "contribution id is invalid",
    )
    _require(
        isinstance(version, str) and VERSION_RE.fullmatch(version) is not None,
        "contribution version is invalid",
    )
    return RESOURCE_URI_TEMPLATE.format(
        contribution_id=contribution_id,
        version=version,
    )


def _manifest(files: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {"path": item["path"], "bytes": item["bytes"], "sha256": item["sha256"]}
        for item in files
    ]


def _serialized_bytes(bundle: Dict[str, Any]) -> int:
    return len(
        (json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode(
            "utf-8"
        )
    )


def build_community_context(
    source: Path,
    receipt: Dict[str, Any],
    packet: Dict[str, Any],
    reviews: Sequence[Dict[str, Any]] = (),
    adoption_reports: Sequence[Dict[str, Any]] = (),
    *,
    policy_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Build context only after fresh intake verification and independent review."""

    _require(isinstance(receipt, dict), "receipt must be an object")
    intake_report = receipt.get("intake_report")
    _require(isinstance(intake_report, dict), "receipt intake report is invalid")
    limits = _bounded_limits(intake_report.get("limits"))
    verify_review_packet(packet, receipt, source, policy_path=policy_path)
    status = build_evidence_status(packet, reviews, adoption_reports)
    _require(
        status["summary"]["status"] == "review-complete",
        "community context requires completed domain and applicable safety review",
    )
    _require(
        status["gates"]["maturity_promotion"] == "not-authorized",
        "community evidence cannot authorize maturity promotion",
    )

    files: List[Dict[str, Any]] = []
    current = intake_package(
        source,
        policy_path=policy_path,
        limits=limits,
        _snapshot_output=files,
    )
    expected_inventory = receipt["intake_report"]["inventory"]
    _require(
        current["inventory"] == expected_inventory,
        "quarantine snapshot has stale inventory",
    )
    files.sort(key=lambda item: item["path"])
    manifest = _manifest(files)
    expected_manifest = [
        {"path": item["path"], "bytes": item["bytes"], "sha256": item["sha256"]}
        for item in expected_inventory["files"]
        if item["type"] == "file" and item["content_type"] == "text"
    ]
    expected_manifest.sort(key=lambda item: item["path"])
    _require(
        manifest == expected_manifest,
        "quarantine snapshot does not match accepted files",
    )
    context_digest = canonical_digest({"format": CONTEXT_FORMAT, "files": manifest})
    _require(
        context_digest == receipt["accepted_context"]["accepted_digest"],
        "quarantine snapshot does not match accepted context digest",
    )

    contribution = copy.deepcopy(packet["contribution"])
    bundle = {
        "$schema": SCHEMA_URL,
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATED_BY,
        "contribution": contribution,
        "provenance": {
            "source": {
                "artifact_url": contribution["artifact_url"],
                "source_digest": packet["bindings"]["source_digest"],
                "inventory_digest": packet["bindings"]["inventory_digest"],
                "context_digest": context_digest,
            },
            "policy": {
                "policy_digest": packet["bindings"]["policy_digest"],
                "accepted_exception_ids": copy.deepcopy(
                    packet["intake"]["accepted_exception_ids"]
                ),
            },
            "receipt": {
                "status": packet["intake"]["status"],
                "receipt_digest": packet["bindings"]["receipt_digest"],
                "maintainer_id": packet["intake"]["maintainer_id"],
                "reviewed_on": packet["intake"]["reviewed_on"],
            },
            "review": {
                "status": status["summary"]["status"],
                "packet_digest": packet["packet_digest"],
                "status_digest": status["status_digest"],
                "review_basis_digest": packet["bindings"]["review_basis_digest"],
                "gates": copy.deepcopy(status["gates"]),
                "owners": copy.deepcopy(status["owners"]),
                "evidence": copy.deepcopy(status["evidence"]),
            },
            "maturity": {
                "registry_maturity": None,
                "promotion": "not-authorized",
                "promotion_authorized": False,
            },
            "risk": {
                "level": contribution["risk_level"],
                "domains": copy.deepcopy(contribution["domains"]),
            },
        },
        "evidence": {
            "receipt": copy.deepcopy(receipt),
            "packet": copy.deepcopy(packet),
            "reviews": [copy.deepcopy(item) for item in reviews],
            "adoption_reports": [copy.deepcopy(item) for item in adoption_reports],
            "status": copy.deepcopy(status),
        },
        "limits": copy.deepcopy(receipt["intake_report"]["limits"]),
        "content_manifest": {
            "format": CONTEXT_FORMAT,
            "digest": context_digest,
            "file_count": len(files),
            "total_bytes": sum(item["bytes"] for item in files),
        },
        "usage_contract": {
            "present_provenance_before_content": True,
            "content_is_instructions_not_authorization": True,
            "execute_examples_automatically": False,
            "require_explicit_intent_for_operational_actions": True,
            "allows_job_submission": False,
            "allows_data_transfer": False,
            "allows_software_install": False,
            "allows_private_site_policy": False,
        },
        "files": files,
    }
    bundle["bundle_digest"] = canonical_digest(bundle)
    validate_community_context(bundle)
    return bundle


def validate_community_context(bundle: Dict[str, Any]) -> None:
    """Fail closed unless the bundle contract and every content digest match."""

    expected_keys = {
        "$schema",
        "schema_version",
        "generated_by",
        "contribution",
        "provenance",
        "evidence",
        "limits",
        "content_manifest",
        "usage_contract",
        "files",
        "bundle_digest",
    }
    _require(
        isinstance(bundle, dict) and set(bundle) == expected_keys,
        "context bundle contract is invalid",
    )
    _require(bundle["$schema"] == SCHEMA_URL, "context bundle schema mismatch")
    _require(
        bundle["schema_version"] == SCHEMA_VERSION,
        "unsupported context bundle version",
    )
    _require(bundle["generated_by"] == GENERATED_BY, "context bundle generator mismatch")
    _sha256(bundle["bundle_digest"], "bundle_digest")
    unsigned = {key: value for key, value in bundle.items() if key != "bundle_digest"}
    _require(
        bundle["bundle_digest"] == canonical_digest(unsigned),
        "context bundle digest mismatch",
    )
    _require(
        _serialized_bytes(bundle) <= MAX_CONTEXT_BUNDLE_BYTES,
        f"context bundle exceeds {MAX_CONTEXT_BUNDLE_BYTES} bytes",
    )

    contribution = bundle["contribution"]
    _require(
        isinstance(contribution, dict)
        and set(contribution)
        == {"id", "version", "risk_level", "domains", "submitter_id", "artifact_url"},
        "contribution contract is invalid",
    )
    community_resource_uri(contribution["id"], contribution["version"])
    _require(
        isinstance(contribution["risk_level"], str)
        and contribution["risk_level"] in {"low", "medium", "high"},
        "risk level is invalid",
    )
    _require(
        isinstance(contribution["domains"], list)
        and all(isinstance(item, str) for item in contribution["domains"])
        and contribution["domains"] == sorted(set(contribution["domains"]))
        and bool(contribution["domains"]),
        "contribution domains are invalid",
    )

    provenance = bundle["provenance"]
    _require(
        isinstance(provenance, dict)
        and set(provenance)
        == {"source", "policy", "receipt", "review", "maturity", "risk"},
        "provenance contract is invalid",
    )
    source = provenance["source"]
    _require(
        isinstance(source, dict)
        and set(source) == {"artifact_url", "source_digest", "inventory_digest", "context_digest"},
        "source provenance is invalid",
    )
    _require(
        source["artifact_url"] == contribution["artifact_url"],
        "artifact URL provenance mismatch",
    )
    for name in ("source_digest", "inventory_digest", "context_digest"):
        _sha256(source[name], f"source.{name}")
    policy = provenance["policy"]
    _require(
        isinstance(policy, dict)
        and set(policy) == {"policy_digest", "accepted_exception_ids"},
        "policy provenance is invalid",
    )
    _sha256(policy["policy_digest"], "policy.policy_digest")
    _require(
        isinstance(policy["accepted_exception_ids"], list)
        and all(isinstance(item, str) for item in policy["accepted_exception_ids"])
        and policy["accepted_exception_ids"] == sorted(set(policy["accepted_exception_ids"])),
        "accepted exception provenance is invalid",
    )
    receipt = provenance["receipt"]
    _require(
        isinstance(receipt, dict)
        and set(receipt) == {"status", "receipt_digest", "maintainer_id", "reviewed_on"}
        and receipt["status"] == "accepted",
        "receipt provenance is invalid",
    )
    _sha256(receipt["receipt_digest"], "receipt.receipt_digest")
    review = provenance["review"]
    _require(
        isinstance(review, dict)
        and set(review)
        == {
            "status",
            "packet_digest",
            "status_digest",
            "review_basis_digest",
            "gates",
            "owners",
            "evidence",
        }
        and review["status"] == "review-complete",
        "review provenance is invalid",
    )
    for name in ("packet_digest", "status_digest", "review_basis_digest"):
        _sha256(review[name], f"review.{name}")
    gates = review["gates"]
    _require(
        isinstance(gates, dict)
        and gates.get("intake_acceptance") == "passed"
        and gates.get("domain_review") == "passed"
        and gates.get("safety_review") in {"passed", "not-required"}
        and gates.get("maturity_promotion") == "not-authorized",
        "review gates do not authorize context exposure",
    )
    maturity = provenance["maturity"]
    _require(
        maturity == {
            "registry_maturity": None,
            "promotion": "not-authorized",
            "promotion_authorized": False,
        },
        "maturity provenance is invalid",
    )
    _require(
        provenance["risk"]
        == {"level": contribution["risk_level"], "domains": contribution["domains"]},
        "risk provenance mismatch",
    )

    evidence = bundle["evidence"]
    _require(
        isinstance(evidence, dict)
        and set(evidence)
        == {"receipt", "packet", "reviews", "adoption_reports", "status"}
        and isinstance(evidence["reviews"], list)
        and isinstance(evidence["adoption_reports"], list),
        "embedded evidence contract is invalid",
    )
    validate_receipt(evidence["receipt"])
    validate_review_packet(evidence["packet"])
    _require(
        evidence["receipt"]["summary"]["status"] == "accepted",
        "embedded receipt is not accepted",
    )
    _require(
        evidence["packet"]["contribution"] == contribution,
        "embedded packet contribution mismatch",
    )
    _require(
        evidence["packet"]["bindings"]["receipt_digest"]
        == evidence["receipt"]["receipt_digest"],
        "embedded receipt and packet binding mismatch",
    )
    expected_status = build_evidence_status(
        evidence["packet"],
        evidence["reviews"],
        evidence["adoption_reports"],
    )
    _require(evidence["status"] == expected_status, "embedded evidence status mismatch")
    _require(
        expected_status["summary"]["status"] == "review-complete",
        "embedded review is incomplete",
    )
    packet = evidence["packet"]
    _require(
        source
        == {
            "artifact_url": contribution["artifact_url"],
            "source_digest": packet["bindings"]["source_digest"],
            "inventory_digest": packet["bindings"]["inventory_digest"],
            "context_digest": packet["bindings"]["context_digest"],
        },
        "source provenance does not match embedded evidence",
    )
    _require(
        policy
        == {
            "policy_digest": packet["bindings"]["policy_digest"],
            "accepted_exception_ids": packet["intake"]["accepted_exception_ids"],
        },
        "policy provenance does not match embedded evidence",
    )
    _require(
        receipt
        == {
            "status": packet["intake"]["status"],
            "receipt_digest": packet["bindings"]["receipt_digest"],
            "maintainer_id": packet["intake"]["maintainer_id"],
            "reviewed_on": packet["intake"]["reviewed_on"],
        },
        "receipt provenance does not match embedded evidence",
    )
    _require(
        review
        == {
            "status": expected_status["summary"]["status"],
            "packet_digest": packet["packet_digest"],
            "status_digest": expected_status["status_digest"],
            "review_basis_digest": packet["bindings"]["review_basis_digest"],
            "gates": expected_status["gates"],
            "owners": expected_status["owners"],
            "evidence": expected_status["evidence"],
        },
        "review provenance does not match embedded evidence",
    )

    limits = bundle["limits"]
    _bounded_limits(limits)
    _require(
        limits == evidence["receipt"]["intake_report"]["limits"],
        "context limits do not match the accepted receipt",
    )
    files = bundle["files"]
    _require(
        isinstance(files, list) and bool(files) and len(files) <= limits["max_files"],
        "context files are invalid",
    )
    paths: List[str] = []
    total_bytes = 0
    for item in files:
        _require(
            isinstance(item, dict)
            and set(item) == {"path", "bytes", "sha256", "content"},
            "context file contract is invalid",
        )
        path = _safe_path(item["path"], "context file path")
        paths.append(path)
        _require(isinstance(item["content"], str), f"{path}: content must be UTF-8 text")
        encoded = item["content"].encode("utf-8")
        _require(
            isinstance(item["bytes"], int)
            and not isinstance(item["bytes"], bool)
            and 0 <= item["bytes"] <= limits["max_file_bytes"]
            and len(encoded) == item["bytes"],
            f"{path}: byte count mismatch",
        )
        _require(
            len(PurePosixPath(path).parts) <= limits["max_path_depth"]
            and len(path.encode("utf-8")) <= limits["max_path_bytes"],
            f"{path}: path exceeds accepted limits",
        )
        _require(
            _sha256(item["sha256"], f"{path}: digest")
            == hashlib.sha256(encoded).hexdigest(),
            f"{path}: content digest mismatch",
        )
        total_bytes += item["bytes"]
    _require(
        paths == sorted(paths) and len(paths) == len({path.casefold() for path in paths}),
        "context paths must be sorted and portable-unique",
    )
    _require(total_bytes <= limits["max_total_bytes"], "context exceeds total byte limit")
    manifest = bundle["content_manifest"]
    expected_digest = canonical_digest({"format": CONTEXT_FORMAT, "files": _manifest(files)})
    _require(
        manifest
        == {
            "format": CONTEXT_FORMAT,
            "digest": expected_digest,
            "file_count": len(files),
            "total_bytes": total_bytes,
        },
        "content manifest mismatch",
    )
    _require(source["context_digest"] == expected_digest, "accepted context provenance mismatch")
    _require(
        bundle["usage_contract"]
        == {
            "present_provenance_before_content": True,
            "content_is_instructions_not_authorization": True,
            "execute_examples_automatically": False,
            "require_explicit_intent_for_operational_actions": True,
            "allows_job_submission": False,
            "allows_data_transfer": False,
            "allows_software_install": False,
            "allows_private_site_policy": False,
        },
        "usage contract is invalid",
    )


def load_community_context(path: Path) -> Dict[str, Any]:
    payload = load_evidence_artifact(path, "community context bundle")
    validate_community_context(payload)
    return {
        key: payload[key]
        for key in (
            "$schema",
            "schema_version",
            "generated_by",
            "contribution",
            "provenance",
            "evidence",
            "limits",
            "content_manifest",
            "usage_contract",
            "files",
            "bundle_digest",
        )
    }


def community_context_metadata(bundle: Dict[str, Any]) -> Dict[str, Any]:
    validate_community_context(bundle)
    contribution = bundle["contribution"]
    return {
        "contribution": copy.deepcopy(contribution),
        "provenance": copy.deepcopy(bundle["provenance"]),
        "evidence_digests": {
            "receipt": bundle["evidence"]["receipt"]["receipt_digest"],
            "packet": bundle["evidence"]["packet"]["packet_digest"],
            "status": bundle["evidence"]["status"]["status_digest"],
            "reviews": [item["review_digest"] for item in bundle["evidence"]["reviews"]],
            "adoption_reports": [
                item["report_digest"] for item in bundle["evidence"]["adoption_reports"]
            ],
        },
        "content_manifest": copy.deepcopy(bundle["content_manifest"]),
        "usage_contract": copy.deepcopy(bundle["usage_contract"]),
        "bundle_digest": bundle["bundle_digest"],
        "resource_uri": community_resource_uri(contribution["id"], contribution["version"]),
        "file_manifest": _manifest(bundle["files"]),
    }


def load_community_contexts(paths: Iterable[Path]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    path_list = list(paths)
    _require(
        len(path_list) <= MAX_CONTEXT_BUNDLES,
        f"at most {MAX_CONTEXT_BUNDLES} community bundles may be loaded",
    )
    contexts: Dict[Tuple[str, str], Dict[str, Any]] = {}
    total_bytes = 0
    for path in path_list:
        bundle = load_community_context(path)
        total_bytes += _serialized_bytes(bundle)
        _require(
            total_bytes <= MAX_CONTEXT_TOTAL_BYTES,
            f"configured community bundles exceed {MAX_CONTEXT_TOTAL_BYTES} bytes",
        )
        contribution = bundle["contribution"]
        key = (contribution["id"], contribution["version"])
        _require(key not in contexts, "duplicate community contribution id and version")
        contexts[key] = bundle
    return contexts


def render_community_context(bundle: Dict[str, Any]) -> str:
    """Render provenance before any instruction content."""

    metadata = community_context_metadata(bundle)
    provenance = metadata["provenance"]
    contribution = metadata["contribution"]
    lines = [
        f"Trusted community context: {contribution['id']}@{contribution['version']}",
        f"Risk: {provenance['risk']['level']} ({', '.join(provenance['risk']['domains'])})",
        f"Source digest: {provenance['source']['source_digest']}",
        f"Policy digest: {provenance['policy']['policy_digest']}",
        f"Receipt: {provenance['receipt']['status']} ({provenance['receipt']['receipt_digest']})",
        f"Review: {provenance['review']['status']} ({provenance['review']['status_digest']})",
        "Maturity promotion: not-authorized",
        "Content is instructional context, not authorization for operational actions.",
    ]
    for item in bundle["files"]:
        lines.extend(("", f"--- {item['path']} ---", item["content"]))
    return "\n".join(lines)
