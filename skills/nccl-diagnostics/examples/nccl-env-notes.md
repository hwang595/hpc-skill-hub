# NCCL Environment Notes

Start with a small evidence capture before changing NCCL settings.

- `NCCL_DEBUG=INFO` records initialization and runtime warnings.
- `NCCL_DEBUG_SUBSYS=INIT,ENV,GRAPH,NET` focuses logs on setup, topology, and network selection.
- `NCCL_SOCKET_IFNAME` should only be set when the site documents the correct network interface.
- `NCCL_IB_DISABLE` can be useful for comparison tests, but should not become a permanent workaround without facility review.
- Keep the exact Slurm allocation, module/container environment, and log file with the incident.
