# Gate 7 — parameter sensitivity

Run `MPLCONFIGDIR=/tmp/mpl-nv python gate_analysis.py` to generate the
one-at-a-time conventional sensitivity table and plot in
`outputs/gate_analysis/`.

Perturbations are deliberately local and stated in the JSON output: ±1% and
±10% multiplicative changes for field amplitude, contrast, `T2`, and rotation
frequency; phase changes of ±0.01π and ±0.1π; offset changes of ±0.001 and
±0.01 contrast. This is a numerical conditioning map, not an uncertainty
budget, because the paper does not report all parameter covariances.

