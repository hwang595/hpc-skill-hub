#!/usr/bin/env python3
"""Verify a built wheel from an isolated workspace and virtual environment."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
PILOT_FIXTURE = ROOT / "tests" / "fixtures" / "community-pilot" / "benign"


class InstalledSmokeError(RuntimeError):
    """Raised when an installed-distribution isolation check fails."""


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str],
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        cwd=str(cwd),
        env=dict(env),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise InstalledSmokeError(
            f"command failed ({result.returncode}): {' '.join(command)}\n{detail}"
        )
    return result


def _run_json(
    command: Sequence[str],
    *,
    cwd: Path,
    env: Mapping[str, str],
) -> Dict[str, Any]:
    result = _run(command, cwd=cwd, env=env)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise InstalledSmokeError(
            f"command did not return JSON: {' '.join(command)}"
        ) from exc
    if not isinstance(payload, dict):
        raise InstalledSmokeError("installed smoke command returned non-object JSON")
    return payload


def _outside(path: Path, root: Path) -> bool:
    try:
        return os.path.commonpath([str(path.resolve()), str(root.resolve())]) != str(
            root.resolve()
        )
    except ValueError:
        return True


def _isolated_environment() -> Dict[str, str]:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("HPC_SKILL_HUB_ROOT", None)
    env["PYTHONNOUSERSITE"] = "1"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    return env


def _python_path(venv_root: Path) -> Path:
    if os.name == "nt":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def _script_path(venv_root: Path, name: str) -> Path:
    if os.name == "nt":
        return venv_root / "Scripts" / f"{name}.exe"
    return venv_root / "bin" / name


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _module_probe(python: Path, workspace: Path, env: Mapping[str, str]) -> Dict[str, Any]:
    code = (
        "import importlib.metadata,json,pathlib,hpc_skill_hub;"
        "print(json.dumps({'distribution_version':importlib.metadata.version('hpc-skill-hub'),"
        "'module_version':hpc_skill_hub.__version__,"
        "'module_path':str(pathlib.Path(hpc_skill_hub.__file__).resolve())},sort_keys=True))"
    )
    return _run_json([str(python), "-c", code], cwd=workspace, env=env)


def _build_installed_context(
    python: Path,
    fixture: Path,
    output: Path,
    workspace: Path,
    env: Mapping[str, str],
) -> None:
    code = "\n".join(
        (
            "import json,sys",
            "from pathlib import Path",
            "from hpc_skill_hub.community_pilot import build_accepted_context_fixture",
            "bundle = build_accepted_context_fixture(Path(sys.argv[1]))",
            "Path(sys.argv[2]).write_text(json.dumps(bundle, indent=2, sort_keys=True) + '\\n', encoding='utf-8')",
        )
    )
    _run(
        [str(python), "-c", code, str(fixture), str(output)],
        cwd=workspace,
        env=env,
    )


def _configured_mcp_probe(
    python: Path,
    bundle: Path,
    workspace: Path,
    env: Mapping[str, str],
) -> Dict[str, Any]:
    code = "\n".join(
        (
            "import asyncio,json,sys",
            "from pathlib import Path",
            "from mcp.shared.memory import create_connected_server_and_client_session",
            "from pydantic import AnyUrl",
            "from hpc_skill_hub.mcp_server import create_server",
            "async def probe():",
            "    server = create_server([Path(sys.argv[1])])",
            "    async with create_connected_server_and_client_session(server, raise_exceptions=True) as session:",
            "        tools = await session.list_tools()",
            "        catalog_result = await session.call_tool('list_community_contexts', {})",
            "        catalog = catalog_result.structuredContent['result']",
            "        assert catalog['count'] == 1",
            "        assert 'files' not in catalog['contexts'][0]",
            "        uri = catalog['contexts'][0]['resource_uri']",
            "        resource = await session.read_resource(AnyUrl(uri))",
            "        raw = resource.contents[0].text",
            "        payload = json.loads(raw)",
            "        assert raw.index('\\\"provenance\\\"') < raw.index('\\\"files\\\"')",
            "        assert payload['provenance']['review']['status'] == 'review-complete'",
            "        assert payload['provenance']['maturity']['promotion'] == 'not-authorized'",
            "        print(json.dumps({'catalog_count':catalog['count'],'resource_uri':uri,'file_count':payload['content_manifest']['file_count'],'tool_count':len(tools.tools),'metadata_contains_files':False,'provenance_before_files':True},sort_keys=True))",
            "asyncio.run(probe())",
        )
    )
    return _run_json(
        [str(python), "-c", code, str(bundle)], cwd=workspace, env=env
    )


def verify_installed_wheel(wheel: Path, mode: str) -> Dict[str, Any]:
    wheel = wheel.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        raise InstalledSmokeError(f"wheel does not exist: {wheel}")
    if mode not in {"core", "mcp"}:
        raise InstalledSmokeError(f"unsupported smoke mode: {mode}")
    if not PILOT_FIXTURE.is_dir():
        raise InstalledSmokeError(f"pilot fixture is missing: {PILOT_FIXTURE}")

    with tempfile.TemporaryDirectory(prefix="hpc-skill-hub-installed-smoke-") as tmpdir:
        root = Path(tmpdir)
        workspace = root / "workspace"
        venv_root = root / "venv"
        workspace.mkdir()
        if not _outside(workspace, ROOT):
            raise InstalledSmokeError("isolated workspace is inside the checkout")
        fixture = workspace / "benign"
        shutil.copytree(PILOT_FIXTURE, fixture)

        venv.EnvBuilder(with_pip=True, clear=True).create(venv_root)
        python = _python_path(venv_root)
        hpc_skill = _script_path(venv_root, "hpc-skill")
        env = _isolated_environment()
        install_target = str(wheel) if mode == "core" else f"{wheel}[mcp]"
        install_command: List[str] = [
            str(python),
            "-m",
            "pip",
            "install",
        ]
        if mode == "core":
            install_command.extend(["--no-index", "--no-deps"])
        install_command.append(install_target)
        _run(install_command, cwd=workspace, env=env)

        probe = _module_probe(python, workspace, env)
        module_path = Path(probe["module_path"])
        if not _outside(module_path, ROOT):
            raise InstalledSmokeError("installed module resolved inside the source checkout")
        if probe["distribution_version"] != probe["module_version"]:
            raise InstalledSmokeError("installed distribution and module versions differ")

        doctor_command = [str(hpc_skill), "doctor", "--json"]
        if mode == "mcp":
            doctor_command.insert(-1, "--require-mcp")
        doctor = _run_json(doctor_command, cwd=workspace, env=env)
        if doctor.get("ok") is not True:
            raise InstalledSmokeError("installed doctor did not pass")
        health = _run_json([str(hpc_skill), "health", "--json"], cwd=workspace, env=env)
        intake = _run_json(
            [str(hpc_skill), "intake", str(fixture), "--json"],
            cwd=workspace,
            env=env,
        )
        if intake["summary"]["context_loading_allowed"] is not False:
            raise InstalledSmokeError("installed intake exposed unreviewed context")
        if intake["quarantine"]["execution_performed"] is not False:
            raise InstalledSmokeError("installed intake executed fixture content")

        bundle = workspace / "community-context.json"
        _build_installed_context(python, fixture, bundle, workspace, env)
        context = _run_json(
            [str(hpc_skill), "community-context", "check", str(bundle), "--json"],
            cwd=workspace,
            env=env,
        )
        if "files" in context.get("context", {}):
            raise InstalledSmokeError("community-context check returned instruction content")

        mcp_probe = None
        if mode == "mcp":
            mcp_check = next(
                check for check in doctor["checks"] if check["id"] == "mcp-protocol"
            )
            if mcp_check["details"]["community_context_count"] != 0:
                raise InstalledSmokeError("default MCP startup exposed community content")
            mcp_probe = _configured_mcp_probe(python, bundle, workspace, env)

        return {
            "schema_version": "0.1.0",
            "mode": mode,
            "ok": True,
            "wheel": {
                "filename": wheel.name,
                "sha256": _sha256(wheel),
                "distribution_version": probe["distribution_version"],
            },
            "isolation": {
                "workspace_outside_checkout": True,
                "pythonpath_removed": True,
                "module_outside_checkout": True,
                "usersite_disabled": True,
            },
            "checks": {
                "doctor_status": doctor["status"],
                "registry_skill_count": health["skill_count"],
                "intake_status": intake["summary"]["status"],
                "context_review_status": context["context"]["provenance"]["review"][
                    "status"
                ],
                "context_maturity_promotion": context["context"]["provenance"][
                    "maturity"
                ]["promotion"],
                "configured_mcp": mcp_probe,
            },
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify an HPC Skill Hub wheel outside the source checkout"
    )
    parser.add_argument("--wheel", type=Path, required=True, help="Built wheel to install")
    parser.add_argument(
        "--mode",
        choices=("core", "mcp"),
        default="core",
        help="Install core only or include the MCP extra",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    args = parser.parse_args()

    try:
        report = verify_installed_wheel(args.wheel, args.mode)
    except (InstalledSmokeError, KeyError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"Installed {args.mode} isolation passed for "
            f"{report['wheel']['filename']} ({report['wheel']['distribution_version']})."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
