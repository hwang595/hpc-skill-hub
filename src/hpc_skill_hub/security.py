"""Static security checks for community-contributed skill packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Dict, Iterable, List, Optional, Sequence


SCANNER_NAME = "hpc-skill-security"
SCANNER_VERSION = "0.1.0"
SCHEMA_URL = "https://hpc-skill-hub.org/schemas/skill-security-report.schema.json"
SEVERITIES = ("low", "medium", "high", "critical")
SEVERITY_RANK = {severity: index for index, severity in enumerate(SEVERITIES)}
TEXT_SUFFIXES = {
    "",
    ".c",
    ".bat",
    ".cfg",
    ".cmd",
    ".conf",
    ".css",
    ".erb",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".ps1",
    ".sh",
    ".sbatch",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}
EXECUTABLE_SUFFIXES = {".bin", ".class", ".dll", ".dylib", ".exe", ".jar", ".so"}
ARCHIVE_SUFFIXES = {".7z", ".bz2", ".gz", ".rar", ".tgz", ".xz", ".zip"}
SKIP_DIRS = {".git", "__pycache__", "build", "dist"}
MAX_FILE_BYTES = 1_000_000


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    category: str
    pattern: re.Pattern[str]
    message: str
    remediation: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    category: str
    path: str
    line: int
    message: str
    remediation: str
    fingerprint: str
    skill_id: Optional[str] = None


def compile_rule(
    rule_id: str,
    severity: str,
    category: str,
    pattern: str,
    message: str,
    remediation: str,
) -> Rule:
    return Rule(
        rule_id=rule_id,
        severity=severity,
        category=category,
        pattern=re.compile(pattern, re.IGNORECASE),
        message=message,
        remediation=remediation,
    )


RULES = (
    compile_rule(
        "secret.private-key",
        "critical",
        "secret",
        r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----",
        "Private key material is embedded in the skill package.",
        "Revoke the exposed key, remove it from history, and use a secret manager.",
    ),
    compile_rule(
        "secret.github-token",
        "critical",
        "secret",
        r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b",
        "A GitHub token-shaped secret is embedded in the skill package.",
        "Revoke the token, remove it from history, and accept credentials only at runtime.",
    ),
    compile_rule(
        "secret.aws-access-key",
        "critical",
        "secret",
        r"\bAKIA[0-9A-Z]{16}\b",
        "An AWS access-key-shaped secret is embedded in the skill package.",
        "Revoke the key, remove it from history, and use a scoped runtime identity.",
    ),
    compile_rule(
        "secret.slack-token",
        "critical",
        "secret",
        r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b",
        "A Slack token-shaped secret is embedded in the skill package.",
        "Revoke the token, remove it from history, and use runtime secret injection.",
    ),
    compile_rule(
        "secret.jupyter-token",
        "high",
        "secret",
        r"\btoken=[A-Za-z0-9][A-Za-z0-9_-]{15,}\b",
        "A Jupyter token-shaped secret is embedded in the skill package.",
        "Remove session URLs/tokens and document a placeholder-based connection flow.",
    ),
    compile_rule(
        "prompt.ignore-instructions",
        "high",
        "prompt-injection",
        r"\b(?:ignore|disregard|override)\b.{0,48}\b(?:previous|prior|system|developer|user)\b.{0,32}\b(?:instruction|prompt|message)s?\b",
        "Instruction-override language can redirect a coding agent away from its safety contract.",
        "Remove instruction-override text and express the skill task directly.",
    ),
    compile_rule(
        "prompt.hide-behavior",
        "high",
        "prompt-injection",
        r"\b(?:do not|don't|never)\b.{0,32}\b(?:tell|inform|reveal|mention|show)\b.{0,24}\b(?:user|operator|reviewer)\b",
        "The skill appears to ask an agent to conceal behavior from the user or reviewer.",
        "Make all actions, side effects, and assumptions visible to the user.",
    ),
    compile_rule(
        "execution.download-pipe-shell",
        "critical",
        "remote-execution",
        r"\b(?:curl|wget)\b[^\n|]{0,240}\|\s*(?:sudo\s+)?(?:ba)?sh\b",
        "Downloaded content is piped directly into a shell.",
        "Download to a file, verify provenance and checksum, then present a reviewed command.",
    ),
    compile_rule(
        "execution.encoded-payload",
        "critical",
        "obfuscation",
        r"\bbase64\b[^\n|]{0,120}(?:--decode|-d)\b[^\n|]{0,120}\|\s*(?:ba)?sh\b",
        "An encoded payload is decoded directly into a shell.",
        "Commit readable source and remove encoded execution chains.",
    ),
    compile_rule(
        "network.reverse-shell",
        "critical",
        "network",
        r"(?:/dev/(?:tcp|udp)/|\bnc\s+(?:-[A-Za-z]*e\b|[^\n]{0,80}\s-e\s)|\bsocat\b[^\n]{0,120}\bexec:)",
        "A reverse-shell or raw outbound shell pattern was detected.",
        "Remove remote shell behavior; skills must not create covert control channels.",
    ),
    compile_rule(
        "persistence.authorized-keys",
        "critical",
        "persistence",
        r"(?:>>?|\btee\b|\bcp\b|\bmv\b|\binstall\b)[^\n]{0,160}(?:authorized_keys|\.ssh/)",
        "The skill appears to modify SSH trust or key files.",
        "Remove SSH persistence behavior and document any legitimate key setup outside the skill.",
    ),
    compile_rule(
        "persistence.shell-profile",
        "high",
        "persistence",
        r"(?:>>?|\btee\b|\bsed\s+-i\b|\binstall\b)[^\n]{0,160}(?:\.bashrc|\.bash_profile|\.profile|\.zshrc)\b",
        "The skill appears to persist changes in a user shell profile.",
        "Use a reviewable environment file or print temporary export commands instead.",
    ),
    compile_rule(
        "credential.sensitive-read",
        "high",
        "credentials",
        r"\b(?:cat|cp|grep|head|less|sed|tail|tar)\b[^\n]{0,180}(?:\.aws/credentials|\.config/gh/hosts\.yml|\.kube/config|\.netrc|\.ssh/(?:id_|config))",
        "The skill appears to read or copy a sensitive credential/configuration file.",
        "Accept narrowly scoped inputs and never collect ambient user credentials.",
    ),
    compile_rule(
        "privilege.sudo",
        "critical",
        "privilege",
        r"(?:^|[;&|]\s*)sudo\s+",
        "The skill invokes privileged execution.",
        "Remove privileged commands or move the workflow into a separately reviewed administrator process.",
    ),
    compile_rule(
        "filesystem.world-writable",
        "high",
        "filesystem",
        r"(?:^|[;&|]\s*)chmod\s+(?:-R\s+)?(?:0?777|a\+rwx)\b",
        "The skill creates world-writable files or directories.",
        "Use least-privilege user/group permissions and document the sharing model.",
    ),
    compile_rule(
        "filesystem.recursive-delete",
        "medium",
        "destructive-action",
        r"(?:^|[;&|]\s*)rm\s+-[A-Za-z]*r[A-Za-z]*f?[A-Za-z]*\s+",
        "The skill contains recursive deletion and requires guard/ownership review.",
        "Constrain deletion to a marker-verified user-owned directory and keep it opt-in.",
    ),
    compile_rule(
        "execution.dynamic-eval",
        "medium",
        "dynamic-execution",
        r"(?:^|[;&|]\s*)eval\s+",
        "The skill dynamically evaluates shell text.",
        "Use an argument array or an explicit command instead of eval.",
    ),
    compile_rule(
        "dependency.unreviewed-install",
        "medium",
        "dependency",
        r"(?:^|[;&|]\s*)(?:pipx?|uv\s+pip|conda|mamba|npm|gem)\s+install\b|(?:^|[;&|]\s*)(?:apt(?:-get)?|dnf|yum|brew)\s+install\b",
        "The skill installs software and requires provenance, scope, and opt-in review.",
        "Pin versions where practical, use a user-owned environment, and make installation explicit.",
    ),
)


def fingerprint(rule_id: str, path: str, line: int) -> str:
    payload = f"{rule_id}\0{path}\0{line}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def finding(
    rule_id: str,
    severity: str,
    category: str,
    path: str,
    line: int,
    message: str,
    remediation: str,
    skill_id: Optional[str] = None,
) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity=severity,
        category=category,
        path=path,
        line=line,
        message=message,
        remediation=remediation,
        fingerprint=fingerprint(rule_id, path, line),
        skill_id=skill_id,
    )


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def iter_files(target: Path) -> Iterable[Path]:
    if target.is_file() or target.is_symlink():
        yield target
        return
    for path in sorted(target.rglob("*")):
        if is_skipped(path.relative_to(target)):
            continue
        if path.is_symlink():
            yield path
            continue
        if path.is_dir():
            continue
        yield path


def display_path(path: Path, target: Path) -> str:
    if target.is_file() or target.is_symlink():
        return path.name
    return path.relative_to(target).as_posix()


def skill_id_for(path: Path, target: Path) -> Optional[str]:
    current = path.parent if path.is_file() else path
    stop = target.parent if target.is_file() else target.parent
    while current != stop:
        manifest = current / "skill.json"
        if manifest.exists():
            try:
                payload = json.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return current.name
            value = payload.get("id")
            return value if isinstance(value, str) else current.name
        if (current / "SKILL.md").exists():
            return current.name
        if current == current.parent:
            break
        current = current.parent
    return None


def scan_text_file(path: Path, target: Path, skill_id: Optional[str]) -> List[Finding]:
    relative = display_path(path, target)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [
            finding(
                "package.non-utf8-text",
                "medium",
                "package",
                relative,
                1,
                "A text-like file is not valid UTF-8 and cannot be reviewed reliably.",
                "Convert the file to UTF-8 or remove it from the skill package.",
                skill_id,
            )
        ]
    findings: List[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append(
                    finding(
                        rule.rule_id,
                        rule.severity,
                        rule.category,
                        relative,
                        line_number,
                        rule.message,
                        rule.remediation,
                        skill_id,
                    )
                )
    return findings


def manifest_findings(path: Path, target: Path, skill_id: Optional[str]) -> List[Finding]:
    relative = display_path(path, target)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [
            finding(
                "metadata.invalid-manifest",
                "high",
                "metadata",
                relative,
                1,
                f"skill.json is not valid readable JSON: {exc}",
                "Fix the manifest before reviewing or installing the skill.",
                skill_id,
            )
        ]
    findings: List[Finding] = []
    for field in ("artifacts", "examples"):
        values = payload.get(field, [])
        if field == "examples" and isinstance(values, list):
            values = [item.get("path") for item in values if isinstance(item, dict)]
        if not isinstance(values, list):
            continue
        for value in values:
            if not isinstance(value, str):
                continue
            posix_path = PurePosixPath(value)
            windows_path = PureWindowsPath(value)
            if (
                posix_path.is_absolute()
                or windows_path.is_absolute()
                or ".." in posix_path.parts
                or ".." in windows_path.parts
            ):
                findings.append(
                    finding(
                        "metadata.path-escape",
                        "high",
                        "metadata",
                        relative,
                        1,
                        f"Manifest field {field} references a path outside the skill package.",
                        "Use a relative path contained by the skill directory.",
                        skill_id,
                    )
                )
    return findings


def scan_target(target: Path, fail_on: str = "high") -> Dict[str, Any]:
    target_label = target.as_posix() if not target.is_absolute() else (target.name or ".")
    target = target.expanduser().absolute()
    if not target.exists() and not target.is_symlink():
        raise FileNotFoundError(f"security scan target does not exist: {target}")

    findings: List[Finding] = []
    files_scanned = 0
    manifests: Dict[str, Dict[str, Any]] = {}
    for path in iter_files(target):
        relative = display_path(path, target)
        skill_id = skill_id_for(path, target)
        if path.is_symlink():
            findings.append(
                finding(
                    "package.symlink",
                    "high",
                    "package",
                    relative,
                    1,
                    "A symbolic link can escape the reviewed skill package.",
                    "Replace the link with a regular reviewed file inside the package.",
                    skill_id,
                )
            )
            continue
        files_scanned += 1
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        if size > MAX_FILE_BYTES:
            findings.append(
                finding(
                    "package.large-file",
                    "medium",
                    "package",
                    relative,
                    1,
                    f"File exceeds the {MAX_FILE_BYTES}-byte static review limit.",
                    "Keep skill packages small and move large data to a referenced release artifact.",
                    skill_id,
                )
            )
        suffix = path.suffix.lower()
        try:
            with path.open("rb") as handle:
                magic = handle.read(4)
        except OSError:
            magic = b""
        binary_magic = magic.startswith(b"\x7fELF") or magic.startswith(b"MZ") or magic in {
            b"\xca\xfe\xba\xbe",
            b"\xcf\xfa\xed\xfe",
            b"\xfe\xed\xfa\xcf",
        }
        if suffix in EXECUTABLE_SUFFIXES or binary_magic:
            findings.append(
                finding(
                    "package.executable-binary",
                    "high",
                    "package",
                    relative,
                    1,
                    "Executable or loadable binary content is not reviewable as source.",
                    "Remove the binary and document a verified external dependency instead.",
                    skill_id,
                )
            )
        if suffix in ARCHIVE_SUFFIXES:
            findings.append(
                finding(
                    "package.archive",
                    "high",
                    "package",
                    relative,
                    1,
                    "Archive content is hidden from the normal source review boundary.",
                    "Extract the archive, review its files, and commit readable source directly.",
                    skill_id,
                )
            )
        if path.name == "skill.json":
            manifest_results = manifest_findings(path, target, skill_id)
            findings.extend(manifest_results)
            try:
                manifests[skill_id or relative] = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        if suffix in TEXT_SUFFIXES:
            findings.extend(scan_text_file(path, target, skill_id))

    # Compare declared manifest risk against the strongest behavior finding for each skill.
    for skill_id, manifest in manifests.items():
        declared = manifest.get("risk_level")
        if declared not in {"low", "medium", "high"}:
            continue
        relevant = [item for item in findings if item.skill_id == skill_id]
        if not relevant:
            continue
        strongest = max(relevant, key=lambda item: SEVERITY_RANK[item.severity]).severity
        declared_rank = {"low": 0, "medium": 1, "high": 2}[declared]
        behavior_rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}[strongest]
        if behavior_rank > declared_rank:
            manifest_path = next(
                (item for item in iter_files(target) if item.name == "skill.json" and skill_id_for(item, target) == skill_id),
                target,
            )
            relative = display_path(manifest_path, target)
            severity = "high" if strongest in {"high", "critical"} else "medium"
            findings.append(
                finding(
                    "metadata.risk-underdeclared",
                    severity,
                    "metadata",
                    relative,
                    1,
                    f"Manifest risk_level={declared} is lower than detected {strongest} behavior.",
                    "Raise risk_level or remove/guard the behavior before review.",
                    skill_id,
                )
            )

    findings.sort(key=lambda item: (-SEVERITY_RANK[item.severity], item.path, item.line, item.rule_id))
    counts = {severity: 0 for severity in SEVERITIES}
    for item in findings:
        counts[item.severity] += 1
    blocking = [] if fail_on == "none" else [
        item for item in findings if SEVERITY_RANK[item.severity] >= SEVERITY_RANK[fail_on]
    ]
    verdict = "block" if blocking else ("review" if findings else "pass")
    return {
        "$schema": SCHEMA_URL,
        "schema_version": "0.1.0",
        "scanner": {"name": SCANNER_NAME, "version": SCANNER_VERSION},
        "target": target_label,
        "policy": {"fail_on": fail_on},
        "summary": {
            "verdict": verdict,
            "files_scanned": files_scanned,
            "finding_count": len(findings),
            "blocking_count": len(blocking),
            "severity_counts": counts,
        },
        "findings": [asdict(item) for item in findings],
    }


def sarif_report(report: Dict[str, Any]) -> Dict[str, Any]:
    rules_by_id = {rule.rule_id: rule for rule in RULES}
    results = []
    for item in report["findings"]:
        severity = item["severity"]
        results.append(
            {
                "ruleId": item["rule_id"],
                "level": "error" if severity in {"critical", "high"} else (
                    "warning" if severity == "medium" else "note"
                ),
                "message": {"text": item["message"]},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": item["path"]},
                            "region": {"startLine": item["line"]},
                        }
                    }
                ],
                "partialFingerprints": {"primaryLocationLineHash": item["fingerprint"]},
                "properties": {
                    "category": item["category"],
                    "severity": severity,
                    "skill_id": item.get("skill_id"),
                },
            }
        )
    descriptors = []
    seen = set()
    for item in report["findings"]:
        rule_id = item["rule_id"]
        if rule_id in seen:
            continue
        seen.add(rule_id)
        rule = rules_by_id.get(rule_id)
        descriptors.append(
            {
                "id": rule_id,
                "shortDescription": {"text": item["message"]},
                "help": {"text": item["remediation"]},
                "properties": {"category": item["category"], "severity": item["severity"]},
            }
        )
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": SCANNER_NAME,
                        "version": SCANNER_VERSION,
                        "informationUri": "https://github.com/hwang595/hpc-skill-hub",
                        "rules": descriptors,
                    }
                },
                "results": results,
            }
        ],
    }


def text_report(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"Skill security verdict: {summary['verdict'].upper()}",
        f"Target: {report['target']}",
        (
            f"Scanned {summary['files_scanned']} file(s); "
            f"{summary['finding_count']} finding(s), {summary['blocking_count']} blocking."
        ),
    ]
    for item in report["findings"]:
        skill = f" [{item['skill_id']}]" if item.get("skill_id") else ""
        lines.append(
            f"{item['severity'].upper()}: {item['path']}:{item['line']}: "
            f"{item['rule_id']}{skill}: {item['message']}"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan a community skill package for security risks")
    parser.add_argument("target", nargs="?", default=".", help="Skill file or directory to scan")
    parser.add_argument(
        "--format",
        choices=("text", "json", "sarif"),
        default="text",
        help="Output format",
    )
    parser.add_argument("--json", action="store_true", help="Alias for --format json")
    parser.add_argument(
        "--fail-on",
        choices=("none",) + SEVERITIES,
        default="high",
        help="Lowest severity that returns a failing exit code",
    )
    return parser


def run_cli(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    output_format = "json" if args.json else args.format
    try:
        report = scan_target(Path(args.target), fail_on=args.fail_on)
    except (FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    payload: Any = sarif_report(report) if output_format == "sarif" else report
    if output_format in {"json", "sarif"}:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(text_report(report))
    return 1 if report["summary"]["verdict"] == "block" else 0


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
