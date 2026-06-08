#!/usr/bin/env python3
"""Scan scientific simulation logs for common HPC failure signals."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class Signal:
    name: str
    category: str
    severity: str
    pattern: re.Pattern[str]
    guidance: str


SIGNALS = [
    Signal(
        "out-of-memory",
        "memory",
        "high",
        re.compile(r"\b(out[- ]of[- ]memory|oom|killed process|cannot allocate memory)\b", re.I),
        "Review memory request, per-rank memory, thread count, and input size before retrying.",
    ),
    Signal(
        "gpu-memory",
        "gpu",
        "high",
        re.compile(r"\b(cuda out of memory|hip out of memory|cublas|nccl.*unhandled|gpu memory)\b", re.I),
        "Check GPU binding, batch size, domain decomposition, and per-process GPU visibility.",
    ),
    Signal(
        "mpi-abort",
        "mpi",
        "high",
        re.compile(r"\b(mpi_abort|mpirun.*aborting|srun: error|rank [0-9]+.*exited|pmix.*error)\b", re.I),
        "Collect rank placement, launcher, MPI module, and first failing rank evidence.",
    ),
    Signal(
        "segmentation-fault",
        "crash",
        "high",
        re.compile(r"\b(segmentation fault|segfault|sigsegv|bus error|core dumped)\b", re.I),
        "Reproduce with a smaller case, confirm compiler/MPI compatibility, and inspect stack traces.",
    ),
    Signal(
        "convergence",
        "numerics",
        "medium",
        re.compile(r"\b(convergence.*not achieved|not converged|nan|floating point exception|diverged)\b", re.I),
        "Review timestep, tolerances, initial conditions, precision, and software-specific stability notes.",
    ),
    Signal(
        "license",
        "license",
        "medium",
        re.compile(r"\b(license checkout failed|license.*denied|no.*license|license server)\b", re.I),
        "Check site license policy, scheduler license requests, and vendor license availability.",
    ),
    Signal(
        "missing-file",
        "input",
        "medium",
        re.compile(r"\b(no such file|cannot open|file not found|missing input|could not read)\b", re.I),
        "Verify staged inputs, working directory, relative paths, and container bind mounts.",
    ),
    Signal(
        "filesystem",
        "filesystem",
        "medium",
        re.compile(r"\b(disk quota exceeded|no space left|read-only file system|permission denied|input/output error)\b", re.I),
        "Check quota, inode usage, filesystem health, permissions, and output volume.",
    ),
    Signal(
        "walltime",
        "scheduler",
        "medium",
        re.compile(r"\b(time limit|walltime|timeout|cancelled.*time|requeue)\b", re.I),
        "Review checkpoint cadence, restart behavior, job time limit, and smaller task decomposition.",
    ),
]


def iter_lines(paths: Iterable[Path]):
    for path in paths:
        try:
            with path.open(encoding="utf-8", errors="replace") as handle:
                for line_number, line in enumerate(handle, start=1):
                    yield path, line_number, line.rstrip("\n")
        except OSError as exc:
            yield path, 0, f"ERROR: cannot read log: {exc}"


def scan_logs(paths: List[Path]) -> dict:
    findings = []
    missing_logs = []
    for path in paths:
        if not path.exists():
            missing_logs.append(str(path))

    for path, line_number, line in iter_lines(paths):
        if line_number == 0:
            findings.append(
                {
                    "log": str(path),
                    "line": 0,
                    "signal": "unreadable-log",
                    "category": "input",
                    "severity": "medium",
                    "snippet": line[:240],
                    "guidance": "Confirm the log path exists and is readable from the current environment.",
                }
            )
            continue
        for signal in SIGNALS:
            if signal.pattern.search(line):
                findings.append(
                    {
                        "log": str(path),
                        "line": line_number,
                        "signal": signal.name,
                        "category": signal.category,
                        "severity": signal.severity,
                        "snippet": line.strip()[:240],
                        "guidance": signal.guidance,
                    }
                )

    return {
        "log_count": len(paths),
        "missing_logs": missing_logs,
        "finding_count": len(findings),
        "findings": findings,
    }


def markdown_report(report: dict) -> str:
    lines = [
        "# Simulation Log Triage",
        "",
        f"- Logs requested: {report['log_count']}",
        f"- Missing logs: {len(report['missing_logs'])}",
        f"- Findings: {report['finding_count']}",
        "",
    ]
    if report["missing_logs"]:
        lines.extend(["## Missing Logs", ""])
        for path in report["missing_logs"]:
            lines.append(f"- `{path}`")
        lines.append("")

    lines.extend(["## Findings", ""])
    if not report["findings"]:
        lines.append("No common simulation failure signals were detected.")
        return "\n".join(lines) + "\n"

    lines.extend(
        [
            "| Log | Line | Signal | Severity | Category | Evidence | Follow-up |",
            "| --- | ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for finding in report["findings"]:
        snippet = finding["snippet"].replace("|", "\\|")
        guidance = finding["guidance"].replace("|", "\\|")
        lines.append(
            f"| `{finding['log']}` | {finding['line']} | "
            f"`{finding['signal']}` | {finding['severity']} | "
            f"{finding['category']} | {snippet} | {guidance} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", action="append", required=True, help="Log file to scan")
    parser.add_argument("--json", action="store_true", help="Write JSON instead of Markdown")
    args = parser.parse_args()

    report = scan_logs([Path(path) for path in args.log])
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(markdown_report(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
