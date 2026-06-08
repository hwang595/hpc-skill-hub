# Pending Limit Reason Reference

Use this page to map common Slurm pending reasons to the evidence this skill
collects.

| Reason family | Likely meaning | Evidence to compare |
| --- | --- | --- |
| `AssocGrp*Limit` | The user's association or parent account has reached an aggregate limit. | `squeue-job.txt`, `sacctmgr-associations.txt`, `sshare-user.txt` |
| `AssocMax*Limit` | The job request exceeds a per-job association limit. | `scontrol-job.txt`, `sacctmgr-associations.txt` |
| `AssociationJobLimit` | The association has reached its maximum running job count. | `squeue-user-pending.txt`, `sacctmgr-associations.txt` |
| `AssociationResourceLimit` | The association has reached a configured resource limit. | `sacctmgr-associations.txt`, `sshare-user.txt` |
| `AssociationTimeLimit` | The association has reached a time-based limit. | `sacctmgr-associations.txt`, `sshare-user.txt` |
| `QOSGrp*Limit` | The selected QOS has reached an aggregate limit. | `squeue-job.txt`, `sacctmgr-qos.txt` |
| `QOSMax*Limit` | The job request exceeds a per-job QOS limit. | `scontrol-job.txt`, `sacctmgr-qos.txt` |
| `QOSJobLimit` | The selected QOS has reached a maximum running job count. | `squeue-job.txt`, `sacctmgr-qos.txt` |
| `QOSResourceLimit` | The selected QOS has reached a configured resource limit. | `sacctmgr-qos.txt`, `sshare-user.txt` |
| `InvalidAccount` | The requested account is not valid for the user, partition, or cluster. | `scontrol-job.txt`, `sacctmgr-associations.txt` |
| `InvalidQOS` | The requested QOS is not valid for the user, account, partition, or cluster. | `scontrol-job.txt`, `sacctmgr-associations.txt`, `sacctmgr-qos.txt` |
| `Priority` | The job is eligible but lower priority than other work. | `sprio-job.txt` or `sprio-user.txt`, `sshare-user.txt` |

Reason strings are hints, not complete policy explanations. Use site public
documentation or support channels before changing accounts, QOS values, or
resource requests for production work.
