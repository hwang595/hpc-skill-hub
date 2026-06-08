#!/usr/bin/env python3
"""Small Hugging Face Accelerate smoke test for Slurm jobs."""

from __future__ import annotations

import os
import socket
import sys


def main() -> int:
    try:
        from accelerate import Accelerator
    except ImportError as exc:
        print(f"ERROR: Accelerate import failed: {exc}", file=sys.stderr)
        return 2

    try:
        import torch
    except ImportError as exc:
        print(f"ERROR: PyTorch import failed: {exc}", file=sys.stderr)
        return 3

    try:
        accelerator = Accelerator()
        rank = accelerator.process_index
        local_rank = accelerator.local_process_index
        world_size = accelerator.num_processes
        device = accelerator.device
    except Exception as exc:
        print(f"ERROR: Accelerate initialization failed: {exc}", file=sys.stderr)
        return 4

    slurm_rank = os.environ.get("SLURM_PROCID", "")
    machine_rank = os.environ.get("SLURM_NODEID", os.environ.get("SLURM_PROCID", ""))

    print(
        "rank_report "
        f"host={socket.gethostname()} "
        f"accelerate_rank={rank} local_rank={local_rank} world_size={world_size} "
        f"slurm_rank={slurm_rank} machine_rank={machine_rank} "
        f"device={device} cuda_available={torch.cuda.is_available()}",
        flush=True,
    )

    try:
        value = torch.tensor([float(rank + 1)], device=device)
        gathered = accelerator.gather(value)
        accelerator.wait_for_everyone()
    except Exception as exc:
        print(f"ERROR: Accelerate tensor collective failed: {exc}", file=sys.stderr)
        return 5

    if accelerator.is_main_process:
        observed = float(gathered.sum().item())
        expected = float(world_size * (world_size + 1) // 2)
        print(f"collective_sum={observed} expected={expected}", flush=True)
        if observed != expected:
            print(
                f"ERROR: collective mismatch observed={observed} expected={expected}",
                file=sys.stderr,
            )
            return 6

    accelerator.wait_for_everyone()
    print(f"rank={rank} status=ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
