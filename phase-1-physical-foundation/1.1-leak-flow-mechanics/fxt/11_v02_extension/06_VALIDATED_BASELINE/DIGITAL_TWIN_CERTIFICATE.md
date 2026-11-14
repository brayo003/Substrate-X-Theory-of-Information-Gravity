# Digital Twin Certificate — limited conventional reproduction

## Certification decision

**CONDITIONALLY CERTIFIED for a Figure 4/5 conventional, digitized-data
reproduction.** This is not a certification of the complete laboratory
apparatus and not evidence for C2/H01.

## What has been validated

| Gate | Evidence | Result |
|---|---|---|
| 1 | supplied paper fully extracted; missing parameters listed | complete |
| 2 | explicit figure plan and digitization protocol | complete |
| 3 | conventional Eq. (1) echo forward model | complete |
| 4 | Figure 4A digitized Rabi rate: 3.742 +/- 0.380 MHz vs 3.6 +/- 0.2 MHz | pass, limited |
| 5 | Figure 5 Eq. (1) fit: 71.1 +/- 6.6 mG vs 88 +/- 29 mG | pass, limited |
| 6 | vector-PDF digitization and metadata | complete |
| 7 | local conventional parameter sensitivity output | complete |
| 8 | 500-trial conventional-null Monte Carlo, mean reduced chi2 0.969 | pass, model-scoped |
| 9 | deliberate removal of field projection / echo toggling strongly worsens fit | pass |

## Agreement metrics

- Figure 4A plain RMSE: 0.0104 normalized contrast.
- Figure 5 plain RMSE: 0.0461 normalized contrast; chi-squared/dof: 5.48/7.
- Incomplete Figure 5 models: no field projection chi-squared 82.44; no echo
  toggling chi-squared 77.04.

## Known limitations

1. The paper does not supply raw Figure 4/5 data. Metrics use points extracted
   from vector graphics.
2. The readout mapping, rotation phase, and Figure 5 contrast are fitted
   nuisance parameters, not predicted.
3. The stationary carbon-13 echo trace cannot be derived from the PDF alone.
4. The model uses an ideal two-level transition and instantaneous pulses; the
   paper does not publish enough pulse/microwave data for a full spin-1,
   time-resolved optical model.
5. This certificate applies only to the stated conventional field-projection
   signal in the plotted `tau < 60 us` regime.

## Explicit scope statement

This simulator reproduces the published conventional Figure 4/5 behaviour
within the documented uncertainty and modelling limits. It does **not** test,
support, reject, or contain C2, Substrate-X, H01, or any additional physical
interaction.

