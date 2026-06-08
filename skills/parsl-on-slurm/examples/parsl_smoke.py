from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path


def getenv_int(name: str, default: int) -> int:
    value = os.environ.get(name, str(default))
    try:
        return int(value)
    except ValueError as exc:
        raise SystemExit(f"{name} must be an integer, got {value!r}") from exc


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


run_parsl = os.environ.get("RUN_PARSL", "0") == "1"
account = os.environ["PARSL_ACCOUNT"]
partition = os.environ["PARSL_PARTITION"]
blocks = getenv_int("PARSL_BLOCKS", 1)
nodes_per_block = getenv_int("PARSL_NODES_PER_BLOCK", 1)
cores_per_node = getenv_int("PARSL_CORES_PER_NODE", 2)
max_workers_per_node = getenv_int("PARSL_MAX_WORKERS_PER_NODE", 2)
walltime = os.environ["PARSL_WALLTIME"]
run_dir = Path(os.environ["PARSL_RUN_DIR"])
output_dir = Path(os.environ["OUTPUT_DIR"])

run_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)

plan = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "driver_host": socket.gethostname(),
    "python": sys.executable,
    "run_parsl": run_parsl,
    "account": account,
    "partition": partition,
    "blocks": blocks,
    "nodes_per_block": nodes_per_block,
    "cores_per_node": cores_per_node,
    "max_workers_per_node": max_workers_per_node,
    "walltime": walltime,
    "run_dir": str(run_dir),
    "output_dir": str(output_dir),
}

plan_path = output_dir / "parsl-plan.json"
write_json(plan_path, plan)
print(f"Wrote: {plan_path}")

if not run_parsl:
    print("RUN_PARSL=0, dry-run complete. Set RUN_PARSL=1 to submit worker blocks.")
    raise SystemExit(0)

try:
    import parsl
    from parsl import python_app
    from parsl.config import Config
    from parsl.executors import HighThroughputExecutor
    from parsl.launchers import SrunLauncher
    from parsl.providers import SlurmProvider
except ImportError as exc:
    raise SystemExit(
        "Parsl is required for RUN_PARSL=1. Install dependencies from requirements.txt."
    ) from exc


@python_app
def square_with_host(value: int) -> dict[str, object]:
    import socket

    return {
        "input": value,
        "square": value * value,
        "host": socket.gethostname(),
    }


config = Config(
    run_dir=str(run_dir),
    executors=[
        HighThroughputExecutor(
            label="slurm_htex",
            max_workers_per_node=max_workers_per_node,
            provider=SlurmProvider(
                account=account,
                partition=partition,
                nodes_per_block=nodes_per_block,
                cores_per_node=cores_per_node,
                init_blocks=blocks,
                min_blocks=0,
                max_blocks=blocks,
                walltime=walltime,
                launcher=SrunLauncher(),
            ),
        )
    ],
)

parsl.load(config)
try:
    futures = [square_with_host(value) for value in range(8)]
    results = [future.result() for future in futures]
    report = {
        **plan,
        "results": results,
        "result_count": len(results),
    }
    result_path = output_dir / "parsl-result.json"
    write_json(result_path, report)
    print(f"Wrote: {result_path}")
finally:
    parsl.dfk().cleanup()
    parsl.clear()
