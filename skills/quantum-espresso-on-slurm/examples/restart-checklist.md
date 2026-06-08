# Quantum ESPRESSO Restart Checklist

- Confirm the same `prefix`, `outdir`, and `wfcdir` are available to all ranks.
- Confirm the prior run stopped cleanly before relying on restart files.
- Keep the generated input file with the restart record.
- Review whether the follow-on calculation needs the same MPI layout.
- Copy node-local `wfcdir` files back to durable storage if your site uses local
  scratch.
- Set `restart_mode = 'restart'` only for a true continuation of a compatible
  interrupted run.
