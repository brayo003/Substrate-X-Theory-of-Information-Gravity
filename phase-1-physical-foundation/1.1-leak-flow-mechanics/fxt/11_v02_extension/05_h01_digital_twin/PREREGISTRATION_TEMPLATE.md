# H01-R Preregistration Template

Complete this document before collecting hardware data. Do not alter the
analysis model after unblinding without recording a new protocol version.

## Scientific question

Can a rotation-controlled platform show a residual rotation-dependent Ramsey
dephasing contribution after a locked conventional-systematics model is tested
on held-out rotation settings?

## Hypotheses

- **Null:** monitored conventional effects explain the data within uncertainty.
- **Frozen-law-shaped benchmark:** an additional term has the form
  `Gamma_extra = k Omega^2`. This is a conditional v01-shaped signal family;
  `k` is not predicted by v01.
- **Exploratory coherent signal:** any `delta_omega = beta Omega` term is a v02
  hypothesis and is reported separately.

## Required commitments

- platform and rotation-axis geometry;
- rotation values, directions, run order, shots, Ramsey times, and exclusions;
- monitor calibration and transfer functions;
- conventional model, priors, held-out split, and decision threshold;
- signal-injection/blinding procedure;
- data/code version hashes and full noise budget.

## Pass/fail language

A conventional-model failure is an unexplained residual, not a substrate
detection. A positive claim requires independent replication and an expanded
conventional-model audit.
