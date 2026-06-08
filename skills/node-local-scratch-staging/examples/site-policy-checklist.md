# Node Local Scratch Site Policy Checklist

Review this list before using node-local temporary storage on a shared cluster.

- Which environment variable names the site-approved node-local directory?
- Is node-local storage available on every partition or only selected nodes?
- Is the capacity shared by all jobs on the node?
- Does the site purge node-local data at job exit, node reboot, or a fixed age?
- Are users allowed to run large metadata workloads from node-local storage?
- Should final outputs, checkpoints, and restart files always stage out before
  the job exits?
- Are there workload types that should stay on shared scratch, burst buffer, or
  project storage instead?
- Who should review cleanup behavior before a workflow scales beyond a smoke
  test?
