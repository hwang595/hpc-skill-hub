from __future__ import annotations

import csv
import os
import socket
import sys
from pathlib import Path

from mpi4py import MPI


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
host = socket.gethostname()
output_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "results")

if rank == 0:
    output_dir.mkdir(parents=True, exist_ok=True)

comm.Barrier()

mpi_version = ".".join(str(part) for part in MPI.Get_version())
library_version = MPI.Get_library_version().strip().replace("\n", " ")
rank_total = comm.allreduce(rank + 1, op=MPI.SUM)
rows = comm.gather(
    {
        "rank": rank,
        "size": size,
        "host": host,
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "mpi_version": mpi_version,
        "library_version": library_version,
    },
    root=0,
)

print(
    f"rank={rank} size={size} host={host} "
    f"rank_total={rank_total} mpi_version={mpi_version}",
    flush=True,
)

if rank == 0:
    csv_path = output_dir / "mpi4py-ranks.csv"
    summary_path = output_dir / "mpi4py-summary.txt"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "size",
                "host",
                "python",
                "executable",
                "mpi_version",
                "library_version",
            ],
        )
        writer.writeheader()
        writer.writerows(rows or [])

    unique_hosts = sorted({row["host"] for row in rows or []})
    with summary_path.open("w", encoding="utf-8") as handle:
        handle.write("mpi4py demo complete\n")
        handle.write(f"world_size: {size}\n")
        handle.write(f"rank_total: {rank_total}\n")
        handle.write(f"hosts: {','.join(unique_hosts)}\n")
        handle.write(f"slurm_job_id: {os.environ.get('SLURM_JOB_ID', 'local')}\n")

    print(f"Wrote: {csv_path}", flush=True)
    print(f"Wrote: {summary_path}", flush=True)

comm.Barrier()
