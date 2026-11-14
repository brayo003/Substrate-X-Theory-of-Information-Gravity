# Gate 2 — figure reproduction plan

## Target selection

Figure 4 is the control-platform validation: it checks that the implementation
can express resonant pulse control and the stated 3.6(2) MHz Rabi rate.

Figure 5 is the primary conventional benchmark: it checks the spin-echo
response to Equation (1), without any new physics.

## Figure 4

**Reproducible in part.** An ideal resonant two-level pulse model predicts the
reported Rabi frequency and the oscillation period. Its exact normalized
fluorescence offset, visibility, phase, and error bars are not parameter-free,
because the microwave/readout calibration and raw points are absent.

Validation target after digitization: fitted oscillation frequency agrees with
the published `3.6(2) MHz`; compare normalized shape after allowing only a
documented affine readout mapping.

## Figure 5

**Reproducible in part, conditional on digitized data.** The published
effective field, pulse timings, and rotation frequency define a conventional
spin-echo phase integral. A two-level unitary simulation can forward-predict
the echo fringe shape from the authors' reported 88 mG amplitude, subject to an
unknown phase and readout mapping. It cannot independently predict the
stationary carbon-13 background or error bars from the PDF alone.

Validation target after digitization:

- fringe time scale / node locations;
- phase relative to an explicitly fitted or published `phi0`;
- rotating curve RMSE and residuals;
- fitted effective-field amplitude compared to `88 +/- 29 mG`;
- a separate report stating that the stationary trace is descriptive unless a
  bath model is sourced.

## Figures not selected for initial validation

- Figure 1 is schematic, not a numerical validation object.
- Figure 2 requires optical point-spread, motor wobble, and timing-jitter data
  not supplied in sufficient detail.
- Figure 3 requires time-resolved raw count traces and a rate-equation optical
  pumping model with missing parameters.

## Digitization plan

No raw Figure 4/5 data are supplied in the paper. Before numerical agreement
metrics, digitize Figure 4 and Figure 5 from `rota.pdf`, preserving only point
coordinates and error bars visible in the plotted figures. Store:

```
digitized/figure4_points.csv
digitized/figure5_rotating_points.csv
digitized/figure5_stationary_trace.csv
digitized/metadata.md
```

`metadata.md` must record image resolution, pixel-to-axis calibration, operator
or tool, and an estimated digitization uncertainty. Digitized values are a
comparison proxy, not original experimental data.

## Gate criteria

Gate 3 begins after the conventional model is implemented with these stated
limits. Gate 4 and Gate 5 are not certified as passes merely because a curve
looks similar: they require saved digitized input, fit parameters, RMSE,
residual plots, and a comparison to the paper's stated uncertainties.

