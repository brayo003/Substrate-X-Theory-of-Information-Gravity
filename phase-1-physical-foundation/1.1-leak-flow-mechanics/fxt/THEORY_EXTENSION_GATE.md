# THEORY_EXTENSION_GATE.md
## SXC-IGC/C2 — Theory Extension Frozen Gate

**Date:** 2026-08-22
**Based on:** THEORY_EXTENSION_SEARCH.md, PREDICTION_LADDER.md,
  DISCRIMINATOR_RECONSTRUCTION.md, SUBSTRATE_CANDIDATE_AUDIT.md,
  EXPERIMENTAL_TARGET_REDESIGN.md, FINAL_THEORY_PREDICTIVITY_AUDIT.md

---

## THEORY STATUS: T2 — STRUCTURALLY UNDERDETERMINED

C2 remains structurally underdetermined. Neither Extension A nor Extension B
produces a genuine discriminator against all physically plausible conventional
mechanisms.

Extension A (c = v_s via A-FPUT1 + C5): produces specific numerical predictions
but makes C2 physically equivalent to a conventional 2D acoustic phonon bath.
All predictions are reproduced by the phonon null model.

Extension B (c ≪ v_s): no physically credible substrate satisfying C2/C5 was found.
The TLS persistent walk is the most promising direction but requires a new theory.

---

## PREDICTIVITY STATUS: ZERO UNCONDITIONAL

No prediction passes all four criteria (derived, constrained, not conventional,
measurable) unconditionally.

Two weak survivors:
1. Causal wavefront: discriminates C2 from diffusion only — not from phonon bath.
2. P3 anomalous c: discriminates only if c_measured ≪ v_s — not predictable from theory.

---

## GAP-7 STATUS: FUNDAMENTAL WITHIN EXISTING C2

All 25 derivation routes tested. C5 closure gives c = v_s conditional on
A-FPUT1 (FPUT substrate assumption) — but this makes C2 equivalent to conventional
phonon physics. The gap is closed numerically under Extension A but the
discriminating content is lost.

---

## STRONGEST SURVIVING PREDICTION

P3 self-consistency: c = ξ_c/(2τ_B) = constant across conditions.

Status: consistency check, not forward prediction. Discriminating only if
c_measured is anomalous. Theory does not predict c.

---

## STRONGEST CONVENTIONAL NULL

2D acoustic phonon bath with telegrapher (not diffusion) propagation dynamics.
Under Extension A, C2 is THIS model. All C2 predictions under Extension A
are reproduced by this null.

---

## WHETHER THE PREDICTION IS GENUINELY DISCRIMINATING

NO — under Extension A.
CONDITIONAL — under the current underdetermined theory (if c ≪ v_s when measured).

The prediction is not genuinely discriminating in the sense required for
an empirical test of the SXC-IGC ontology.

---

## REQUIRED EXPERIMENTAL OBSERVABLE

**Best measurement target:** Causal propagation speed c = r/t_onset, measured
from the onset time of spatial decoherence correlations vs. qubit separation.

This test:
- Bypasses the K₀/power-law shape degeneracy
- Directly measures the substrate propagation speed
- Distinguishes telegrapher (causal front) from diffusion (no front)
- Is technically feasible on Brisbane-class hardware

**Condition for authorization:** The theory must first predict c. It does not.

---

## WHETHER HARDWARE IS NOW JUSTIFIED

**NO.**

The RESCUE_GATE remains frozen. The theory has not produced a parameter-free
prediction of c. Running the causal onset experiment without a prior prediction
is a parameter fit, not a theory test.

---

## DECISION TREE OUTCOME

**Outcome B** (Extension A): C2 can become predictive but predictions remain
conventionally equivalent.

**Outcome E** (Extension B): No physically credible extension was found.

Combined: **Outcome B/E** — the theory produces correct conventional phonon
phenomenology, not a genuinely discriminating claim about SXC-IGC ontology.

---

## REQUIRED NEXT STEPS BEFORE RE-OPENING

Exactly one of the following must be accomplished and documented:

**Step T1 (weak, leads to Outcome B):**
Formally adopt A-FPUT1 as a C2 axiom. Measure τ_B on an Eagle-scale chip
(needs τ_B ~ 1.2 µs; current Brisbane gives τ_B ~ 5 µs). Verify ξ_c = 2v_s·τ_B.
This tests telegrapher vs. diffusion phonon propagation — a legitimate physics
question, but does not test the SXC-IGC substrate ontology distinctively.

**Step T2 (strong, leads toward Outcome A/D):**
Develop a physical model for a persistent random walk substrate with c ≪ v_s.
TLS-based persistent hopping is the most plausible candidate. This requires:
- Demonstrating that TLS in amorphous SiO₂ exhibit directional persistence
- Computing the effective PRW speed from TLS density and hop dynamics
- Verifying C5 closure for the resulting coarse-grained field
- Predicting c and τ_B from TLS material parameters

Until Step T2 is complete, no hardware work is justified beyond what
Step T1 requires.

---

## FROZEN GATE STATEMENT

The SXC-IGC/C2 theory has not crossed from T2 (underdetermined) toward
a genuinely predictive theory as of this audit.

Extension A produces correct but conventionally equivalent predictions.
Extension B found no physically credible mechanism.

The theory remains scientifically interesting as a mathematical framework
for causal substrate dynamics. Its empirical program is paused.

The experiment identified (causal onset measurement) is the correct design
IF the theory provides a pre-measurement prediction for c. It does not yet.

**HARDWARE AUTHORIZED: NO**

*Gate frozen: 2026-08-22*
*Not revisable without documented completion of Step T1 or Step T2 above.*
