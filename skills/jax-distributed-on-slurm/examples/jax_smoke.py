#!/usr/bin/env python3
"""Small JAX distributed smoke test for Slurm jobs."""

from __future__ import annotations

import os
import socket
import sys


def getenv_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return int(value)


def main() -> int:
    rank = getenv_int("SLURM_PROCID", getenv_int("JAX_PROCESS_ID", 0))
    local_rank = getenv_int("SLURM_LOCALID", 0)
    world_size = getenv_int("SLURM_NTASKS", getenv_int("JAX_NUM_PROCESSES", 1))
    coordinator_address = os.environ.get("JAX_COORDINATOR_ADDRESS")

    try:
        import jax
        import jax.numpy as jnp
    except ImportError as exc:
        print(f"ERROR: JAX import failed: {exc}", file=sys.stderr)
        return 2

    if world_size > 1:
        if not coordinator_address:
            print(
                "ERROR: JAX_COORDINATOR_ADDRESS is required for multi-process runs",
                file=sys.stderr,
            )
            return 3
        try:
            jax.distributed.initialize(
                coordinator_address=coordinator_address,
                num_processes=world_size,
                process_id=rank,
            )
        except Exception as exc:
            print(f"ERROR: JAX distributed initialize failed: {exc}", file=sys.stderr)
            return 4

    try:
        backend = jax.default_backend()
        devices = jax.local_devices()
        process_index = jax.process_index()
        process_count = jax.process_count()
    except Exception as exc:
        print(f"ERROR: JAX device query failed: {exc}", file=sys.stderr)
        return 5

    print(
        "rank_report "
        f"host={socket.gethostname()} "
        f"rank={rank} local_rank={local_rank} world_size={world_size} "
        f"jax_process_index={process_index} jax_process_count={process_count} "
        f"jax={jax.__version__} backend={backend} local_devices={len(devices)}",
        flush=True,
    )

    try:
        values = jnp.arange(8, dtype=jnp.float32) + float(rank)
        result = jnp.sum(values)
        result.block_until_ready()
        observed = float(result)
    except Exception as exc:
        print(f"ERROR: JAX smoke computation failed: {exc}", file=sys.stderr)
        return 6

    expected = 28.0 + (8.0 * float(rank))
    if observed != expected:
        print(
            f"ERROR: smoke mismatch rank={rank} observed={observed} expected={expected}",
            file=sys.stderr,
        )
        return 7

    if world_size > 1:
        try:
            from jax.experimental import multihost_utils

            multihost_utils.sync_global_devices("jax-slurm-smoke")
        except Exception as exc:
            print(f"ERROR: JAX multi-host sync failed: {exc}", file=sys.stderr)
            return 8

    print(f"rank={rank} status=ok smoke_sum={observed}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
