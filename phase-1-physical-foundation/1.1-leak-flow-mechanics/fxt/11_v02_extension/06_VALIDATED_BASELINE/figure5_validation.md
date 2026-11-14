# Gate 5 — Figure 5 validation

## Result: PASS, conditional conventional figure-level reproduction

The rotating blue points and error bars in Figure 5 were extracted from the
PDF vector paths. They were fit using only the paper's conventional effective
magnetic field of Eq. (1), ideal spin-echo toggling, and a fitted affine
readout mapping. No C2/H01 or extra decoherence term was used.

| Metric | Result |
|---|---:|
| Fitted effective AC field | 71.1 +/- 6.6 mG |
| Paper's reported effective AC field | 88 +/- 29 mG |
| Difference | -16.9 mG |
| Chi-squared / dof | 5.48 / 7 |
| Plain RMSE | 0.0461 normalized contrast |
| Weighted RMSE | 0.706 |

The fitted amplitude is within the paper's reported one-standard-error range.
The chi-squared is below the degrees of freedom, so the residuals do not show
an unresolved discrepancy at the resolution of the digitized plot.

## Boundary of this pass

This is **not** a parameter-free reconstruction. Rotation phase, readout
contrast, and readout offset were fitted because the paper does not tabulate
them. The grey stationary trace is not treated as raw numerical data; the PDF
does not give the carbon-13 bath model needed to predict it. The pass means
only that the supplied paper’s stated conventional explanation can reproduce
its plotted rotating signal within documented limits.

Saved metrics and residual plot: `outputs/validation/`.

