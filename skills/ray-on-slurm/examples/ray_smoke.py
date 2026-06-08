from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path

import ray


@ray.remote
def describe_task(index: int) -> dict[str, object]:
    return {
        "index": index,
        "host": socket.gethostname(),
        "pid": os.getpid(),
    }


record_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "ray-record-local")
record_dir.mkdir(parents=True, exist_ok=True)

ray.init(address="auto")
try:
    resources = ray.cluster_resources()
    nodes = ray.nodes()
    futures = [describe_task.remote(i) for i in range(8)]
    results = ray.get(futures)
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ray_version": ray.__version__,
        "address": os.environ.get("RAY_ADDRESS", "auto"),
        "cluster_resources": resources,
        "node_count": len(nodes),
        "alive_node_count": sum(1 for node in nodes if node.get("Alive")),
        "results": results,
    }
    result_path = record_dir / "ray-result.json"
    result_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print("Ray resources:", resources, flush=True)
    print("Ray nodes:", len(nodes), flush=True)
    print(f"Wrote: {result_path}", flush=True)
finally:
    ray.shutdown()
