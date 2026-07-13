#!/usr/bin/env python3
"""Summarize an existing GPU sanity log without contacting the scheduler."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SIGNALS = {
    "scheduler allocation": [
        r"SLURM_JOB_ID=\S+",
        r"SLURM_JOB_GPUS=\S+",
        r"CUDA_VISIBLE_DEVICES=\S+",
        r"ROCR_VISIBLE_DEVICES=\S+",
    ],
    "vendor visibility": [
        r"NVIDIA-SMI",
        r"GPU\[\d+\]",
        r"rocm-smi",
    ],
    "framework visibility": [
        r"cuda_available:\s*True",
        r"cuda_device_count:\s*[1-9]\d*",
    ],
    "failure clues": [
        r"command not found",
        r"torch_check_error:",
        r"cuda_available:\s*False",
        r"No devices were found",
        r"Driver/library version mismatch",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review an existing gpu-sanity.sbatch output log."
    )
    parser.add_argument("log_file", type=Path, help="Path to the saved Slurm output log")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.log_file.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"error: cannot read {args.log_file}: {exc}")
        return 2

    print(f"log: {args.log_file}")
    for label, patterns in SIGNALS.items():
        matches = [pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)]
        status = "present" if matches else "not observed"
        print(f"{label}: {status}")

    print("review: correlate scheduler, vendor, and framework evidence before assigning a cause")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
