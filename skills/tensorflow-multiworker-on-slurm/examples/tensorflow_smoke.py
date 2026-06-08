#!/usr/bin/env python3
"""Small TensorFlow distributed strategy smoke test for Slurm jobs."""

from __future__ import annotations

import json
import os
import socket
import sys
from typing import Iterable


def getenv_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def split_workers(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def configure_tf_config(workers: Iterable[str], task_index: int) -> None:
    worker_list = list(workers)
    if not worker_list or "TF_CONFIG" in os.environ:
        return
    os.environ["TF_CONFIG"] = json.dumps(
        {
            "cluster": {"worker": worker_list},
            "task": {"type": "worker", "index": task_index},
        }
    )


def main() -> int:
    workers = split_workers(os.environ.get("TF_WORKERS", ""))
    task_index = getenv_int("TF_TASK_INDEX", getenv_int("SLURM_PROCID", 0))
    configure_tf_config(workers, task_index)

    try:
        import tensorflow as tf
    except ImportError as exc:
        print(f"ERROR: TensorFlow import failed: {exc}", file=sys.stderr)
        return 2

    try:
        if len(workers) > 1:
            strategy = tf.distribute.MultiWorkerMirroredStrategy()
        else:
            strategy = tf.distribute.MirroredStrategy()
    except Exception as exc:
        print(f"ERROR: TensorFlow strategy initialization failed: {exc}", file=sys.stderr)
        return 3

    tf_config = os.environ.get("TF_CONFIG", "")
    physical_gpus = tf.config.list_physical_devices("GPU")
    logical_gpus = tf.config.list_logical_devices("GPU")
    worker_count = len(workers) if workers else 1

    print(
        "rank_report "
        f"host={socket.gethostname()} "
        f"task_index={task_index} worker_count={worker_count} "
        f"strategy={type(strategy).__name__} "
        f"replicas={strategy.num_replicas_in_sync} "
        f"physical_gpus={len(physical_gpus)} logical_gpus={len(logical_gpus)} "
        f"tf_version={tf.__version__} tf_config={tf_config}",
        flush=True,
    )

    try:
        with strategy.scope():
            per_replica = strategy.run(
                lambda: tf.constant(float(task_index + 1), dtype=tf.float32)
            )
            reduced = strategy.reduce(tf.distribute.ReduceOp.SUM, per_replica, axis=None)
            result = float(reduced.numpy())
    except Exception as exc:
        print(f"ERROR: TensorFlow tensor reduction failed: {exc}", file=sys.stderr)
        return 4

    if result <= 0.0:
        print(f"ERROR: unexpected reduction result={result}", file=sys.stderr)
        return 5

    print(
        f"task_index={task_index} reduction_result={result} status=ok",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
