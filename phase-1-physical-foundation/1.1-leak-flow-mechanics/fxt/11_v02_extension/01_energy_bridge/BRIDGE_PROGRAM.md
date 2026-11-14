# Workstream 1 — Energy/Information Bridge

## Frozen obstruction

The v01 interaction is

`H_int = g J(x_q,t) sigma_z`, with `[g] = J m^2 s / info`.

The transport variables use `{m, s, info}` while the qubit Hamiltonian uses
joules. The v01 rescaling

`(s, J, s0, g) -> (a s, a J, a s0, g/a)`

leaves the transport equations, `H_int`, `Gamma_phi`, and `k_rot` invariant.
Thus v01 fixes neither the field normalization nor `g` separately.

## Proposed extension E1 (not a v01 result)

Introduce a positive bridge quantity

`eta = energy / information`  with  `[eta] = J / info`.

E1 is not yet an equation. Its physical operational definition must be chosen
before it can be used: for example, an experimentally calibrated energy change
per independently counted substrate-information quantum. Merely writing
`E = eta I` is a new postulate, not a derivation.

## What would count as progress

There are only two valid routes:

1. **Derivation route:** derive `eta` from additional v02 axioms whose physical
   origin is independently defended. The derivation must eliminate every free
   dimensionless coefficient.
2. **Calibration route:** measure `eta` with an observable unrelated to qubit
   Ramsey decay, including a traceable energy calibration and uncertainty.

If neither occurs, `eta` and `g` remain phenomenological constants and v02 has
not produced a parameter-free prediction.

## Required falsifier

If two independent calibrations of `eta` disagree beyond their preregistered
combined uncertainty, E1 in its operational form fails.
