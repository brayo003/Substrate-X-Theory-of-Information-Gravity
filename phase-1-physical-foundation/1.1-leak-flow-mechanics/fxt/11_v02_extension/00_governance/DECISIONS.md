# v02 Decisions Register

## D-001 — v02 primary target: residual/discovery route

**Decision:** v02 proceeds first on **Path B**: a controlled residual-search
program. Its question is whether a carefully controlled external parameter
`X` (initially a rotation/modulation candidate) produces a qubit spectroscopic
energy shift that remains after conventional electromagnetic, thermal,
vibrational/strain, and control-line mechanisms are quantitatively modelled.

**Reason:** A direct identification of substrate `J` with a known field can
calibrate an effective coupling, but cannot establish a C2-specific physical
degree of freedom. A residual is a necessary condition before claiming a novel
substrate-current detector.

**Status:** Proposed v02 research program; not a prediction of v01.

## D-002 — known-field route is a positive control only

**Decision:** A calibrated microwave/optical/mechanical field may be used to
validate spectroscopy, metrology, and analysis pipelines, but success only
recovers known physics. It is not evidence for a C2 bridge and must never be
reported as such.

## D-003 — no operational definition of J yet

**Decision:** `J` is not considered absolutely measured until a detector has a
specified response law, SI-traceable calibration, independently known geometry,
and a response coefficient that is not fitted from the same qubit data.

## D-004 — proposals explicitly parked

The following are not adopted as v02 assumptions:

- `s0 = ell_P^-3`: unsupported by v01, introduces a Planck-scale assignment,
  and does not constitute a calibration of the information field.
- PRW momentum/force transfer: requires a new momentum/energy postulate.
- Optical susceptibility `chi_s`: requires a new electromagnetic coupling;
  an interferometer calibrated only through its own response cannot by itself
  establish absolute substrate flux.
- Detectable PRW particles: requires a new interaction and detector efficiency
  law absent from v01.

These may return only as individually stated hypotheses with a derivation,
parameter inventory, standard competitor, and falsifier.

## D-005 — H01 primary control: physical rotation, platform-gated

**Decision:** The primary theory-linked control for H01 is physical rotation
`omega_rot`, because it is the externally varied quantity in the frozen
variance relation. H01 is not to be run on remote/fixed-cryostat IBM hardware:
that platform does not permit controlled rotation of the device.

**Platform gate:** an implementation requires a qubit/sensor platform that can
be rotated while maintaining spectroscopy and a complete conventional-noise
monitoring system. Until such a platform is available, v02 work remains design,
simulation, and positive-control validation.

## D-006 — dynamic mass proximity rejected for H01

**Decision:** A modulated nearby mass is not adopted as an H01 control.
v01 supplies no equation mapping mass density, gravitational potential, or a
mass gradient to substrate current `J`. A response to such a mass would test a
new gravitational/matter coupling, not the frozen rotation prediction.

Claims that a dense external mass has "zero" conventional background are also
not acceptable without measurement: rotating/chopping masses can transmit
vibration, alter magnetic/electrical surroundings, and produce ordinary
systematic effects.

## D-007 — no frozen coherent-shift prediction from rotation

**Decision:** v01's stated quantitative rotation result is a *dephasing-rate*
law, `Gamma_phi = k_rot omega_rot^2`, derived from a current variance. It does
not by itself supply a separately validated nonzero mean current or a coherent
spectroscopic law `Delta omega_q proportional to omega_rot`.

Such a coherent shift may later be introduced as a named v02 hypothesis, but
cannot be presented as a v01 prediction. Likewise, defining
`J_eff = s0 r_q omega_rot` after observing a residual is not an absolute
calibration because `s0` remains unnormalised.
