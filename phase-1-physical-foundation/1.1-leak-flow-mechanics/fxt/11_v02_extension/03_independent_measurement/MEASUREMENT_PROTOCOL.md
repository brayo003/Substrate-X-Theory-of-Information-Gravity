# Workstream 3 — Independent Measurement of the Bridge

## What cannot work

Fitting Ramsey decay versus detuning/rotation and then solving for `g` is not
an independent measurement. It estimates the already-degenerate product
`g^2 s0^2 r_q^2 tau`.

## Minimum viable experiment

An experiment must control or measure, independently:

| Quantity | Needed evidence |
|---|---|
| Substrate-current amplitude `J` or `s0` | calibrated observable with an absolute normalization |
| Energy shift `delta E` | qubit spectroscopy or another traceable energy measurement |
| Coupling | estimate `g = delta E / J` before any Ramsey fit |
| Background noise | control condition with the proposed substrate modulation absent |
| Competing explanation | electromagnetic, thermal, vibration, and control-noise monitors |

The direct signature is a coherent energy shift proportional to a known,
externally controlled `J`, followed by a blinded prediction of the decoherence
rate using the independently estimated coupling. A rate-only result is not
sufficient.

## IBM hardware decision

Do not spend the IBM allocation on this until an operational measurement of
`J` exists. Cloud qubits can measure Ramsey and `T1`, but they do not provide
control of the proposed substrate current or its absolute normalization.

## Success criterion

Calibrate `g` from spectroscopy/control data, lock it, and predict a separate
Ramsey data set with no fitted amplitude. Compare the locked v02 prediction to
a standard noise model using held-out likelihood or Bayes factor.
