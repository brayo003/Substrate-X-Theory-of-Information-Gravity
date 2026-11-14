# H01 Digital Twin

This workspace tests whether a proposed rotation experiment could distinguish a
chosen injected signal from ordinary, rotation-correlated systematics. It does
not simulate a verified substrate field and cannot validate C2.

The core Ramsey evolution is calculated with QuTiP. The generated data include
magnetic, thermal, vibration, and readout-correlated monitor channels. The
analysis then compares a conventional monitor model with a monitor-plus-
quadratic-dephasing model on held-out rotation settings.

## Signal labels

- **Null:** no extra rotation-dependent dephasing.
- **Frozen-law-shaped injection:** `Gamma_extra = k_injected Omega^2`.
  This is an injected detectability benchmark, not evidence that C2 predicts
  the chosen coefficient.
- **Coherent injection:** `delta_omega = beta_injected Omega`. This is a v02
  exploratory signal, not a v01 prediction.
- **Adversarial systematic:** rotation-synchronous vibration omitted from a
  deliberately incomplete analysis model to measure false-positive risk.

## Run

```bash
MPLCONFIGDIR=/tmp/mpl-h01 python digital_twin.py
MPLCONFIGDIR=/tmp/mpl-h01 python digital_twin.py --config config/adversarial.json
```

Outputs are written under `outputs/<scenario>/`. Inspect the blinded summary
first; use `--unblind` only after deciding the analysis specification is final.
