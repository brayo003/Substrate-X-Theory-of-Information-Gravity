# H01 — Controlled Residual Spectroscopy Search

## Hypothesis status

**Proposed v02 experimental hypothesis.** This does not assume an absolute
substrate current or claim to measure `g`.

## Question

For an externally controlled parameter `X`, is there a reproducible observable
signal (a qubit transition-frequency shift only if separately hypothesized,
or the frozen dephasing rate where applicable)

`Y(X)`

that cannot be accounted for by a preregistered conventional model of the
apparatus?

## Pre-registered null model

The conventional model must include, as relevant to the platform:

- electromagnetic field pickup and AC/DC Stark shifts;
- control-line phase/frequency drift and crosstalk;
- temperature and thermal-population drift;
- mechanical vibration, acceleration, strain, and rotation effects;
- magnetic-field variation;
- readout and fitting bias.

## Required measurement sequence

1. Choose and calibrate a physical control `X` in SI units.
2. Use spectroscopy for conventional-response calibration. For the frozen
   rotation claim, measure the dephasing rate separately as the primary
   observable; do not replace it with an un-derived coherent shift.
3. Record the conventional monitor channels above during every run.
4. Run matched sham/control sequences and randomize the order/blind the label
   where feasible.
5. Fit the conventional model on a training subset.
6. Test its locked prediction on held-out data.

## Decision rule

- If the held-out conventional model explains the frequency shifts within the
  preregistered uncertainty, H01 reports a **null result**. No substrate
  current has been detected.
- If a residual survives controls and replication, it is a **candidate new
  observable**, not yet a measurement of `J`. Only then may v02 propose a
  response law `J = F(X_residual)` and test it independently.

## Relation to g

Only after an absolute, independently calibrated `J` exists **and a v02
coherent-coupling hypothesis is stated** can spectroscopy
use

`Delta omega_q = 2 g J / hbar`

to estimate `g = hbar (d Delta omega_q / dJ) / 2`. Ramsey decay is reserved as
a held-out consequence, not a calibration input.
