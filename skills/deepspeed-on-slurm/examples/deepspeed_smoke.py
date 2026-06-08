#!/usr/bin/env python3
"""Tiny DeepSpeed smoke test for Slurm allocations."""

from __future__ import annotations

import argparse
import os
import sys


def getenv_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return int(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a tiny DeepSpeed smoke test")
    parser.add_argument("--deepspeed_config", required=True)
    args = parser.parse_args()

    try:
        import deepspeed
        import torch
        import torch.distributed as dist
    except ImportError as exc:
        print(f"ERROR: import failed: {exc}", file=sys.stderr)
        return 2

    rank = getenv_int("SLURM_PROCID", getenv_int("RANK", 0))
    local_rank = getenv_int("SLURM_LOCALID", getenv_int("LOCAL_RANK", 0))
    world_size = getenv_int("SLURM_NTASKS", getenv_int("WORLD_SIZE", 1))

    cuda_available = torch.cuda.is_available()
    if cuda_available:
        device_count = torch.cuda.device_count()
        torch.cuda.set_device(local_rank % max(device_count, 1))
        backend = "nccl"
    else:
        backend = "gloo"

    if world_size > 1 and not dist.is_initialized():
        deepspeed.init_distributed(dist_backend=backend)

    model = torch.nn.Linear(4, 2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    engine, optimizer, _, _ = deepspeed.initialize(
        model=model,
        optimizer=optimizer,
        config=args.deepspeed_config,
    )

    device = engine.device
    batch = torch.ones((2, 4), device=device)
    target = torch.zeros((2, 2), device=device)
    output = engine(batch)
    loss = torch.nn.functional.mse_loss(output, target)
    engine.backward(loss)
    engine.step()

    print(
        "deepspeed_smoke "
        f"rank={rank} local_rank={local_rank} world_size={world_size} "
        f"backend={backend} loss={float(loss.detach().cpu()):.6f}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
