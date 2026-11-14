# Conventional rotating-NV reproduction

This folder implements Gates 1–12 of the requested reproduction protocol for
the supplied `../rota.pdf`. It is isolated from `05_h01_digital_twin` and
contains no C2/H01/substrate contribution.

Current status:

- Gate 1: complete paper extraction — complete.
- Gate 2: figure reproduction plan — complete.
- Gate 3: conventional forward model — complete.
- Gates 4–5: limited figure-level validation — passed against documented
  vector-digitized points.
- Gates 6–9: digitization, local sensitivity, null, and model-break analyses
  — complete.
- Gate 10: limited conventional digital-twin certificate issued.
- Gate 11: readiness review complete; no additional term has been injected.

Run the conventional Figure 5 forward model:

```bash
MPLCONFIGDIR=/tmp/mpl-nv python simulation.py
```

Output is saved in `outputs/published_forward_model/`. It is only a forward
model based on reported parameters; it is not evidence of agreement with the
paper until Gate 5 comparison is performed.
