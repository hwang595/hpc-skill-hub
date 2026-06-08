from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path

from dask.distributed import Client
from dask_jobqueue import SLURMCluster


def getenv_int(name: str, default: int) -> int:
    value = os.environ.get(name, str(default))
    try:
        return int(value)
    except ValueError as exc:
        raise SystemExit(f"{name} must be an integer, got {value!r}") from exc


def square_with_host(value: int) -> dict[str, object]:
    return {
        "input": value,
        "square": value * value,
        "host": socket.gethostname(),
    }


run_dask = os.environ.get("RUN_DASK", "0") == "1"
jobs = getenv_int("DASK_JOBS", 1)
cores = getenv_int("DASK_CORES", 2)
processes = getenv_int("DASK_PROCESSES", 1)
account = os.environ["DASK_ACCOUNT"]
queue = os.environ["DASK_QUEUE"]
memory = os.environ["DASK_MEMORY"]
walltime = os.environ["DASK_WALLTIME"]
log_dir = Path(os.environ["DASK_LOG_DIR"])
local_dir = Path(os.environ["DASK_LOCAL_DIR"])
output_dir = Path(os.environ["OUTPUT_DIR"])

log_dir.mkdir(parents=True, exist_ok=True)
local_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)

cluster = SLURMCluster(
    account=account,
    queue=queue,
    cores=cores,
    processes=processes,
    memory=memory,
    walltime=walltime,
    local_directory=str(local_dir),
    log_directory=str(log_dir),
    job_extra_directives=[
        "--output={}/dask-worker-%j.out".format(log_dir),
    ],
)

job_script_path = output_dir / "dask-worker-job.sh"
job_script = cluster.job_script()
job_script_path.write_text(job_script, encoding="utf-8")

print("Python executable:", sys.executable)
print("Driver host:", socket.gethostname())
print("Dask worker job script:")
print(job_script)
print(f"Wrote: {job_script_path}")

if not run_dask:
    print("RUN_DASK=0, dry-run complete. Set RUN_DASK=1 to submit worker jobs.")
    cluster.close()
    raise SystemExit(0)

client = Client(cluster)
try:
    cluster.scale(jobs=jobs)
    expected_workers = max(jobs * processes, 1)
    print("Scheduler address:", client.scheduler.address)
    print("Dashboard link:", getattr(client, "dashboard_link", "unavailable"))
    client.wait_for_workers(expected_workers, timeout="120s")
    print("Workers connected:", len(client.scheduler_info()["workers"]))

    futures = client.map(square_with_host, range(8), pure=False)
    results = client.gather(futures)
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scheduler_address": client.scheduler.address,
        "workers": len(client.scheduler_info()["workers"]),
        "jobs_requested": jobs,
        "cores_per_job": cores,
        "processes_per_job": processes,
        "results": results,
    }
    result_path = output_dir / "dask-result.json"
    result_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote: {result_path}")
finally:
    client.close()
    cluster.close()
