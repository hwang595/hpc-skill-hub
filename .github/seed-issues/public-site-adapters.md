Site adapters let HPC centers publish public local policy without forking core
skills. A good first adapter can be small: public partition names, scheduler
type, module system, supported container runtime, storage tiers, and links to
public user documentation.

Good first contributions:

- A campus Slurm cluster adapter using only public documentation.
- A training cluster adapter for a workshop or course.
- A cloud HPC adapter that documents public scheduler and storage conventions.

Please do not include private hostnames, usernames, allocation names, security
procedures, internal project ids, private storage paths, or unpublished policy.

Start from:

```bash
python3 tools/hpc_skill.py scaffold site-adapter your-site-id --name "Your Site"
```

Then run:

```bash
python3 tools/hpc_skill.py validate
make check
```
