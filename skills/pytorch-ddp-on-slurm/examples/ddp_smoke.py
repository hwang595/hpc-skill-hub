#!/usr/bin/env python3
"""Small PyTorch distributed smoke test for Slurm jobs."""

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
    try:
        import torch
        import torch.distributed as dist
    except ImportError as exc:
        print(f"ERROR: PyTorch import failed: {exc}", file=sys.stderr)
        return 2

    rank = getenv_int("SLURM_PROCID", getenv_int("RANK", 0))
    local_rank = getenv_int("SLURM_LOCALID", getenv_int("LOCAL_RANK", 0))
    world_size = getenv_int("SLURM_NTASKS", getenv_int("WORLD_SIZE", 1))

    cuda_available = torch.cuda.is_available()
    backend = "nccl" if cuda_available else "gloo"

    print(
        "rank_report "
        f"host={socket.gethostname()} "
        f"rank={rank} local_rank={local_rank} world_size={world_size} "
        f"torch={torch.__version__} cuda_available={cuda_available} backend={backend}",
        flush=True,
    )

    if cuda_available:
        device_count = torch.cuda.device_count()
        if device_count == 0:
            print("ERROR: CUDA is available but no devices are visible", file=sys.stderr)
            return 3
        torch.cuda.set_device(local_rank % device_count)
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")

    if world_size > 1:
        dist.init_process_group(backend=backend, rank=rank, world_size=world_size)

    value = torch.tensor([float(rank + 1)], device=device)
    if world_size > 1:
        dist.all_reduce(value, op=dist.ReduceOp.SUM)
        dist.barrier()

    expected = float(world_size * (world_size + 1) // 2)
    observed = float(value.item())

    if rank == 0:
        print(f"all_reduce_sum={observed} expected={expected}", flush=True)

    if observed != expected:
        print(
            f"ERROR: all-reduce mismatch rank={rank} observed={observed} expected={expected}",
            file=sys.stderr,
        )
        return 4

    if world_size > 1:
        dist.destroy_process_group()

    print(f"rank={rank} status=ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
