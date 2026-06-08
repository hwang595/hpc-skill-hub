# GPU Memory Signals

- `CUDA out of memory`: the framework reached visible device memory limits.
- `CUBLAS_STATUS_ALLOC_FAILED` or `CUDNN_STATUS_ALLOC_FAILED`: often a downstream allocator symptom.
- `HIP out of memory` or ROCm allocation errors: check AMD GPU visibility and framework build.
- `Killed` without a CUDA traceback: often host memory, cgroup, or scheduler memory enforcement.
- Data-loader worker failures: may be host memory, pinned memory, file descriptor pressure, or dataset staging.
- Smaller than expected device memory: check GPU model, MIG partitions, container visibility, or Slurm GPU request.
