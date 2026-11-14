# Rotation-versus-Mechanical Discrimination Design

The central H01 comparison is not `no signal` versus `Omega^2`. Both a
hypothetical rotation-linked contribution and ordinary mechanical coupling can
be quadratic in rotation rate.

## Design lever: alter mechanical transfer without altering rotation schedule

Run the identical signed rotation schedule under at least three independently
characterized mounting/isolation configurations. In the digital twin these are
called `soft`, `reference`, and `damped`, with different mechanical transfer
gains. The injected benchmark signal is held fixed across configurations.

| Hypothesis | Expected configuration dependence |
|---|---|
| Mechanical artifact | scales with the measured mechanical transfer gain |
| Injected rotation-linked benchmark | fixed when geometry and rotation rate are fixed |

This is only a testable experimental distinction if the mount change has been
shown not to alter qubit geometry, temperature, electromagnetic environment, or
control calibration. Those invariances are measured controls, not assumptions.

## Analysis comparison

- `M_mech`: intercept + measured vibration monitor.
- `M_mech+quad`: intercept + measured vibration monitor + independent
  `Omega^2` coefficient shared across mount configurations.

The second model is useful only if it improves *held-out* prediction and its
coefficient is stable under monitor calibration uncertainty. A preference for
`M_mech+quad` is not a substrate discovery.
