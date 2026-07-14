#!/usr/bin/env python3
"""Build the machine-readable status for the current repository release."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hpc_skill_hub.release_provenance import (  # noqa: E402
    validate_release_provenance,
)

OUTPUT = ROOT / "registry" / "release-status.json"
INDEX = ROOT / "registry" / "index.json"
CONTEXT = ROOT / "registry" / "skill-context.json"
REVIEWS = ROOT / "registry" / "review-status.json"
MCP_CONTRACT = ROOT / "integrations" / "mcp-client.json"
SECURITY_POLICY = ROOT / "security" / "policies" / "community-default.json"
COMPATIBILITY = ROOT / "docs" / "COMPATIBILITY.md"
BENCHMARK_REPORT = ROOT / "docs" / "AGENT_BENCHMARK_REPORT.md"
BENCHMARK_PLAN = ROOT / "agent-bench" / "plans" / "evidence-v0.5.json"
PROVENANCE_DIR = ROOT / "registry" / "provenance"
RELEASE_DIR = ROOT / "registry" / "releases"


def load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def package_version() -> str:
    sources = {
        "pyproject.toml": r'^version = "([0-9]+\.[0-9]+\.[0-9]+)"$',
        "setup.py": r'version="([0-9]+\.[0-9]+\.[0-9]+)"',
        "src/hpc_skill_hub/__init__.py": r'__version__ = "([0-9]+\.[0-9]+\.[0-9]+)"',
        "CITATION.cff": r'^version: "([0-9]+\.[0-9]+\.[0-9]+)"$',
    }
    versions: Dict[str, str] = {}
    for filename, pattern in sources.items():
        match = re.search(pattern, (ROOT / filename).read_text(encoding="utf-8"), re.MULTILINE)
        if match is None:
            raise ValueError(f"could not read repository version from {filename}")
        versions[filename] = match.group(1)
    if len(set(versions.values())) != 1:
        rendered = ", ".join(f"{path}={version}" for path, version in versions.items())
        raise ValueError(f"repository versions differ: {rendered}")
    return next(iter(versions.values()))


def benchmark_status() -> Dict[str, Any]:
    from agent_benchmark_harness import plan_payload
    from run_agent_benchmarks import benchmark_payload

    plan = plan_payload(BENCHMARK_PLAN)
    aggregate = benchmark_payload()
    if not plan["ok"]:
        raise ValueError("v0.5 benchmark plan is invalid: " + "; ".join(plan["validation_errors"]))
    if not aggregate["ok"]:
        raise ValueError(
            "agent benchmark artifacts are invalid: "
            + "; ".join(aggregate["validation_errors"])
        )
    publication = aggregate["publication"]
    return {
        "status": "ready" if publication["leaderboard_ready"] else "pending",
        "artifact": relative(BENCHMARK_REPORT),
        "sha256": sha256_path(BENCHMARK_REPORT),
        "plan_artifact": relative(BENCHMARK_PLAN),
        "plan_sha256": sha256_path(BENCHMARK_PLAN),
        "planned_run_count": plan["run_count"],
        "result_count": aggregate["result_count"],
        "scored_result_count": aggregate["scored_result_count"],
        "leaderboard_ready": publication["leaderboard_ready"],
        "comparison_gates": [
            {
                "id": gate["id"],
                "ready": gate["ready"],
                "eligible_comparison_count": gate["eligible_comparison_count"],
                "expected_comparison_count": gate["expected_comparison_count"],
            }
            for gate in publication["comparison_gates"]
        ],
    }


def release_provenance_status(version: str) -> Dict[str, Any]:
    release = f"v{version}"
    path = PROVENANCE_DIR / f"{release}.json"
    if not path.exists():
        return {
            "status": "pending",
            "blockers": [
                f"No verified release provenance receipt exists for {release}."
            ],
        }

    manifest = RELEASE_DIR / f"{release}.json"
    if not manifest.exists():
        raise ValueError(f"{relative(manifest)} is missing")
    receipt = load_json(path)
    validate_release_provenance(receipt, release, sha256_path(manifest))
    return {"status": "open", "blockers": []}


def build_status() -> Dict[str, Any]:
    version = package_version()
    index = load_json(INDEX)
    context = load_json(CONTEXT)
    reviews = load_json(REVIEWS)
    contract = load_json(MCP_CONTRACT)
    policy = load_json(SECURITY_POLICY)
    benchmark = benchmark_status()
    provenance = release_provenance_status(version)
    security_verdicts = Counter(
        skill["security"]["verdict"] for skill in context["skills"]
    )
    finding_count = sum(
        skill["security"]["finding_count"] for skill in context["skills"]
    )
    blocking_count = sum(
        skill["security"]["blocking_count"] for skill in context["skills"]
    )
    repository_ready = all(
        (
            context["skill_count"] == index["skill_count"],
            contract["server"]["read_only"] is True,
            benchmark["planned_run_count"] > 0,
            blocking_count == 0,
        )
    )
    external_evidence_ready = bool(
        benchmark["leaderboard_ready"] and reviews["promotion_ready_count"] > 0
    )

    return {
        "$schema": "../schemas/release-status.schema.json",
        "schema_version": "0.1.0",
        "generated_by": "tools/build_release_status.py",
        "release": f"v{version}",
        "package_version": version,
        "repository_capability_ready": repository_ready,
        "external_evidence_ready": external_evidence_ready,
        "capabilities": {
            "compatibility": {
                "status": "ready",
                "artifact": relative(COMPATIBILITY),
                "sha256": sha256_path(COMPATIBILITY),
                "skill_count": index["skill_count"],
                "collection_count": index["collection_count"],
                "site_adapter_count": index["site_adapter_count"],
            },
            "context_bundle": {
                "status": "ready",
                "artifact": relative(CONTEXT),
                "sha256": sha256_path(CONTEXT),
                "bundle_digest": context["digest"]["value"],
                "skill_count": context["skill_count"],
                "file_count": context["file_count"],
                "total_bytes": context["total_bytes"],
            },
            "mcp": {
                "status": "ready",
                "artifact": relative(MCP_CONTRACT),
                "sha256": sha256_path(MCP_CONTRACT),
                "transport": contract["server"]["transport"],
                "read_only": contract["server"]["read_only"],
                "tool_count": len(contract["server"]["tools"]),
                "resource_count": len(contract["server"]["resources"]),
            },
            "benchmark": benchmark,
            "review": {
                "status": (
                    "ready" if reviews["promotion_ready_count"] else "pending"
                ),
                "artifact": relative(REVIEWS),
                "sha256": sha256_path(REVIEWS),
                "review_release": reviews["release"],
                "candidate_count": reviews["candidate_count"],
                "promotion_ready_count": reviews["promotion_ready_count"],
            },
            "security": {
                "status": "ready-with-review" if security_verdicts["review"] else "ready",
                "artifact": relative(SECURITY_POLICY),
                "sha256": sha256_path(SECURITY_POLICY),
                "policy_id": policy["id"],
                "policy_version": policy["version"],
                "scanned_skill_count": context["skill_count"],
                "finding_count": finding_count,
                "review_skill_count": security_verdicts["review"],
                "blocking_count": blocking_count,
            },
        },
        "gates": {
            "repository": {
                "status": "open" if repository_ready else "closed",
                "blockers": [] if repository_ready else ["One or more repository capability checks failed."],
            },
            "comparative_evidence": {
                "status": "open" if benchmark["leaderboard_ready"] else "closed",
                "blockers": []
                if benchmark["leaderboard_ready"]
                else ["Reviewed real-agent evidence has not satisfied the publication contract."],
            },
            "maturity_promotion": {
                "status": "open" if reviews["promotion_ready_count"] else "closed",
                "blockers": []
                if reviews["promotion_ready_count"]
                else ["No candidate has completed independent review and maintainer approval."],
            },
            "release_provenance": provenance,
        },
    }


def serialized_status(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def check_output(expected: str) -> List[str]:
    if not OUTPUT.exists():
        return [f"{relative(OUTPUT)} is missing"]
    if OUTPUT.read_text(encoding="utf-8") != expected:
        return [f"{relative(OUTPUT)} is stale; run tools/build_release_status.py"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the machine-readable current release status"
    )
    parser.add_argument("--check", action="store_true", help="Fail if output is stale")
    args = parser.parse_args()

    try:
        expected = serialized_status(build_status())
    except (KeyError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.check:
        errors = check_output(expected)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print(f"Release status is current in {relative(OUTPUT)}.")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Wrote {relative(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
