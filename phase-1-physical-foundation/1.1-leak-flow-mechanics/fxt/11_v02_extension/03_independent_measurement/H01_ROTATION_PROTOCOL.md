# H01-R — Rotation-Controlled Residual Search

## Chosen control

`X = omega_rot`, physical rotation of a rotation-compatible qubit/sensor
platform. This is selected because it is the only currently frozen external
control directly appearing in the v01 rotation/dephasing chain.

## Scope

The frozen observable is the dephasing-rate dependence

`Gamma_phi(omega_rot) = k_rot omega_rot^2`

under its stated assumptions. This protocol does **not** assume a coherent
frequency-shift law. Any such law would require a separate v02 hypothesis.

## Preconditions

- A platform that can actually rotate during the measurement. Remote/fixed
  cryostat hardware is not sufficient.
- Rotation axis and sensor position specified in the laboratory frame.
- Rotation-rate calibration with uncertainty and reversible direction control.
- Independent monitoring of acceleration/vibration, magnetic field,
  temperature, strain, microwave leakage, timing, and electronics.

## Positive controls before rotation

Use known magnetic and, where appropriate, controlled strain responses to
validate spectroscopy, sensor monitors, time synchronization, and the
conventional-systematics model. These controls are not tests of C2.

## Rotation measurement

1. Pre-register rotation-rate values, durations, random order, shot count,
   fitting model, and exclusion rules.
2. Include both rotation directions and stationary runs with motor/electronics
   active but mechanically decoupled where feasible.
3. Fit a conventional artifact model using monitor channels on training data.
4. Lock that model before evaluating held-out rotation data.
5. Compare a constant dephasing model, a conventional artifact model, and the
   frozen quadratic form with equal transparency about fitted parameters.

## Interpretation

- A null result bounds any rotation-correlated dephasing contribution in the
  tested regime; it does not establish `J`.
- A quadratic residual only motivates replication and a stronger conventional
  noise audit. It does not by itself identify a substrate field, fix `g`, or
  calibrate `s0`.
- An absolute `J` calibration remains a later v02 requirement.
