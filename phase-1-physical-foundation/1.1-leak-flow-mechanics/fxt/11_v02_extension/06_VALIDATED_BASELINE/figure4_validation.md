# Gate 4 — Figure 4 validation

## Result: PASS, limited to the digitized frequency check

The Figure 4A vector plot was digitized reproducibly (see `digitized/`). A
weighted sinusoidal Rabi fit gives:

| Metric | Result |
|---|---:|
| Digitized fit frequency | 3.742 +/- 0.380 MHz |
| Paper's reported frequency | 3.6 +/- 0.2 MHz |
| Difference | 0.142 MHz |
| Plain RMSE | 0.0104 normalized contrast |
| Weighted RMSE | 0.356 |

The difference is smaller than the combined reported/digitization-fit
uncertainty (about 0.43 MHz). This passes the appropriate limited criterion:
the conventional resonant-pulse model reproduces the published Rabi time scale.

## What is not validated

The paper does not provide the raw trace, microwave amplitude/detuning,
normalization formula, or a full pulse calibration. The fitted offset,
amplitude, and phase are therefore descriptive nuisance parameters, not
independent predictions. Figure 4B has not been separately digitized, so it is
not included in the pass statement.

Saved metrics and residual plot: `outputs/validation/`.

